import * as cdk from 'aws-cdk-lib';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import { Construct } from 'constructs';

interface ApiLayerProps {
  dataIngestionFunction: lambda.Function;
  aiAnalysisFunction: lambda.Function;
  predictionsFunction: lambda.Function;
  gapAnalysisFunction: lambda.Function;
  scoutChatbotFunction: lambda.Function;
  competitorsApiFunction: lambda.Function;
  reportFunction: lambda.Function;
}

export class ApiLayerStack extends Construct {
  public readonly api: apigateway.RestApi;
  public readonly userPool: cognito.UserPool;
  public readonly userPoolClient: cognito.UserPoolClient;
  public readonly distribution: cloudfront.Distribution;

  constructor(scope: Construct, id: string, props: ApiLayerProps) {
    super(scope, id);

    // Cognito User Pool for authentication
    this.userPool = new cognito.UserPool(this, 'UserPool', {
      userPoolName: 'stratscout-users',
      selfSignUpEnabled: true,
      signInAliases: {
        email: true,
      },
      autoVerify: {
        email: true,
      },
      standardAttributes: {
        email: {
          required: true,
          mutable: true,
        },
        fullname: {
          required: true,
          mutable: true,
        },
      },
      passwordPolicy: {
        minLength: 8,
        requireLowercase: true,
        requireUppercase: true,
        requireDigits: true,
        requireSymbols: false,
      },
      accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For MVP
    });

    this.userPoolClient = this.userPool.addClient('WebClient', {
      authFlows: {
        userPassword: true,
        userSrp: true,
      },
      oAuth: {
        flows: {
          authorizationCodeGrant: true,
        },
        scopes: [cognito.OAuthScope.EMAIL, cognito.OAuthScope.OPENID, cognito.OAuthScope.PROFILE],
      },
    });

    // API Gateway with Cognito authorizer
    const authorizer = new apigateway.CognitoUserPoolsAuthorizer(this, 'ApiAuthorizer', {
      cognitoUserPools: [this.userPool],
    });

    this.api = new apigateway.RestApi(this, 'StratScoutApi', {
      restApiName: 'StratScout API',
      description: 'StratScout Competitive Intelligence Platform API',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS, // Restrict in production
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: [
          'Content-Type',
          'X-Amz-Date',
          'Authorization',
          'X-Api-Key',
          'X-Amz-Security-Token',
        ],
      },
      deployOptions: {
        stageName: 'prod',
        throttlingRateLimit: 100,
        throttlingBurstLimit: 200,
        // Disable logging to avoid CloudWatch Logs role requirement
        loggingLevel: apigateway.MethodLoggingLevel.OFF,
        dataTraceEnabled: false,
      },
    });

    // API Resources and Methods

    // Competitors endpoints (use dedicated API function)
    const competitors = this.api.root.addResource('competitors');
    competitors.addMethod(
      'GET',
      new apigateway.LambdaIntegration(props.competitorsApiFunction),
      {
        authorizer,
        authorizationType: apigateway.AuthorizationType.COGNITO,
      }
    );

    const competitor = competitors.addResource('{competitorId}');
    competitor.addMethod(
      'GET',
      new apigateway.LambdaIntegration(props.competitorsApiFunction),
      {
        authorizer,
        authorizationType: apigateway.AuthorizationType.COGNITO,
      }
    );

    // Analysis endpoints
    const analysis = this.api.root.addResource('analysis');
    analysis.addMethod(
      'GET',
      new apigateway.LambdaIntegration(props.aiAnalysisFunction),
      {
        authorizer,
        authorizationType: apigateway.AuthorizationType.COGNITO,
      }
    );

    // Predictions endpoints
    const predictions = this.api.root.addResource('predictions');
    predictions.addMethod(
      'GET',
      new apigateway.LambdaIntegration(props.predictionsFunction),
      {
        authorizer,
        authorizationType: apigateway.AuthorizationType.COGNITO,
      }
    );

    predictions.addMethod(
      'POST',
      new apigateway.LambdaIntegration(props.predictionsFunction),
      {
        authorizer,
        authorizationType: apigateway.AuthorizationType.COGNITO,
      }
    );

    // Gap Analysis endpoints
    const gaps = this.api.root.addResource('gaps');
    gaps.addMethod(
      'GET',
      new apigateway.LambdaIntegration(props.gapAnalysisFunction),
      {
        authorizer,
        authorizationType: apigateway.AuthorizationType.COGNITO,
      }
    );

    gaps.addMethod(
      'POST',
      new apigateway.LambdaIntegration(props.gapAnalysisFunction),
      {
        authorizer,
        authorizationType: apigateway.AuthorizationType.COGNITO,
      }
    );

    // Scout Chatbot endpoints
    const scout = this.api.root.addResource('scout');
    scout.addMethod(
      'POST',
      new apigateway.LambdaIntegration(props.scoutChatbotFunction),
      {
        authorizer,
        authorizationType: apigateway.AuthorizationType.COGNITO,
      }
    );

    const conversation = scout.addResource('conversation');
    conversation.addMethod(
      'GET',
      new apigateway.LambdaIntegration(props.scoutChatbotFunction),
      {
        authorizer,
        authorizationType: apigateway.AuthorizationType.COGNITO,
      }
    );

    // Report endpoints
    const report = this.api.root.addResource('report');
    report.addMethod(
      'GET',
      new apigateway.LambdaIntegration(props.reportFunction),
      {
        authorizer,
        authorizationType: apigateway.AuthorizationType.COGNITO,
      }
    );

    // Frontend hosting with S3 and CloudFront
    const frontendBucket = new s3.Bucket(this, 'FrontendBucket', {
      publicReadAccess: false,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
    });

    const originAccessIdentity = new cloudfront.OriginAccessIdentity(this, 'OAI');
    frontendBucket.grantRead(originAccessIdentity);

    this.distribution = new cloudfront.Distribution(this, 'FrontendDistribution', {
      defaultBehavior: {
        origin: new origins.S3Origin(frontendBucket, {
          originAccessIdentity,
        }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
      },
      defaultRootObject: 'index.html',
      errorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
        },
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
        },
      ],
    });

    // Outputs
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: this.api.url,
      description: 'API Gateway URL',
    });

    new cdk.CfnOutput(this, 'FrontendBucketName', {
      value: frontendBucket.bucketName,
      description: 'Frontend S3 bucket name',
    });

    new cdk.CfnOutput(this, 'CloudFrontUrl', {
      value: `https://${this.distribution.distributionDomainName}`,
      description: 'CloudFront distribution URL',
    });
  }
}
