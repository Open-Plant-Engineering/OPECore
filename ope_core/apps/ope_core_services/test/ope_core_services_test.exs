defmodule OpeCoreServicesTest do
  use ExUnit.Case
  doctest OpeCoreServices

  test "greets the world" do
    assert OpeCoreServices.hello() == :world
  end
end
