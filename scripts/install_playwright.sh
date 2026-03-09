#!/bin/bash
# Install Playwright and browsers

echo "Installing Playwright..."
pip install playwright

echo ""
echo "Installing browser binaries..."
playwright install chromium

echo ""
echo "✅ Playwright installation complete!"
echo ""
echo "Now run:"
echo "  python3 scripts/scrape_ads_automated.py"
