#!/usr/bin/env bash

set -eou

sudo apt-get update
sudo apt-get install git \
  build-essentials \
  libssl-dev \
  pkg-config \
  ca-certificates \
  sysstat \
  man \
  curl \
  gnupg \
  "linux-modules-extra-$(uname -r)" \
  vnstat


# Install Stellar
# ######################################################

# Download and install the public signing key:
wget -qO - https://apt.stellar.org/SDF.asc | sudo apt-key add -

# Save the repository definition to /etc/apt/sources.list.d/SDF.list:
echo "deb https://apt.stellar.org $(lsb_release -cs) stable" | sudo tee -a /etc/apt/sources.list.d/SDF.list

# Prevent stellar-core from starting post install
ln -s /dev/null /etc/systemd/system/stellar-core.service

# Install packages
sudo apt-get update
sudo apt-get install stellar-core \
  stellar-core-utils \
  stellar-core-postgres

# Install stellar-core and a PostgreSQL database

# Configuration - testnet, db, peers
systemctl start stellar-core
stellar-core new-db
