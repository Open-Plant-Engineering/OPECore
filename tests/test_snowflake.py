from opecore.id.snowflake import SnowflakeGenerator


def test_unique():
    gen = SnowflakeGenerator(1)

    a = gen.generate()
    b = gen.generate()

    assert a != b


def test_decode():
    gen = SnowflakeGenerator(2)
    sid = gen.generate()

    d = gen.decode(sid)

    assert d["db_id"] == 2
