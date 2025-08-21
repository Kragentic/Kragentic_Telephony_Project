defmodule KragenticTelephony.CampaignsTest do
  use ExUnit.Case, async: true

  alias KragenticTelephony.Campaigns
  alias KragenticTelephony.Campaigns.Campaign
  alias KragenticTelephony.Campaigns.CampaignRunner

  describe "Campaigns" do
    test "lists campaigns" do
      campaigns = Campaigns.list_campaigns()
      assert is_list(campaigns)
    end

    test "gets a campaign" do
      campaign = Campaigns.create_campaign(%{name: "Test Campaign", config: %{dial_rate: 10, retry_attempts: 3}})
      assert campaign.id != nil

      fetched_campaign = Campaigns.get_campaign!(campaign.id)
      assert fetched_campaign.name == "Test Campaign"
    end

    test "creates a campaign" do
      campaign = Campaigns.create_campaign(%{name: "Test Campaign", config: %{dial_rate: 10, retry_attempts: 3}})
      assert campaign.name == "Test Campaign"
    end

    test "updates a campaign" do
      campaign = Campaigns.create_campaign(%{name: "Test Campaign", config: %{dial_rate: 10, retry_attempts: 3}})
      assert campaign.name == "Test Campaign"

      updated_campaign = Campaigns.update_campaign(campaign, %{name: "Updated Campaign"})
      assert updated_campaign.name == "Updated Campaign"
    end

    test "deletes a campaign" do
      campaign = Campaigns.create_campaign(%{name: "Test Campaign", config: %{dial_rate: 10, retry_attempts: 3}})
      assert campaign.id != nil

      Campaigns.delete_campaign(campaign)
      assert_raise Ecto.NotFoundError, fn ->
        Campaigns.get_campaign!(campaign.id)
      end
    end

    test "starts a campaign" do
      campaign = Campaigns.create_campaign(%{name: "Test Campaign", config: %{dial_rate: 10, retry_attempts: 3}})
      assert campaign.id != nil

      CampaignRunner.start_campaign(campaign.id)
      # Add assertions to verify the campaign started correctly
      assert true
    end

    test "stops a campaign" do
      campaign = Campaigns.create_campaign(%{name: "Test Campaign", config: %{dial_rate: 10, retry_attempts: 3}})
      assert campaign.id != nil

      CampaignRunner.start_campaign(campaign.id)
      CampaignRunner.stop_campaign(campaign.id)
      # Add assertions to verify the campaign stopped correctly
      assert true
    end
  end
end
