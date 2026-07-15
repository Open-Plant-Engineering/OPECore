defmodule OpeCoreTestSupportTest do
  use ExUnit.Case
  doctest OpeCoreTestSupport

  test "greets the world" do
    assert OpeCoreTestSupport.hello() == :world
  end
end
