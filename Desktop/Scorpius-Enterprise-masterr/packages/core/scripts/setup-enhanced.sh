#!/usr/bin/env bash
# Setup script for Scorpius Enhanced Scanner with Hardhat simulation support

echo "🔧 Setting up Scorpius Enhanced Vulnerability Scanner..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js from https://nodejs.org/"
    echo "   Minimum version required: Node.js 16.x or higher"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm (usually comes with Node.js)"
    exit 1
fi

echo "✅ Node.js $(node --version) found"
echo "✅ npm $(npm --version) found"

# Check if Python is installed
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8 or higher"
    exit 1
fi

# Determine Python command
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo "✅ Python $($PYTHON_CMD --version) found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
$PYTHON_CMD -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Test Hardhat installation capability
echo "🧪 Testing Hardhat setup capability..."
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# Create minimal package.json for testing
cat > package.json << EOF
{
  "name": "hardhat-test",
  "version": "1.0.0",
  "devDependencies": {
    "@nomicfoundation/hardhat-toolbox": "^4.0.0",
    "hardhat": "^2.19.0"
  }
}
EOF

# Try to install Hardhat (this may take a moment)
echo "📦 Testing npm install (this may take a moment)..."
timeout 120 npm install --silent

if [ $? -eq 0 ]; then
    echo "✅ Hardhat installation test successful"
    
    # Test if Hardhat can initialize
    npx hardhat --version > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "✅ Hardhat is working correctly"
    else
        echo "⚠️  Hardhat installed but may have issues"
    fi
else
    echo "⚠️  Hardhat installation test failed or timed out"
    echo "   Simulation features may not work, but other scanner features will function"
fi

# Cleanup
cd - > /dev/null
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Quick Start:"
echo "   1. Run a simple test: python test_enhanced_scanner.py"
echo "   2. Run the demo: python demo_enhanced_scanner.py" 
echo "   3. Use the CLI: python -m cli.scanner_cli --help"
echo ""
echo "🔍 For simulation features:"
echo "   - Ensure Node.js 16+ and npm are installed"
echo "   - Internet connection required for Hardhat dependencies"
echo "   - First simulation run may take longer as dependencies download"
echo ""
echo "🚀 Ready to scan for vulnerabilities!"
