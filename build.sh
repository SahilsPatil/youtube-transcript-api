#!/bin/bash

# Create a directory for ffmpeg binary in /tmp
mkdir -p /tmp/ffmpeg

# Download ffmpeg binary for Linux (static build)
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz -P /tmp/ffmpeg

# Extract the tar file
tar -xf /tmp/ffmpeg/ffmpeg-release-i686-static.tar.xz -C /tmp/ffmpeg

# Remove the tar file after extraction
rm /tmp/ffmpeg/ffmpeg-release-i686-static.tar.xz

pip install -r requirements.txt
