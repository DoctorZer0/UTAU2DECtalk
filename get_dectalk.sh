#!/bin/bash
echo "Downloading latest dectalk release..."
curl -fL -o ubuntu-latest.tar.gz https://github.com/dectalk/dectalk/releases/latest/download/ubuntu-latest.tar.gz

echo "Extracting dectalk release..."
mkdir -p dectalk
tar -xzf ubuntu-latest.tar.gz -C dectalk
echo "Cleaning up..."
rm ubuntu-latest.tar.gz
echo "Done!"