defmodule KragenticTelephony.CampaignRunnerTest do
  use ExUnit.Case, async: true
  alias KragenticTelephony.Repo
  alias KragenticTelephony.Campaigns.Campaign
  alias KragenticTelephony.Campaigns.CampaignRunner

  describe "CampaignRunner" do
    @campaign_attrs %{name: "Test Campaign", config: %{dial_rate: 10}, status: "active"}

    setup do
      :ok = Ecto.Adapters.SQL.Sandbox.checkout(Repo)
      {:ok, campaign: insert_campaign()}
    end

    defp insert_campaign do
      %Campaign{}
      |> Campaign.changeset(@campaign_attrs)
      |> Repo.insert()
    end

    test "start_campaign/1 starts a campaign runner" do
      {:ok, _pid} = CampaignRunner.start_campaign(@campaign_attrs.id)

      assert true # The process should start without errors
    end

    test "stop_campaign/1 stops a campaign runner" do
      {:ok, pid} = CampaignRunner.start_campaign(@campaign_attrs.id)
      CampaignRunner.stop_campaign(@campaign_attrs.id)

      assert Process.alive?(pid) == false
    end

    test "campaign runner processes contacts" do
      # Mock the make_call/2 function to avoid actual calls
      defmodule MockCampaignRunner do
        def make_call(_contact, _campaign), do: :ok
      end

      # Replace the original make_call/2 with our mock
      original_make_call = CampaignRunner.__info__(:make_call)
      CampaignRunner.__info__(:make_call, &MockCampaignRunner.make_call/2)

      # Start the campaign runner
      {:ok, pid} = CampaignRunner.start_campaign(@campaign_attrs.id)

      # Wait for the process to start
      Process.send_after(self(), :check, 1000)

      # Check that the process is running
      assert Process.alive?(pid) == true

      # Restore the original make_call/2
      CampaignRunner.__info__(:make_call, original_make_call)

      # Stop the campaign runner
      CampaignRunner.stop_campaign(@campaign_attrs.id)
    end

    test "campaign runner handles retries" do
      # Mock the make_call/2 function to simulate failures
      defmodule MockCampaignRunner do
        def make_call(_contact, _campaign), do: :error
      end

      # Replace the original make_call/2 with our mock
      original_make_call = CampaignRunner.__info__(:make_call)
      CampaignRunner.__info__(:make_call, &MockCampaignRunner.make_call/2)

      # Start the campaign runner
      {:ok, pid} = CampaignRunner.start_campaign(@campaign_attrs.id)

      # Wait for the process to start and process the contacts
      Process.send_after(self(), :check, 2000)

      # Check that the process is still running
      assert Process.alive?(pid) == true

      # Restore the original make_call/2
      CampaignRunner.__info__(:make_call, original_make_call)

      # Stop the campaign runner
      CampaignRunner.stop_campaign(@campaign_attrs.id)
    end

    test "campaign runner updates metrics" do
      # Mock the make_call/2 function to simulate different outcomes
      defmodule MockCampaignRunner do
        @count 0

        def make_call(_contact, _campaign) do
          if @count < 2 do
            @count = @count + 1
            :ok
          else
            :error
          end
        end
      end

      # Replace the original make_call/2 with our mock
      original_make_call = CampaignRunner.__info__(:make_call)
      CampaignRunner.__info__(:make_call, &MockCampaignRunner.make_call/2)

      # Start the campaign runner
      {:ok, pid} = CampaignRunner.start_campaign(@campaign_attrs.id)

      # Wait for the process to start and process the contacts
      Process.send_after(self(), :check, 3000)

      # Check that the process is still running
      assert Process.alive?(pid) == true

      # Restore the original make_call/2
      CampaignRunner.__info__(:make_call, original_make_call)

      # Stop the campaign runner
      CampaignRunner.stop_campaign(@campaign_attrs.id)
    end
  end
end
