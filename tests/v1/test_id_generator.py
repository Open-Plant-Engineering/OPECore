from opecore.v1.domain.id_generator import SnowflakeIDGenerator


def test_unique_ids():
    gen = SnowflakeIDGenerator()

    ids = set()

    for _ in range(1000):
        ids.add(gen.generate())

    assert len(ids) == 1000


def test_monotonic_increasing():
    gen = SnowflakeIDGenerator()

    last = gen.generate()

    for _ in range(100):
        current = gen.generate()
        assert current > last
        last = current