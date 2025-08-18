defmodule MCPBackend.TelephonyTest do
  use ExUnit.Case

  test "handles inbound call" do
    assert MCPBackend.Telephony.handle_inbound_call("1234567890") == :ok
  end

  test "handles outbound call" do
    assert MCPBackend.Telephony.handle_outbound_call("1234567890") == :ok
  end
end
