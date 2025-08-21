import Config

# General application configuration
config :kragentic_telephony,
  ecto_repos: [KragenticTelephony.Repo]

# Configures the endpoint
config :kragentic_telephony, KragenticTelephonyWeb.Endpoint,
  url: [host: "localhost"],
  render_errors: [
    formats: [html: KragenticTelephonyWeb.ErrorHTML, json: KragenticTelephonyWeb.ErrorJSON],
    layout: false
  ],
  pubsub_server: KragenticTelephony.PubSub,
  live_view: [signing_salt: "SECRET_SALT"]

# Configure esbuild (the version is required)
config :esbuild,
  version: "0.17.11",
  kragentic_telephony: [
    args:
      ~w(js/app.js --bundle --target=es2017 --outdir=../priv/static/assets --external:/fonts/* --external:/images/*),
    cd: Path.expand("../assets", __DIR__),
    env: %{"NODE_PATH" => Path.expand("../deps", __DIR__)}
  ]

# Configure tailwind (the version is required)
config :tailwind,
  version: "3.4.0",
  kragentic_telephony: [
    args: ~w(
      --config=tailwind.config.js
      --input=css/app.css
      --output=../priv/static/assets/app.css
    ),
    cd: Path.expand("../assets", __DIR__)
  ]

# Configures Elixir's Logger
config :logger, :console,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]

# Use Jason for JSON parsing in Phoenix
config :phoenix, :json_library, Jason

# LiveKit configuration
config :kragentic_telephony,
  livekit_api_key: System.get_env("LIVEKIT_API_KEY"),
  livekit_api_secret: System.get_env("LIVEKIT_API_SECRET"),
  livekit_url: System.get_env("LIVEKIT_URL", "ws://localhost:7880")

# Import environment specific config
import_config "#{config_env()}.exs"
