defmodule KragenticTelephony.Livekit.RoomTest do
  use ExUnit.Case, async: true
  alias KragenticTelephony.Livekit.Room

  test "create_room/1 creates a new LiveKit room" do
    call_id = "test_call_123"
    assert {:ok, room} = Room.create_room(call_id)
    assert room.name == "call_#{call_id}"
  end

  test "generate_token/2 generates a valid LiveKit token" do
    room_name = "test_room"
    identity = "test_user"
    assert {:ok, token} = Room.generate_token(room_name, identity)
    assert token != nil
  end

  test "connect_participant/2 connects a participant to a LiveKit room" do
    room_name = "test_room"
    identity = "test_user"
    assert {:ok, participant} = Room.connect_participant(room_name, identity)
    assert participant.identity == identity
  end

  test "disconnect_participant/2 disconnects a participant from a LiveKit room" do
    room_name = "test_room"
    identity = "test_user"
    assert :ok = Room.disconnect_participant(room_name, identity)
  end

  test "delete_room/1 deletes a LiveKit room" do
    room_name = "test_room"
    assert :ok = Room.delete_room(room_name)
  end
end
