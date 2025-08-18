defmodule MCPBackend.CampaignTest do
  use ExUnit.Case

  test "configures campaign" do
    assert MCPBackend.Campaign.configure_campaign("test_campaign", %{}) == :ok
  end

  test "applies dispatch rules" do
    assert MCPBackend.Campaign.apply_dispatch_rules(%{}) == :ok
  end
end
