defmodule MCPBackendTest do
  use ExUnit.Case
  doctest MCPBackend

  test "greets the world" do
    assert MCPBackend.hello() == :world
  end
end
