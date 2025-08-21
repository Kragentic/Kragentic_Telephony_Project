# Multi-stage build for Elixir Phoenix application
FROM elixir:1.15-alpine AS builder

# Install build dependencies
RUN apk add --no-cache build-base git python3

# Set working directory
WORKDIR /app

# Install Hex and Rebar
RUN mix local.hex --force && \
    mix local.rebar --force

# Copy mix files
COPY mix.exs mix.lock ./
COPY config config

# Install dependencies
RUN mix deps.get --only prod
RUN mix deps.compile

# Copy application files
COPY lib lib
COPY priv priv

# Compile application
RUN mix compile
RUN mix assets.deploy

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

# Set environment
ENV HOME=/app

# Start the release
CMD ["bin/kragentic_telephony", "start"]
