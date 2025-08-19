defmodule KragenticTelephony.Repo.Migrations.CreateContacts do
  use Ecto.Migration

  def change do
    create table(:contacts) do
      add :phone, :string, null: false
      add :name, :string
      add :email, :string
      add :metadata, :map, default: %{}
      add :blacklisted, :boolean, default: false
      add :consent_status, :string, default: "pending"
      add :last_contacted_at, :utc_datetime
      add :call_count, :integer, default: 0
      
      timestamps(type: :utc_datetime)
    end

    create index(:contacts, [:phone], unique: true)
    create index(:contacts, [:blacklisted])
    create index(:contacts, [:consent_status])
  end
end
