import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as rds from 'aws-cdk-lib/aws-rds';
import * as elasticache from 'aws-cdk-lib/aws-elasticache';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

interface ComputeLayerProps {
  competitorTable: dynamodb.Table;
  adDataTable: dynamodb.Table;
  analysisTable: dynamodb.Table;
  predictionTable: dynamodb.Table;
  gapAnalysisTable: dynamodb.Table;
  conversationTable: dynamodb.Table;
  reportTable: dynamodb.Table;
  adCreativesBucket: s3.Bucket;
}

export class ComputeLayerStack extends Construct {
  public readonly dataIngestionFunction: lambda.Function;
  public readonly aiAnalysisFunction: lambda.Function;
  public readonly predictionsFunction: lambda.Function;
  public readonly gapAnalysisFunction: lambda.Function;
  public readonly scoutChatbotFunction: lambda.Function;
  public readonly competitorsApiFunction: lambda.Function;
  public readonly reportFunction: lambda.Function;

  constructor(scope: Construct, id: string, props: ComputeLayerProps) {
    super(scope, id);

    // Common Lambda environment variables
    const commonEnv = {
      COMPETITOR_TABLE: props.competitorTable.tableName,
      AD_DATA_TABLE: props.adDataTable.tableName,
      ANALYSIS_TABLE: props.analysisTable.tableName,
      PREDICTION_TABLE: props.predictionTable.tableName,
      GAP_ANALYSIS_TABLE: props.gapAnalysisTable.tableName,
      CONVERSATION_TABLE: props.conversationTable.tableName,
      REPORT_TABLE: props.reportTable.tableName,
      AD_CREATIVES_BUCKET: props.adCreativesBucket.bucketName,
      BEDROCK_MODEL_ID: 'anthropic.claude-3-sonnet-20240229-v1:0',
      BEDROCK_REGION: cdk.Stack.of(this).region,
    };

    // SQS Queue for processing pipeline
    const processingQueue = new sqs.Queue(this, 'ProcessingQueue', {
      visibilityTimeout: cdk.Duration.seconds(300),
      retentionPeriod: cdk.Duration.days(7),
      deadLetterQueue: {
        queue: new sqs.Queue(this, 'ProcessingDLQ', {
          retentionPeriod: cdk.Duration.days(14),
        }),
        maxReceiveCount: 3,
      },
    });

    // Data Ingestion Function (Meta Ads Library, Google Trends)
    this.dataIngestionFunction = new lambda.Function(this, 'DataIngestionFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'data_ingestion.handler.main',
      code: lambda.Code.fromAsset('../backend', {
        exclude: ['venv', 'venv/**', '__pycache__', '**/__pycache__', '*.pyc', '.pytest_cache', 'tests'],
      }),
      timeout: cdk.Duration.minutes(5),
      memorySize: 512,
      environment: {
        ...commonEnv,
        PROCESSING_QUEUE_URL: processingQueue.queueUrl,
      },
    });

    // Grant permissions
    props.competitorTable.grantReadWriteData(this.dataIngestionFunction);
    props.adDataTable.grantWriteData(this.dataIngestionFunction);
    props.adCreativesBucket.grantReadWrite(this.dataIngestionFunction);
    processingQueue.grantSendMessages(this.dataIngestionFunction);

    // Schedule data ingestion every 15 minutes
    const ingestionRule = new events.Rule(this, 'IngestionSchedule', {
      schedule: events.Schedule.rate(cdk.Duration.minutes(15)),
      description: 'Trigger data ingestion every 15 minutes',
    });
    ingestionRule.addTarget(new targets.LambdaFunction(this.dataIngestionFunction));

