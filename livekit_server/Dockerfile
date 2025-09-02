FROM elixir:1.17-alpine AS build

# Install required packages
RUN apk add --no-cache build-base git npm python3

# Set working directory
WORKDIR /app

# Copy mix files
COPY mix.exs mix.lock ./

# Install Hex + Rebar
RUN mix local.hex --force && mix local.rebar --force

# Copy umbrella apps
COPY apps apps
COPY config config

# Install deps
RUN mix deps.get --only prod && mix deps.compile

# Build assets and release
RUN MIX_ENV=prod mix assets.deploy
RUN MIX_ENV=prod mix release

# Final image
FROM alpine:3.18

# Install required packages
RUN apk add --no-cache libstdc++ openssl ncurses-libs

# Set working directory
WORKDIR /app

# Copy release
COPY --from=build /app/_build/prod/rel/livekit_server ./

# Command to start the release
CMD ["bin/livekit_server", "start"]
