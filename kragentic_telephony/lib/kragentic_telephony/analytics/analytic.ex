defmodule KragenticTelephony.Analytics.Analytic do
  use Ecto.Schema
  import Ecto.Changeset

  schema "analytics" do
    field :metric, :string
    field :value, :float
    field :date, :date
    field :metadata, :map, default: %{}
    
    timestamps(type: :utc_datetime)
  end

  @doc false
  def changeset(analytic, attrs) do
    analytic
    |> cast(attrs, [:metric, :value, :date, :metadata])
    |> validate_required([:metric, :value, :date])
  end
end
