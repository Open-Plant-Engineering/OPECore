defmodule OpeCoreRepositoryTest do
  use ExUnit.Case
  doctest OpeCoreRepository

  test "greets the world" do
    assert OpeCoreRepository.hello() == :world
  end
end
