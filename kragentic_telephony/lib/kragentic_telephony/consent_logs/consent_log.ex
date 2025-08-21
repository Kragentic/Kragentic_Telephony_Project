defmodule KragenticTelephony.ConsentLogs.ConsentLog do
  use Ecto.Schema
  import Ecto.Changeset

  schema "consent_logs" do
    field :call_sid, :string
    field :phone_number, :string
    field :consent_given, :boolean, default: false
    field :recording_enabled, :boolean, default: false
    field :timestamp, :utc_datetime
    field :timeout, :boolean, default: false

    timestamps()
  end

  @doc false
  def changeset(consent_log, attrs) do
    consent_log
    |> cast(attrs, [:call_sid, :phone_number, :consent_given, :recording_enabled, :timestamp, :timeout])
    |> validate_required([:call_sid, :phone_number, :consent_given, :recording_enabled, :timestamp])
    |> unique_constraint([:call_sid])
  end
end
