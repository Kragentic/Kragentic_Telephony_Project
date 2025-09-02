defmodule LivekitCoreTest do
  use ExUnit.Case
  doctest LivekitCore

  test "greets the world" do
    assert LivekitCore.hello() == :world
  end
end
