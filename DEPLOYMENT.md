# Fly.io Deployment Guide

This guide covers how to deploy the Kragentic Telephony application to Fly.io.

## Prerequisites

1. Install [Fly.io CLI](https://fly.io/docs/hands-on/install-flyctl/)
2. Create a Fly.io account
3. Install Docker (for local testing)

## Setup Steps

### 1. Install Fly.io CLI
```bash
curl -L https://fly.io/install.sh | sh
```

### 2. Login to Fly.io
```bash
fly auth login
```

### 3. Create the App
```bash
fly apps create kragentic-telephony
```

### 4. Set Environment Variables
```bash
# Copy environment template
cp .env.example .env

# Set your secrets
flyctl secrets set \
  DATABASE_URL=your_database_url \
  SECRET_KEY_BASE=your_secret_key \
  TWILIO_ACCOUNT_SID=your_twilio_sid \
  TWILIO_AUTH_TOKEN=your_twilio_token \
  LIVEKIT_API_KEY=your_livekit_key \
  LIVEKIT_API_SECRET=your_livekit_secret \
  OPENAI_API_KEY=your_openai_key \
  ANTHROPIC_API_KEY=your_anthropic_key
```

### 5. Deploy to Staging
```bash
# Deploy to staging
flyctl deploy --app kragentic-telephony-staging
```

### 6. Deploy to Production
```bash
# Deploy to production
flyctl deploy --app kragentic-telephony
```

## Health Check

The application includes a health check endpoint at `/health` that returns:
- `200 OK` if the application is healthy
- `500 Internal Server Error` if there are issues

## Monitoring

- **Logs**: `fly logs`
- **Status**: `fly status`
- **Scale**: `fly scale show`

## Regions

The application is configured to run in:
- `lax` (Los Angeles) - Primary region
- `ord` (Chicago) - Secondary region
- `fra` (Frankfurt) - European region

## Scaling

```bash
# Scale up
fly scale count 3

# Scale memory
fly scale memory 1024

# Scale CPU
fly scale vm shared-cpu-2x
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check DATABASE_URL secret
   - Verify database is running: `fly status -a kragentic-telephony-db`

2. **Build Failures**
   - Check Dockerfile syntax
   - Verify all dependencies are included

3. **Health Check Failures**
   - Check application logs: `fly logs`
   - Verify health endpoint: `curl https://your-app.fly.dev/health`

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| DATABASE_URL | PostgreSQL connection string | Yes |
| SECRET_KEY_BASE | Phoenix secret key | Yes |
| TWILIO_ACCOUNT_SID | Twilio account identifier | Yes |
| TWILIO_AUTH_TOKEN | Twilio authentication token | Yes |
| LIVEKIT_API_KEY | LiveKit API key | Yes |
| LIVEKIT_API_SECRET | LiveKit API secret | Yes |
| OPENAI_API_KEY | OpenAI API key | Yes |
| ANTHROPIC_API_KEY | Anthropic API key | Yes |

## CI/CD

The GitHub Actions workflow automatically:
- Runs tests on PR
- Deploys to staging on `dev` branch
- Deploys to production on `main` branch

## Local Development

```bash
# Install dependencies
cd kragentic_telephony && mix deps.get

# Run tests
mix test

# Start Phoenix server
mix phx.server
