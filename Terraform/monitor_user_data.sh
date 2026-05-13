#!/bin/bash
set -eu

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y python3 python3-pip git ansible

ansible-pull \
  -U ${github_repo} \
  -d /home/ubuntu/TFG-ASIR-AAU \
  -i ansible/inventory \
  ansible/playbooks/monitor.yml
