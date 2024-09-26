#!/bin/bash

# Check if docker-compose or docker compose is available
DOCKER_COMPOSE_COMMAND=""

if command -v docker-compose &> /dev/null; then
  DOCKER_COMPOSE_COMMAND="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
  DOCKER_COMPOSE_COMMAND="docker compose"
else
  echo "Neither docker-compose nor docker compose is installed on your system."
  exit 1
fi

echo "Using $DOCKER_COMPOSE_COMMAND."

# Check if directories and files exist
MOUNT_SELENIUM=false
MOUNT_CHROMEDRIVER=false
MOUNT_GOOGLE_CHROME=false

# Check if selenium directory exists
if [ -d "/home/ed/.local/lib/python3.8/site-packages" ]; then
  MOUNT_SELENIUM=true
fi

# Check if chromedriver exists
if [ -f "/usr/bin/chromedriver" ]; then
  MOUNT_CHROMEDRIVER=true
fi

# Check if google-chrome exists
if [ -f "/usr/bin/google-chrome" ]; then
  MOUNT_GOOGLE_CHROME=true
fi

# Run docker-compose with or without overrides based on conditions
if [ "$MOUNT_SELENIUM" = true ] && [ "$MOUNT_CHROMEDRIVER" = true ] && [ "$MOUNT_GOOGLE_CHROME" = true ]; then
  echo "Mounting volumes as all dependencies are present."
  $DOCKER_COMPOSE_COMMAND -f docker-compose.yml -f docker-compose.selenium.yml up --build
else
  echo "Not all dependencies found. Running without volume mounts."
  $DOCKER_COMPOSE_COMMAND -f docker-compose.yml up --build
fi

