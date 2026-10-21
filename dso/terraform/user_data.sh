#!/bin/bash
set -euxo pipefail
dnf install -y docker
systemctl enable --now docker
usermod -aG docker ec2-user
docker run -d --name sarps --restart unless-stopped -p 80:8000 ${docker_image}
