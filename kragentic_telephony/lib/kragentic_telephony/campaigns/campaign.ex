defmodule KragenticTelephony.Campaigns.Campaign do
  use Ecto.Schema
  require Ecto.Schema
  import Ecto.Changeset

  schema "campaigns" do
    field :name, :string
    field :config, :map, default: %{}
    field :status, :string, default: "draft"
    field :contact_list_id, :integer
    field :script_template, :string
    field :schedule, :map, default: %{}
    field :retry_count, :integer, default: 3
    field :retry_delay_minutes, :integer, default: 60
    field :started_at, :utc_datetime
    field :completed_at, :utc_datetime
    
    timestamps(type: :utc_datetime)
  end

  @doc false
  def changeset(campaign, attrs) do
    campaign
    |> cast(attrs, [
      :name,
      :config,
      :status,
      :contact_list_id,
      :script_template,
      :schedule,
      :retry_count,
      :retry_delay_minutes,
      :started_at,
      :completed_at
    ])
    |> validate_required([:name])
    |> validate_inclusion(:status, ["draft", "active", "paused", "completed"])
  end
end
