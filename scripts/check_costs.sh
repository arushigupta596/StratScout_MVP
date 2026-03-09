#!/bin/bash

echo "======================================"
echo "StratScout - Cost Monitoring"
echo "======================================"
echo ""

# Get current month costs
START_DATE=$(date -u +%Y-%m-01)
END_DATE=$(date -u +%Y-%m-%d)

echo "Checking costs from $START_DATE to $END_DATE..."
echo ""

# Get total cost
TOTAL_COST=$(aws ce get-cost-and-usage \
  --time-period Start=$START_DATE,End=$END_DATE \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --query 'ResultsByTime[0].Total.BlendedCost.Amount' \
  --output text 2>/dev/null || echo "0")

echo "Total Cost This Month: \$$TOTAL_COST"
echo ""

# Get cost by service
echo "Cost by Service:"
echo "----------------"
aws ce get-cost-and-usage \
  --time-period Start=$START_DATE,End=$END_DATE \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE \
  --query 'ResultsByTime[0].Groups[].[Keys[0],Metrics.BlendedCost.Amount]' \
  --output text 2>/dev/null | \
  awk '{printf "%-30s $%.2f\n", $1, $2}' | \
  sort -t'$' -k2 -rn | \
  head -10

echo ""
echo "Target: $250/month"
echo ""

# Check if over budget
if (( $(echo "$TOTAL_COST > 250" | bc -l) )); then
    echo "⚠️  WARNING: Over budget by \$$(echo "$TOTAL_COST - 250" | bc)"
else
    echo "✓ Within budget"
fi
