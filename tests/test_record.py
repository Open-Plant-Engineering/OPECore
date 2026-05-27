from opecore.storage.record import Record

def test_encode_decode():
    payload = b"hello"
    data = Record.encode(1, payload)

    import io
    f = io.BytesIO(data)

    rtype, out = Record.decode(f)

    assert rtype == 1
    assert out == payload