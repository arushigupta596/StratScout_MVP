import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as elasticache from 'aws-cdk-lib/aws-elasticache';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import { Construct } from 'constructs';

export class DataLayerStack extends Construct {
  public readonly competitorTable: dynamodb.Table;
  public readonly adDataTable: dynamodb.Table;
  public readonly analysisTable: dynamodb.Table;
  public readonly predictionTable: dynamodb.Table;
  public readonly gapAnalysisTable: dynamodb.Table;
  public readonly conversationTable: dynamodb.Table;
  public readonly adCreativesBucket: s3.Bucket;
  public readonly database: rds.DatabaseCluster;
  public readonly redisCluster: elasticache.CfnCacheCluster;
  public readonly vpc: ec2.Vpc;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    // VPC for Aurora and Redis
    this.vpc = new ec2.Vpc(this, 'StratScoutVpc', {
      maxAzs: 2,
      natGateways: 1,
      subnetConfiguration: [
        {
          cidrMask: 24,
          name: 'Public',
          subnetType: ec2.SubnetType.PUBLIC,
        },
        {
          cidrMask: 24,
          name: 'Private',
          subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
        },
        {
          cidrMask: 28,
          name: 'Isolated',
          subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
        },
      ],
    });

    // DynamoDB Tables

    // Competitor profiles and metadata
    this.competitorTable = new dynamodb.Table(this, 'CompetitorTable', {
      partitionKey: { name: 'competitorId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For MVP - change to RETAIN for production
      pointInTimeRecovery: true,
    });

    // Ad data from Meta Ads Library
    this.adDataTable = new dynamodb.Table(this, 'AdDataTable', {
      partitionKey: { name: 'adId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'scrapedAt', type: dynamodb.AttributeType.NUMBER },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      timeToLiveAttribute: 'ttl', // Auto-cleanup old data
    });

    // GSI for querying by competitor
    this.adDataTable.addGlobalSecondaryIndex({
      indexName: 'CompetitorIndex',
      partitionKey: { name: 'competitorId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'scrapedAt', type: dynamodb.AttributeType.NUMBER },
    });

    // AI analysis results
    this.analysisTable = new dynamodb.Table(this, 'AnalysisTable', {
      partitionKey: { name: 'analysisId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'createdAt', type: dynamodb.AttributeType.NUMBER },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    this.analysisTable.addGlobalSecondaryIndex({
      indexName: 'CompetitorAnalysisIndex',
      partitionKey: { name: 'competitorId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'createdAt', type: dynamodb.AttributeType.NUMBER },
    });

    // Campaign predictions
    this.predictionTable = new dynamodb.Table(this, 'PredictionTable', {
      partitionKey: { name: 'predictionId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'createdAt', type: dynamodb.AttributeType.NUMBER },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    this.predictionTable.addGlobalSecondaryIndex({
      indexName: 'CampaignPredictionIndex',
      partitionKey: { name: 'campaignId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'createdAt', type: dynamodb.AttributeType.NUMBER },
    });

    // Gap analysis results
    this.gapAnalysisTable = new dynamodb.Table(this, 'GapAnalysisTable', {
      partitionKey: { name: 'gapAnalysisId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'createdAt', type: dynamodb.AttributeType.NUMBER },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Scout conversation history
    this.conversationTable = new dynamodb.Table(this, 'ConversationTable', {
      partitionKey: { name: 'sessionId', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      timeToLiveAttribute: 'ttl', // Auto-cleanup old conversations
    });

    // S3 Bucket for ad creatives and media
    this.adCreativesBucket = new s3.Bucket(this, 'AdCreativesBucket', {
      versioned: false,
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For MVP
      autoDeleteObjects: true, // For MVP
      lifecycleRules: [
        {
          id: 'DeleteOldCreatives',
          expiration: cdk.Duration.days(90), // Keep creatives for 90 days
          enabled: true,
        },
      ],
      cors: [
        {
          allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.PUT],
          allowedOrigins: ['*'], // Restrict in production
          allowedHeaders: ['*'],
        },
      ],
    });

    // Aurora Serverless v2 PostgreSQL for analytics
    const dbSecret = new secretsmanager.Secret(this, 'DBSecret', {
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ username: 'stratscout_admin' }),
        generateStringKey: 'password',
        excludePunctuation: true,
        includeSpace: false,
      },
    });

    const dbSecurityGroup = new ec2.SecurityGroup(this, 'DBSecurityGroup', {
      vpc: this.vpc,
      description: 'Security group for Aurora Serverless',
      allowAllOutbound: true,
    });

    this.database = new rds.DatabaseCluster(this, 'AnalyticsDB', {
      engine: rds.DatabaseClusterEngine.auroraPostgres({
        version: rds.AuroraPostgresEngineVersion.VER_15_4,
      }),
      credentials: rds.Credentials.fromSecret(dbSecret),
      writer: rds.ClusterInstance.serverlessV2('writer', {
        scaleWithWriter: true,
      }),
      serverlessV2MinCapacity: 0.5,
      serverlessV2MaxCapacity: 2,
      vpc: this.vpc,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
      },
      securityGroups: [dbSecurityGroup],
      defaultDatabaseName: 'stratscout',
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For MVP
    });

    // ElastiCache Redis for caching
    const redisSubnetGroup = new elasticache.CfnSubnetGroup(this, 'RedisSubnetGroup', {
      description: 'Subnet group for Redis',
      subnetIds: this.vpc.privateSubnets.map(subnet => subnet.subnetId),
    });

    const redisSecurityGroup = new ec2.SecurityGroup(this, 'RedisSecurityGroup', {
      vpc: this.vpc,
      description: 'Security group for Redis',
      allowAllOutbound: true,
    });

    redisSecurityGroup.addIngressRule(
      ec2.Peer.ipv4(this.vpc.vpcCidrBlock),
      ec2.Port.tcp(6379),
      'Allow Redis access from VPC'
    );

    this.redisCluster = new elasticache.CfnCacheCluster(this, 'RedisCluster', {
      cacheNodeType: 'cache.t4g.micro',
      engine: 'redis',
      numCacheNodes: 1,
      cacheSubnetGroupName: redisSubnetGroup.ref,
      vpcSecurityGroupIds: [redisSecurityGroup.securityGroupId],
    });

    // Outputs
    new cdk.CfnOutput(this, 'CompetitorTableName', {
      value: this.competitorTable.tableName,
    });

    new cdk.CfnOutput(this, 'AdDataTableName', {
      value: this.adDataTable.tableName,
    });

    new cdk.CfnOutput(this, 'AdCreativesBucketName', {
      value: this.adCreativesBucket.bucketName,
    });

    new cdk.CfnOutput(this, 'DatabaseEndpoint', {
      value: this.database.clusterEndpoint.hostname,
    });

    new cdk.CfnOutput(this, 'DatabaseSecretArn', {
      value: dbSecret.secretArn,
    });
  }
}
