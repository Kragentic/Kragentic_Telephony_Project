defmodule KragenticTelephony.Repo.Migrations.CreateConsentLogs do
  use Ecto.Migration

  def change do
    create table(:consent_logs) do
      add :call_id, references(:calls, on_delete: :nothing)
      add :phone_number, :string, null: false
      add :consent_given, :boolean, null: false
      add :recording_enabled, :boolean, default: false
      add :consent_method, :string, default: "verbal"
      add :ip_address, :string
      add :user_agent, :string
      add :timestamp, :utc_datetime, null: false
      
      timestamps(type: :utc_datetime)
    end

    create index(:consent_logs, [:call_id])
    create index(:consent_logs, [:phone_number])
    create index(:consent_logs, [:timestamp])
    create index(:consent_logs, [:consent_given])
  end
end
