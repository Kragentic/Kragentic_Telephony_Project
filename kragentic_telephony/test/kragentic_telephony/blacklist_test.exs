defmodule KragenticTelephony.BlacklistTest do
  use ExUnit.Case, async: true

  alias KragenticTelephony.Blacklist
  alias KragenticTelephony.Contacts.Contact

  describe "Blacklist" do
    test "checks if a phone is blacklisted" do
      contact = %Contact{phone: "+1234567890", blacklisted: true}
      Repo.insert(contact)

      assert Blacklist.is_blacklisted?("+1234567890")
      assert not Blacklist.is_blacklisted?("+0987654321")
    end

    test "blacklists a phone" do
      contact = %Contact{phone: "+1234567890", blacklisted: false}
      Repo.insert(contact)

      assert not Blacklist.is_blacklisted?("+1234567890")

      Blacklist.blacklist_phone("+1234567890", "profanity")
      assert Blacklist.is_blacklisted?("+1234567890")
    end

    test "unblacklists a phone" do
      contact = %Contact{phone: "+1234567890", blacklisted: true}
      Repo.insert(contact)

      assert Blacklist.is_blacklisted?("+1234567890")

      Blacklist.unblacklist_phone("+1234567890")
      assert not Blacklist.is_blacklisted?("+1234567890")
    end

    test "lists all blacklisted phones" do
      contact1 = %Contact{phone: "+1234567890", blacklisted: true}
      contact2 = %Contact{phone: "+0987654321", blacklisted: true}
      Repo.insert(contact1)
      Repo.insert(contact2)

      blacklisted_phones = Blacklist.list_blacklisted_phones()
      assert length(blacklisted_phones) == 2
      assert Enum.any?(blacklisted_phones, &(&1.phone == "+1234567890"))
      assert Enum.any?(blacklisted_phones, &(&1.phone == "+0987654321"))
    end
  end
end
