defmodule KragenticTelephony.Repo.Migrations.CreateCalls do
  use Ecto.Migration

  def change do
    create table(:calls) do
      add :twilio_sid, :string, null: false
      add :direction, :string, null: false
      add :status, :string, null: false
      add :recording_url, :string
      add :consent_granted, :boolean, default: false
      add :from_number, :string
      add :to_number, :string
      add :duration_seconds, :integer
      add :started_at, :utc_datetime
      add :ended_at, :utc_datetime
      
      timestamps(type: :utc_datetime)
    end

    create index(:calls, [:twilio_sid], unique: true)
    create index(:calls, [:from_number])
    create index(:calls, [:to_number])
    create index(:calls, [:status])
    create index(:calls, [:started_at])
  end
end
