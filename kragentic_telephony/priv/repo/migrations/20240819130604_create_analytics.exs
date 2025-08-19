defmodule KragenticTelephony.Repo.Migrations.CreateAnalytics do
  use Ecto.Migration

  def change do
    create table(:analytics) do
      add :metric, :string, null: false
      add :value, :float, null: false
      add :date, :date, null: false
      add :metadata, :map, default: %{}
      
      timestamps(type: :utc_datetime)
    end

    create index(:analytics, [:metric])
    create index(:analytics, [:date])
    create index(:analytics, [:metric, :date])
  end
end
