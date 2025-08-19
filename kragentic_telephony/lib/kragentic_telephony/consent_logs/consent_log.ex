defmodule KragenticTelephony.ConsentLogs.ConsentLog do
  use Ecto.Schema
  import Ecto.Changeset

  schema "consent_logs" do
    field :phone_number, :string
    field :consent_given, :boolean
    field :recording_enabled, :boolean, default: false
    field :consent_method, :string, default: "verbal"
    field :ip_address, :string
    field :user_agent, :string
    field :timestamp, :utc_datetime
    
    belongs_to :call, KragenticTelephony.Calls.Call
    
    timestamps(type: :utc_datetime)
  end

  @doc false
  def changeset(consent_log, attrs) do
    consent_log
    |> cast(attrs, [
      :call_id,
      :phone_number,
      :consent_given,
      :recording_enabled,
      :consent_method,
      :ip_address,
      :user_agent,
      :timestamp
    ])
    |> validate_required([:phone_number, :consent_given, :timestamp])
    |> validate_format(:phone_number, ~r/^\+?[1-9]\d{1,14}$/)
  end
end
