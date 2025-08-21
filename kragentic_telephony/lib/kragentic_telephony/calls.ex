defmodule KragenticTelephony.Calls do
  import Ecto.Query, warn: false
  require Ecto.Query
  alias KragenticTelephony.Repo
  alias KragenticTelephony.Calls.Call

  def list_calls do
    Repo.all(Call)
  end

  def get_call!(id), do: Repo.get!(Call, id)

  def get_call_by_telnyx_id(telnyx_call_id) do
    Repo.get_by(Call, telnyx_call_id: telnyx_call_id)
  end

  def create_call(attrs \\ %{}) do
    %Call{}
    |> Call.changeset(attrs)
    |> Repo.insert()
  end

  def update_call(%Call{} = call, attrs) do
    call
    |> Call.changeset(attrs)
    |> Repo.update()
  end

  def delete_call(%Call{} = call) do
    Repo.delete(call)
  end

  def change_call(%Call{} = call, attrs \\ %{}) do
    Call.changeset(call, attrs)
  end

  def get_calls_by_status(status) do
    from(c in Call, where: c.status == ^status)
    |> Repo.all()
  end

  def get_calls_by_date_range(start_date, end_date) do
    from(c in Call, where: c.started_at >= ^start_date and c.started_at <= ^end_date)
    |> Repo.all()
  end

  def get_calls_by_phone_number(phone_number) do
    from(c in Call, where: c.from_number == ^phone_number or c.to_number == ^phone_number)
    |> Repo.all()
  end
end
