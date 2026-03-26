import * as cdk from 'aws-cdk-lib';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class DataLayerStack extends Construct {
  public readonly competitorTable: dynamodb.Table;
  public readonly adDataTable: dynamodb.Table;
  public readonly analysisTable: dynamodb.Table;
  public readonly predictionTable: dynamodb.Table;
  public readonly gapAnalysisTable: dynamodb.Table;
  public readonly conversationTable: dynamodb.Table;
  public readonly adCreativesBucket: s3.Bucket;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    // DynamoDB Tables (on-demand billing for cost optimization)
    
    // Competitors Table
    this.competitorTable = new dynamodb.Table(this, 'CompetitorTable', {
      tableName: 'StratScout-Competitors',
      partitionKey: { name: 'competitorId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For MVP - change to RETAIN for production
      pointInTimeRecovery: false, // Disable for cost savings
    });

    // Ad Data Table
    this.adDataTable = new dynamodb.Table(this, 'AdDataTable', {
      tableName: 'StratScout-Ads',
      partitionKey: { name: 'ad_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      pointInTimeRecovery: false,
      timeToLiveAttribute: 'ttl', // Auto-delete old data
    });

    // Add GSI for competitor queries
    this.adDataTable.addGlobalSecondaryIndex({
      indexName: 'CompetitorIndex',
      partitionKey: { name: 'competitor_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
    });

    // Analysis Table
    this.analysisTable = new dynamodb.Table(this, 'AnalysisTable', {
      tableName: 'StratScout-Analysis',
      partitionKey: { name: 'analysis_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      pointInTimeRecovery: false,
    });

    this.analysisTable.addGlobalSecondaryIndex({
      indexName: 'CompetitorAnalysisIndex',
      partitionKey: { name: 'competitor_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
    });

    // Prediction Table
    this.predictionTable = new dynamodb.Table(this, 'PredictionTable', {
      tableName: 'StratScout-Predictions',
      partitionKey: { name: 'prediction_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      pointInTimeRecovery: false,
    });

    // Gap Analysis Table
    this.gapAnalysisTable = new dynamodb.Table(this, 'GapAnalysisTable', {
      tableName: 'StratScout-GapAnalysis',
      partitionKey: { name: 'gap_analysis_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      pointInTimeRecovery: false,
    });

    // Conversation Table (for Scout chatbot)
    this.conversationTable = new dynamodb.Table(this, 'ConversationTable', {
      tableName: 'StratScout-Conversations',
      partitionKey: { name: 'conversation_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      pointInTimeRecovery: false,
    });

    this.conversationTable.addGlobalSecondaryIndex({
      indexName: 'UserConversationIndex',
      partitionKey: { name: 'user_id', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'timestamp', type: dynamodb.AttributeType.STRING },
    });

    // S3 Bucket for ad creatives
    this.adCreativesBucket = new s3.Bucket(this, 'AdCreativesBucket', {
      bucketName: `stratscout-creatives-${cdk.Stack.of(this).account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      lifecycleRules: [
        {
          expiration: cdk.Duration.days(90), // Delete after 90 days
          transitions: [
            {
              storageClass: s3.StorageClass.INFREQUENT_ACCESS,
              transitionAfter: cdk.Duration.days(30),
            },
          ],
        },
      ],
    });
  }
}
