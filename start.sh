#!/bin/bash

# Install Chromium
apt-get update && apt-get install -y chromium-browser

# Set the path for Chromium
export PATH=$PATH:/usr/bin/chromium-browser

# Run your Flask app
python3 main.py
