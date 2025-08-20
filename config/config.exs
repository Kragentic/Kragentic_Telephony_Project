use Config

config :mcp_backend, Twilio,
  account_sid: System.get_env("TWILIO_ACCOUNT_SID"),
  auth_token: System.get_env("TWILIO_AUTH_TOKEN"),
  phone_number: System.get_env("TWILIO_PHONE_NUMBER")

config :mcp_backend, LiveKit,
  api_url: System.get_env("LIVEKIT_API_URL"),
  api_key: System.get_env("LIVEKIT_API_KEY"),
  secret: System.get_env("LIVEKIT_SECRET")
