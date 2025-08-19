# Multi-stage Dockerfile for Elixir Phoenix application
FROM elixir:1.15-alpine AS builder

# Install build dependencies
RUN apk add --no-cache build-base git nodejs npm

# Set build environment
ENV MIX_ENV=prod

# Install hex and rebar
RUN mix local.hex --force && \
    mix local.rebar --force

# Create app directory
WORKDIR /app

# Copy mix files
COPY kragentic_telephony/mix.exs kragentic_telephony/mix.lock ./
COPY kragentic_telephony/config ./config

# Install dependencies
RUN mix deps.get --only prod
RUN mix deps.compile

# Copy assets and source code
COPY kragentic_telephony/priv ./priv
COPY kragentic_telephony/lib ./lib
COPY kragentic_telephony/assets ./assets

# Build assets
RUN cd assets && npm ci && npm run deploy
RUN mix phx.digest

# Compile application
RUN mix compile

# Create release
RUN mix release

# Production stage
FROM alpine:3.18 AS production

# Install runtime dependencies
RUN apk add --no-cache openssl ncurses-libs libstdc++

# Create non-root user
RUN addgroup -g 1000 elixir && \
    adduser -u 1000 -G elixir -s /bin/sh -D elixir

# Set working directory
WORKDIR /app

# Copy release from builder stage
COPY --from=builder --chown=elixir:elixir /app/_build/prod/rel/kragentic_telephony ./

# Switch to non-root user
USER elixir

# Expose port
EXPOSE 4000

# Set runtime environment
ENV HOME=/app \
    MIX_ENV=prod \
    PORT=4000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD /app/bin/kragentic_telephony eval "KragenticTelephony.HealthCheck.check()" || exit 1

# Start application
CMD ["bin/kragentic_telephony", "start"]
