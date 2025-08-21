# LiveKit Real-time Audio Setup Guide

This guide provides complete instructions for setting up LiveKit real-time audio streaming for the Kragentic Telephony project.

## Overview

Task ID 5: "Setup LiveKit Real-time Audio" has been completed with the following components:

1. **LiveKit Room Management Module** - Elixir module for managing audio rooms
2. **Configuration Files** - Complete setup for LiveKit server and client
3. **Docker Integration** - Docker Compose for easy deployment
4. **Environment Configuration** - Proper environment variable setup

## Quick Start

### 1. Environment Variables

Create a `.env` file in the project root:

```bash
# LiveKit Configuration
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
LIVEKIT_URL=ws://localhost:7880

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# Database Configuration
DATABASE_URL=ecto://postgres:postgres@localhost:5432/kragentic_telephony_dev
```

### 2. Start Services with Docker

```bash
# Start all services (PostgreSQL, Redis, LiveKit, Phoenix)
docker-compose up -d

# Check service status
docker-compose ps
```

### 3. Manual LiveKit Installation (Alternative)

If you prefer not to use Docker:

```bash
# Install LiveKit server
curl -sSL https://get.livekit.io | bash

# Start LiveKit server
livekit-server --config livekit.yaml
```

### 4. Install Dependencies

```bash
cd kragentic_telephony
mix deps.get
mix deps.compile
```

## LiveKit Room Module Usage

The `KragenticTelephony.Livekit.Room` module provides the following functions:

### Create a Room
```elixir
{:ok, room} = KragenticTelephony.Livekit.Room.create_room("call_123")
```

### Generate Token
```elixir
{:ok, token} = KragenticTelephony.Livekit.Room.generate_token("call_123", "participant_1")
```

### Connect Participant
```elixir
{:ok, participant} = KragenticTelephony.Livekit.Room.connect_participant("call_123", "participant_1")
```

### Disconnect Participant
```elixir
:ok = KragenticTelephony.Livekit.Room.disconnect_participant("call_123", "participant_1")
```

### Delete Room
```elixir
:ok = KragenticTelephony.Livekit.Room.delete_room("call_123")
```

## Testing the Setup

### 1. Start LiveKit Server
```bash
# Using Docker
docker-compose up livekit

# Or manually
livekit-server --config livekit.yaml
```

### 2. Test Connection
```bash
# Check if LiveKit is running
curl http://localhost:7880/health

# Expected response: {"status":"ok"}
```

### 3. Test Audio Streaming
```bash
# Use LiveKit's test client
# Visit: http://localhost:7880
```

## Integration with Twilio

The LiveKit integration works with Twilio as follows:

1. **Incoming Call** → Twilio webhook creates LiveKit room
2. **Audio Bridge** → Twilio <Stream> connects to LiveKit
3. **AI Agent** → Joins LiveKit room for real-time audio
4. **Recording** → LiveKit provides recording capabilities

## Configuration Files

### livekit.yaml
Contains LiveKit server configuration including:
- Port settings (7880)
- API keys for authentication
- WebRTC configuration
- Room settings

### docker-compose.yml
Complete development environment with:
- PostgreSQL database
- Redis cache
- LiveKit server
- Phoenix application

### Environment Variables
Required environment variables:
- `LIVEKIT_API_KEY`: API key for LiveKit
- `LIVEKIT_API_SECRET`: API secret for LiveKit
- `LIVEKIT_URL`: LiveKit server URL

## Production Deployment

### Fly.io Deployment
```bash
# Deploy LiveKit to Fly.io
fly launch --image livekit/livekit-server:latest --name kragentic-livekit

# Set secrets
flyctl secrets set LIVEKIT_KEYS=your_key:your_secret
```

### Environment Variables for Production
```bash
# Production LiveKit URL
LIVEKIT_URL=wss://your-livekit-app.fly.dev

# Production API credentials
LIVEKIT_API_KEY=your_production_key
LIVEKIT_API_SECRET=your_production_secret
```

## Verification Checklist

- [x] LiveKit server configuration
- [x] Elixir LiveKit client setup
- [x] Docker Compose configuration
- [x] Environment variable setup
- [x] Audio streaming capabilities
- [x] Twilio integration ready
- [x] Production deployment guide

## Next Steps

1. **Task 6**: Implement Consent Flow
2. **Task 7**: Create STT Service
3. **Task 8**: Create TTS Service
4. **Task 9**: Build LangChain AI Agent

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using port 7880
   lsof -i :7880
   
   # Kill process if needed
   kill -9 <PID>
   ```

2. **Docker Issues**
   ```bash
   # Reset Docker environment
   docker-compose down
   docker-compose up --build
   ```

3. **Connection Issues**
   ```bash
   # Test LiveKit connection
   curl http://localhost:7880/health
   
   # Check logs
   docker-compose logs livekit
   ```

## Summary

Task ID 5 "Setup LiveKit Real-time Audio" has been successfully completed with:
- Complete LiveKit server setup
- Elixir client integration
- Docker containerization
- Production deployment guide
- Testing instructions
- Troubleshooting guide

The system is now ready for real-time audio streaming between Twilio calls and AI agents.
