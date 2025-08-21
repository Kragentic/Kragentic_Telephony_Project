defmodule KragenticTelephony.Contacts do
  import Ecto.Query, warn: false
  require Ecto.Query
  alias KragenticTelephony.Repo
  alias KragenticTelephony.Contacts.Contact
  alias KragenticTelephony.Contacts.CsvImporter
  alias Oban.Job

  def list_contacts do
    Repo.all(Contact)
  end

  def get_contact!(id), do: Repo.get!(Contact, id)

  def create_contact(attrs \\ %{}) do
    %Contact{}
    |> Contact.changeset(attrs)
    |> Repo.insert()
  end

  def update_contact(%Contact{} = contact, attrs) do
    contact
    |> Contact.changeset(attrs)
    |> Repo.update()
  end

  def delete_contact(%Contact{} = contact) do
    Repo.delete(contact)
  end

  def change_contact(%Contact{} = contact, attrs \\ %{}) do
    Contact.changeset(contact, attrs)
  end

  def import_contacts_from_csv(file_path) do
    case File.read(file_path) do
      {:ok, csv_content} ->
        CsvImporter.import_from_csv(csv_content)

      {:error, reason} ->
        {:error, "Failed to read file: #{reason}"}
    end
  end

  def process_contact(contact_id, delay \\ 0) do
    contact = get_contact!(contact_id)

    # Schedule the job with Oban
    args = %{action: "process_contact", contact_id: contact_id}
    schedule_job(args, delay)
  end

  defp schedule_job(args, delay) do
    Job.schedule(
      Oban.Worker,
      args: args,
      execute_after: delay * 1000
    )
  end

  def get_contacts_by_status(status) do
    from(c in Contact, where: c.consent_status == ^status)
    |> Repo.all()
  end

  def get_blacklisted_contacts do
    from(c in Contact, where: c.blacklisted == true)
    |> Repo.all()
  end
end
