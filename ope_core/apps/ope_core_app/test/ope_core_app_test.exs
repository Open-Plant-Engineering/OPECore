defmodule OpeCoreAppTest do
  use ExUnit.Case
  doctest OpeCoreApp

  test "greets the world" do
    assert OpeCoreApp.hello() == :world
  end
end
