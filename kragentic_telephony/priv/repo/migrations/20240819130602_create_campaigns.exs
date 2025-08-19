defmodule KragenticTelephony.Repo.Migrations.CreateCampaigns do
  use Ecto.Migration

  def change do
    create table(:campaigns) do
      add :name, :string, null: false
      add :config, :map, default: %{}
      add :status, :string, default: "draft"
      add :contact_list_id, :integer
      add :script_template, :text
      add :schedule, :map, default: %{}
      add :retry_count, :integer, default: 3
      add :retry_delay_minutes, :integer, default: 60
      add :started_at, :utc_datetime
      add :completed_at, :utc_datetime
      
      timestamps(type: :utc_datetime)
    end

    create index(:campaigns, [:status])
    create index(:campaigns, [:started_at])
  end
end
