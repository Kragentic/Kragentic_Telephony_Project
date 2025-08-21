defmodule KragenticTelephony.ContactsTest do
  use KragenticTelephony.DataCase

  alias KragenticTelephony.Contacts
  alias KragenticTelephony.Contacts.Contact

  describe "contacts" do
    @valid_attrs %{phone: "+1234567890", name: "John Doe", metadata: %{"notes" => "VIP customer"}}
    @update_attrs %{phone: "+1234567890", name: "John Smith", metadata: %{"notes" => "Updated notes"}}
    @invalid_attrs %{phone: "invalid", name: nil}

    def contact_fixture(attrs \\ %{}) do
      {:ok, contact} =
        attrs
        |> Enum.into(@valid_attrs)
        |> Contacts.create_contact()

      contact
    end

    test "list_contacts/0 returns all contacts" do
      contact = contact_fixture()
      assert Contacts.list_contacts() == [contact]
    end

    test "get_contact!/1 returns the contact with given id" do
      contact = contact_fixture()
      assert Contacts.get_contact!(contact.id) == contact
    end

    test "create_contact/1 with valid data creates a contact" do
      assert {:ok, %Contact{} = contact} = Contacts.create_contact(@valid_attrs)
      assert contact.phone == "+1234567890"
      assert contact.name == "John Doe"
    end

    test "create_contact/1 with invalid data returns error changeset" do
      assert {:error, %Ecto.Changeset{}} = Contacts.create_contact(@invalid_attrs)
    end

    test "update_contact/2 with valid data updates the contact" do
      contact = contact_fixture()
      assert {:ok, %Contact{} = contact} = Contacts.update_contact(contact, @update_attrs)
      assert contact.name == "John Smith"
    end

    test "update_contact/2 with invalid data returns error changeset" do
      contact = contact_fixture()
      assert {:error, %Ecto.Changeset{}} = Contacts.update_contact(contact, @invalid_attrs)
      assert contact == Contacts.get_contact!(contact.id)
    end

    test "delete_contact/1 deletes the contact" do
      contact = contact_fixture()
      assert {:ok, %Contact{}} = Contacts.delete_contact(contact)
      assert_raise Ecto.NoResultsError, fn -> Contacts.get_contact!(contact.id) end
    end

    test "change_contact/1 returns a contact changeset" do
      contact = contact_fixture()
      assert %Ecto.Changeset{} = Contacts.change_contact(contact)
    end

    test "get_contact_by_phone/1 returns contact for valid phone" do
      contact = contact_fixture()
      assert Contacts.get_contact_by_phone("+1234567890") == contact
    end

    test "get_contact_by_phone/1 returns nil for non-existent phone" do
      assert Contacts.get_contact_by_phone("+9999999999") == nil
    end

    test "list_blacklisted_contacts/0 returns only blacklisted contacts" do
      contact1 = contact_fixture(%{blacklisted: true})
      contact2 = contact_fixture(%{phone: "+1987654321"})
      
      assert Contacts.list_blacklisted_contacts() == [contact1]
    end

    test "blacklisted?/1 checks if phone is blacklisted" do
      contact_fixture(%{phone: "+1234567890", blacklisted: true})
      assert Contacts.blacklisted?("+1234567890") == true
      assert Contacts.blacklisted?("+9999999999") == false
    end
  end
end
