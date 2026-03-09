#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { StratScoutStack } from '../lib/stratscout-stack';

const app = new cdk.App();

new StratScoutStack(app, 'StratScoutStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
  description: 'StratScout Competitive Intelligence Platform - MVP',
});

app.synth();
