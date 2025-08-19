alias KragenticTelephony.Repo
alias KragenticTelephony.Calls.Call
alias KragenticTelephony.Contacts.Contact
alias KragenticTelephony.Campaigns.Campaign
alias KragenticTelephony.ConsentLogs.ConsentLog
alias KragenticTelephony.Analytics.Analytic

# Insert sample contacts
contacts = [
  %{phone: "+15551234567", name: "John Doe", email: "john@example.com", consent_status: "granted"},
  %{phone: "+15551234568", name: "Jane Smith", email: "jane@example.com", consent_status: "pending"},
  %{phone: "+15551234569", name: "Bob Johnson", email: "bob@example.com", consent_status: "denied", blacklisted: true}
]

Enum.each(contacts, fn contact ->
  Contact.changeset(%Contact{}, contact) |> Repo.insert!()
end)

# Insert sample campaigns
campaigns = [
  %{name: "Product Launch", status: "active", script_template: "Hello, we're excited to share our new product..."},
  %{name: "Customer Survey", status: "draft", script_template: "We'd love your feedback on our service..."}
]

Enum.each(campaigns, fn campaign ->
  Campaign.changeset(%Campaign{}, campaign) |> Repo.insert!()
end)

# Insert sample analytics data
analytics = [
  %{metric: "total_calls", value: 100, date: Date.utc_today()},
  %{metric: "consent_rate", value: 0.85, date: Date.utc_today()},
  %{metric: "avg_call_duration", value: 180, date: Date.utc_today()}
]

Enum.each(analytics, fn analytic ->
  Analytic.changeset(%Analytic{}, analytic) |> Repo.insert!()
end)

IO.puts("Database seeded successfully!")
