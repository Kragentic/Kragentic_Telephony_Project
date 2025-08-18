# Use an official Elixir runtime as a parent image
FROM elixir:1.13.4-alpine

# Set the working directory
WORKDIR /app

# Copy the mix.exs file and the elixir files
COPY mix.exs mix.exs
COPY lib lib

# Install dependencies
RUN mix deps.get

# Copy the rest of the application code
COPY . .

# Compile the application
RUN mix compile

# Expose the port the app runs on
EXPOSE 4000

# Start the application
CMD ["mix", "run", "--no-halt"]
