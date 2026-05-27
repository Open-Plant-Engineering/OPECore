import os
from opecore.v1.infra.record import Record
from opecore.v1.infra.header import Header, HEADER_SIZE


DATA_START = HEADER_SIZE * 2


class FileManager:
    """
    SOLID v1 FileManager

    Responsibility:
    - Manage file lifecycle
    - Append-only record writes
    - Read records by logical offset
    - Maintain header (root pointer)
    """

    def __init__(self, path: str):
        self.path = path
        self.fd = None
        self.header = None

        self._init_file()
        self._open()

    # ------------------------
    # Lifecycle
    # ------------------------

    def _init_file(self):
        if not os.path.exists(self.path):
            with open(self.path, "wb") as f:
                empty = Header().encode()
                f.write(empty)
                f.write(empty)

    def _open(self):
        self.fd = open(self.path, "r+b")
        self.header = self._load_header()

    def close(self):
        if self.fd and not self.fd.closed:
            self.fd.close()
            self.fd = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    # ------------------------
    # Header
    # ------------------------

    def _load_header(self):
        self.fd.seek(0)

        h1_data = self.fd.read(HEADER_SIZE)
        h2_data = self.fd.read(HEADER_SIZE)

        h1 = Header.decode(h1_data)
        h2 = Header.decode(h2_data)

        if h1 and h2:
            return h1 if h1.txn_id >= h2.txn_id else h2

        return h1 or h2 or Header()

    def update_root(self, root_offset):
        new_txn = self.header.txn_id + 1

        new_header = Header(
            root_offset=root_offset,
            version=self.header.version,
            txn_id=new_txn
        )

        self._write_header(new_header)
        self.header = new_header

    def _write_header(self, header):
        offset = 0 if header.txn_id % 2 == 0 else HEADER_SIZE

        self.fd.seek(offset)
        self.fd.write(header.encode())
        self.fd.flush()
        os.fsync(self.fd.fileno())

    # ------------------------
    # Write
    # ------------------------

    def append_record(self, rtype, payload: bytes):
        self.fd.seek(0, os.SEEK_END)

        file_offset = self.fd.tell()
        logical_offset = file_offset - DATA_START

        encoded = Record.encode(rtype, payload)

        self.fd.write(encoded)
        self.fd.flush()
        os.fsync(self.fd.fileno())

        return logical_offset

    def append_txn_record(self, rtype, txn_id, payload):
        full = txn_id.to_bytes(8, "little") + payload
        return self.append_record(rtype, full)

    # ------------------------
    # Read
    # ------------------------

    def read_at(self, offset):
        physical = offset + DATA_START

        self.fd.seek(physical)
        return Record.decode(self.fd)

    def read_txn_record(self, offset):
        rtype, payload = self.read_at(offset)

        txn_id = int.from_bytes(payload[:8], "little")
        data = payload[8:]

        return rtype, txn_id, data

    # ------------------------
    # Scan
    # ------------------------

    def scan_records(self):
        self.fd.seek(DATA_START)

        while True:
            pos = self.fd.tell()

            try:
                record = Record.decode(self.fd)
            except Exception:
                break

            if record is None:
                break

            logical_offset = pos - DATA_START
            yield logical_offset, record