defmodule KragenticTelephony.Calls.Call do
  use Ecto.Schema
  import Ecto.Changeset

  schema "calls" do
    field :telnyx_call_id, :string
    field :direction, :string
    field :status, :string
    field :recording_url, :string
    field :consent_granted, :boolean, default: false
    field :from_number, :string
    field :to_number, :string
    field :duration_seconds, :integer
    field :started_at, :utc_datetime
    field :ended_at, :utc_datetime

    has_many :consent_logs, KragenticTelephony.ConsentLogs.ConsentLog

    timestamps(type: :utc_datetime)
  end

  @doc false
  def changeset(call, attrs) do
    call
    |> cast(attrs, [
      :telnyx_call_id,
      :direction,
      :status,
      :recording_url,
      :consent_granted,
      :from_number,
      :to_number,
      :duration_seconds,
      :started_at,
      :ended_at
    ])
    |> validate_required([:telnyx_call_id, :direction, :status])
    |> unique_constraint(:telnyx_call_id)
  end
end
