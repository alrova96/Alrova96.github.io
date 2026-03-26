#!/bin/bash
# Quick server script for local development

echo "🚀 Starting local development server..."
echo "📁 Building site..."
python3 build.py

echo ""
echo "🌐 Starting server at http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

cd docs
python3 -m http.server 8000
