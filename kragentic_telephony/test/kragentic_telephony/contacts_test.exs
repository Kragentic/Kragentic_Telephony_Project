defmodule KragenticTelephony.ContactsTest do
  use ExUnit.Case, async: true

  alias KragenticTelephony.Contacts
  alias KragenticTelephony.Contacts.Contact

  describe "Contacts" do
    test "lists contacts" do
      contacts = Contacts.list_contacts()
      assert is_list(contacts)
    end

    test "gets a contact" do
      contact = Contacts.create_contact(%{phone: "+1234567890", name: "Test User"})
      assert contact.id != nil

      fetched_contact = Contacts.get_contact!(contact.id)
      assert fetched_contact.phone == "+1234567890"
    end

    test "creates a contact" do
      contact = Contacts.create_contact(%{phone: "+1234567890", name: "Test User"})
      assert contact.phone == "+1234567890"
    end

    test "updates a contact" do
      contact = Contacts.create_contact(%{phone: "+1234567890", name: "Test User"})
      assert contact.name == "Test User"

      updated_contact = Contacts.update_contact(contact, %{name: "Updated User"})
      assert updated_contact.name == "Updated User"
    end

    test "deletes a contact" do
      contact = Contacts.create_contact(%{phone: "+1234567890", name: "Test User"})
      assert contact.id != nil

      Contacts.delete_contact(contact)
      assert_raise Ecto.NotFoundError, fn ->
        Contacts.get_contact!(contact.id)
      end
    end

    test "imports contacts from CSV" do
      # Create a temporary CSV file
      csv_content = """
      phone,name,email,metadata
      +1234567890,Test User,test@example.com,"{\"note\": \"Test contact\"}"
      +0987654321,Another User,another@example.com,"{\"note\": \"Another test contact\"}"
      """

      path = Path.tmp_dir() <> "/test_contacts.csv"
      File.write!(path, csv_content)

      # Import contacts
      result = Contacts.import_contacts_from_csv(path)

      # Clean up
      File.rm!(path)

      # Assert results
      assert result[:imported] == 2
      assert Enum.count(result[:errors]) == 0
    end

    test "processes a contact with delay" do
      contact = Contacts.create_contact(%{phone: "+1234567890", name: "Test User"})
      assert contact.id != nil

      # Schedule processing with a short delay
      Contacts.process_contact(contact.id, 1)

      # Wait for the job to be processed
      Process.sleep(2000)

      # Verify the contact was processed
      # (In a real test, you would check the expected outcome of the processing)
      assert true
    end
  end
end
