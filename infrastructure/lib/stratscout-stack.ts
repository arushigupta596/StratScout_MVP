import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DataLayerStack } from './data-layer-stack';
import { ComputeLayerStack } from './compute-layer-stack';
import { ApiLayerStack } from './api-layer-stack';

export class StratScoutStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Layer 1 & 2: Data Layer (DynamoDB, Aurora, S3, Redis)
    const dataLayer = new DataLayerStack(this, 'DataLayer');

    // Layer 3-5: Compute Layer (Lambda functions for all services)
    const computeLayer = new ComputeLayerStack(this, 'ComputeLayer', {
      competitorTable: dataLayer.competitorTable,
      adDataTable: dataLayer.adDataTable,
      analysisTable: dataLayer.analysisTable,
      predictionTable: dataLayer.predictionTable,
      gapAnalysisTable: dataLayer.gapAnalysisTable,
      conversationTable: dataLayer.conversationTable,
      reportTable: dataLayer.reportTable,
      adCreativesBucket: dataLayer.adCreativesBucket,
    });

    // Layer 6: API Layer (API Gateway, Cognito, CloudFront)
    const apiLayer = new ApiLayerStack(this, 'ApiLayer', {
      dataIngestionFunction: computeLayer.dataIngestionFunction,
      aiAnalysisFunction: computeLayer.aiAnalysisFunction,
      predictionsFunction: computeLayer.predictionsFunction,
      gapAnalysisFunction: computeLayer.gapAnalysisFunction,
      scoutChatbotFunction: computeLayer.scoutChatbotFunction,
      competitorsApiFunction: computeLayer.competitorsApiFunction,
      reportFunction: computeLayer.reportFunction,
    });

    // Outputs
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: apiLayer.api.url,
      description: 'API Gateway endpoint URL',
    });

    new cdk.CfnOutput(this, 'UserPoolId', {
      value: apiLayer.userPool.userPoolId,
      description: 'Cognito User Pool ID',
    });

    new cdk.CfnOutput(this, 'UserPoolClientId', {
      value: apiLayer.userPoolClient.userPoolClientId,
      description: 'Cognito User Pool Client ID',
    });

    new cdk.CfnOutput(this, 'FrontendUrl', {
      value: apiLayer.distribution.distributionDomainName,
      description: 'CloudFront distribution URL',
    });
  }
}
