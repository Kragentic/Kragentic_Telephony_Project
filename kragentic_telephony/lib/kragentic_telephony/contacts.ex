defmodule KragenticTelephony.Contacts do
  import Ecto.Query, warn: false
  alias KragenticTelephony.Repo
  alias KragenticTelephony.Contacts.Contact

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
    # Implementation for CSV import
    {:ok, "CSV import functionality to be implemented"}
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
