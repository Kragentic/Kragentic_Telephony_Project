FROM python:3.12-slim

# Install git and other needed tools
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && apt-get clean

# Set the working directory
WORKDIR /workspace