    // AI Analysis Function (Bedrock integration)
    this.aiAnalysisFunction = new lambda.Function(this, 'AIAnalysisFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'ai_analysis.handler.main',
      code: lambda.Code.fromAsset('../backend', {
        exclude: ['venv', 'venv/**', '__pycache__', '**/__pycache__', '*.pyc', '.pytest_cache', 'tests'],
      }),
      timeout: cdk.Duration.minutes(2),
      memorySize: 1024,
      environment: commonEnv,
    });

    // Grant Bedrock access
    this.aiAnalysisFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['bedrock:InvokeModel'],
        resources: [`arn:aws:bedrock:${cdk.Stack.of(this).region}::foundation-model/*`],
      })
    );

    props.adDataTable.grantReadData(this.aiAnalysisFunction);
    props.analysisTable.grantWriteData(this.aiAnalysisFunction);
    props.adCreativesBucket.grantRead(this.aiAnalysisFunction);

    // Campaign Predictions Function
    this.predictionsFunction = new lambda.Function(this, 'PredictionsFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'predictions.handler.main',
      code: lambda.Code.fromAsset('../backend', {
        exclude: ['venv', 'venv/**', '__pycache__', '**/__pycache__', '*.pyc', '.pytest_cache', 'tests'],
      }),
      timeout: cdk.Duration.seconds(30),
      memorySize: 1024,
      environment: commonEnv,
    });

    this.predictionsFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['bedrock:InvokeModel'],
        resources: [`arn:aws:bedrock:${cdk.Stack.of(this).region}::foundation-model/*`],
      })
    );

    props.adDataTable.grantReadData(this.predictionsFunction);
    props.analysisTable.grantReadData(this.predictionsFunction);
    props.predictionTable.grantReadWriteData(this.predictionsFunction);

    // Gap Analysis Function
    this.gapAnalysisFunction = new lambda.Function(this, 'GapAnalysisFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'gap_analysis.handler.main',
      code: lambda.Code.fromAsset('../backend', {
        exclude: ['venv', 'venv/**', '__pycache__', '**/__pycache__', '*.pyc', '.pytest_cache', 'tests'],
      }),
      timeout: cdk.Duration.minutes(1),
      memorySize: 1024,
      environment: commonEnv,
    });

    this.gapAnalysisFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['bedrock:InvokeModel'],
        resources: [`arn:aws:bedrock:${cdk.Stack.of(this).region}::foundation-model/*`],
      })
    );

    props.analysisTable.grantReadData(this.gapAnalysisFunction);
    props.competitorTable.grantReadData(this.gapAnalysisFunction);
    props.gapAnalysisTable.grantReadWriteData(this.gapAnalysisFunction);

    // Scout Chatbot Function
    this.scoutChatbotFunction = new lambda.Function(this, 'ScoutChatbotFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'scout_chatbot.handler.main',
      code: lambda.Code.fromAsset('../backend', {
        exclude: ['venv', 'venv/**', '__pycache__', '**/__pycache__', '*.pyc', '.pytest_cache', 'tests'],
      }),
      timeout: cdk.Duration.seconds(60),
      memorySize: 1024,
      environment: commonEnv,
    });

    this.scoutChatbotFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['bedrock:InvokeModel'],
        resources: [`arn:aws:bedrock:${cdk.Stack.of(this).region}::foundation-model/*`],
      })
    );

    // Grant read access to all data tables
    props.competitorTable.grantReadData(this.scoutChatbotFunction);
    props.adDataTable.grantReadData(this.scoutChatbotFunction);
    props.analysisTable.grantReadData(this.scoutChatbotFunction);
    props.predictionTable.grantReadData(this.scoutChatbotFunction);
    props.gapAnalysisTable.grantReadData(this.scoutChatbotFunction);
    props.conversationTable.grantReadWriteData(this.scoutChatbotFunction);

    // Competitors API Function
    this.competitorsApiFunction = new lambda.Function(this, 'CompetitorsApiFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'api.competitors_handler.main',
      code: lambda.Code.fromAsset('../backend', {
        exclude: ['venv', 'venv/**', '__pycache__', '**/__pycache__', '*.pyc', '.pytest_cache', 'tests'],
      }),
      timeout: cdk.Duration.seconds(10),
      memorySize: 256,
      environment: commonEnv,
    });

    props.competitorTable.grantReadData(this.competitorsApiFunction);
    props.adDataTable.grantReadData(this.competitorsApiFunction);

    // Report Generation Function
    this.reportFunction = new lambda.Function(this, 'ReportFunction', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'reports.handler.main',
      code: lambda.Code.fromAsset('../backend', {
        exclude: ['venv', 'venv/**', '__pycache__', '**/__pycache__', '*.pyc', '.pytest_cache', 'tests'],
      }),
      timeout: cdk.Duration.seconds(60),
      memorySize: 1024,
      environment: commonEnv,
    });

    this.reportFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['bedrock:InvokeModel'],
        resources: [`arn:aws:bedrock:${cdk.Stack.of(this).region}::foundation-model/*`],
      })
    );

    // Grant read access to all data tables
    props.competitorTable.grantReadData(this.reportFunction);
    props.adDataTable.grantReadData(this.reportFunction);
    props.predictionTable.grantReadData(this.reportFunction);
    props.gapAnalysisTable.grantReadData(this.reportFunction);
    props.reportTable.grantReadWriteData(this.reportFunction);

    // Dashboard API Function (not needed - using service handlers directly)
    // Commenting out for MVP - API Gateway will call service handlers directly
  }
}
