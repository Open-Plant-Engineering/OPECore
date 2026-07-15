defmodule OpeCoreGrpcTest do
  use ExUnit.Case
  doctest OpeCoreGrpc

  test "greets the world" do
    assert OpeCoreGrpc.hello() == :world
  end
end
