#!/bin/bash

set -e

# This script installs a pip package in compute instance azureml_py38 environment.

sudo -u azureuser -i <<'EOF'


ENVIRONMENT=azureml_py38_tensorflow 
conda activate "$ENVIRONMENT"
sudo apt-get update
sudo apt-get install -y xvfb ffmpeg freeglut3-dev
pip install 'imageio==2.4.0'
pip install pyvirtualdisplay
pip install tensorflow
pip install tf-agents[reverb]
pip install pyglet
conda deactivate
EOF
