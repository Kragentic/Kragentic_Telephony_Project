defmodule MCPBackend.TelephonyTest do
  use ExUnit.Case
  import MCPBackend.Telephony

  test "handles inbound call" do
    assert handle_inbound_call("1234567890") == :ok
  end

  test "handles outbound call" do
    assert handle_outbound_call("1234567890") == :ok
  end
end
