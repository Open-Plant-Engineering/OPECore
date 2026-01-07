#!/usr/bin/env bash
set -e

echo "Updating apt..."
sudo apt update -y

echo "Installing system packages required by vcpkg..."
sudo apt install -y \
    build-essential \
    pkg-config \
    autoconf \
    autoconf-archive \
    automake \
    libtool \
    ninja-build \
    curl \
    zip \
    unzip \
    tar \
    python3 \
    python3-distutils \
    python3-venv

echo "System packages installed successfully."