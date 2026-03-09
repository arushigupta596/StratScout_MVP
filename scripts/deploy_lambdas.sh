#!/bin/bash
set -e

echo "Deploying Lambda functions..."
cd infrastructure
npx cdk deploy --require-approval never
echo "Deployment complete!"
