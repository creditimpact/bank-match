#!/usr/bin/env bash
set -e
echo "Checking Docker..."
if ! command -v docker >/dev/null 2>&1; then
  echo "❌ Docker not installed. Get Docker Desktop: https://www.docker.com/products/docker-desktop"
  exit 1
fi
echo "Docker OK"
echo "Checking docker compose..."
if ! docker compose version >/dev/null 2>&1; then
  echo "❌ docker compose not available. Update Docker Desktop."
  exit 1
fi
echo "docker compose OK"
echo "✅ Environment looks good."
