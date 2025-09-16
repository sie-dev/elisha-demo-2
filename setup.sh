#!/bin/bash

echo "🚀 Setting up Chabad Torah Search Interface"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this from the chabad_search_interface directory."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed. Please install pip first."
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully!"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Check if ripgrep is installed
if ! command -v rg &> /dev/null; then
    echo "⚠️  Warning: ripgrep (rg) is not installed."
    echo "   For full functionality, install ripgrep:"
    echo "   macOS: brew install ripgrep"
    echo "   Linux: sudo apt install ripgrep"
else
    echo "✅ ripgrep is installed!"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Get your Claude API key from: https://console.anthropic.com/"
echo "   2. For demo version: Open dropbox_demo.html in your browser"
echo "   3. For full version: Run 'python3 server.py' then open http://localhost:5000"
echo ""
echo "💡 Quick start with demo:"
echo "   open dropbox_demo.html"
echo ""