defmodule MCPBackend.ComplianceTest do
  use ExUnit.Case

  test "requests consent" do
    assert MCPBackend.Compliance.request_consent("1234567890") == :ok
  end

  test "stores consent log" do
    assert MCPBackend.Compliance.store_consent_log("1234567890", true) == :ok
  end
end
