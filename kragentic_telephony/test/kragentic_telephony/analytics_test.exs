defmodule KragenticTelephony.AnalyticsTest do
  use ExUnit.Case, async: true

  alias KragenticTelephony.Analytics
  alias KragenticTelephony.Analytics.Analytic

  describe "Analytics" do
    test "tracks an event" do
      Analytics.track_event("call_started", %{duration: 120, consent_given: true, blacklisted: false})

      analytics = Analytics.get_analytics()
      assert length(analytics) == 1
      assert analytics[0].event == "call_started"
    end

    test "gets analytics data for a specific time range" do
      # Track some events
      Analytics.track_event("call_started", %{duration: 120, consent_given: true, blacklisted: false})
      Analytics.track_event("call_ended", %{duration: 120, consent_given: true, blacklisted: false})

      # Get analytics for a specific date range
      start_date = DateTime.utc_now() - 1
      end_date = DateTime.utc_now() + 1

      analytics = Analytics.get_analytics(start_date, end_date)
      assert length(analytics) == 2
    end

    test "gets aggregated analytics data" do
      # Track some events
      Analytics.track_event("call_started", %{duration: 120, consent_given: true, blacklisted: false})
      Analytics.track_event("call_ended", %{duration: 120, consent_given: true, blacklisted: false})
      Analytics.track_event("call_started", %{duration: 150, consent_given: false, blacklisted: true})

      aggregated_analytics = Analytics.get_aggregated_analytics()
      assert length(aggregated_analytics) == 1
      assert aggregated_analytics[0].event == "call_started"
      assert aggregated_analytics[0].count == 2
      assert aggregated_analytics[0].avg_duration == 135
      assert aggregated_analytics[0].consent_rate == 0.5
      assert aggregated_analytics[0].blacklist_rate == 0.5
    end

    test "creates a daily aggregation job" do
      # This is a bit tricky to test directly, but we can verify the function runs
      assert KragenticTelephony.Analytics.create_daily_aggregation_job() == :ok
    end
  end
end
