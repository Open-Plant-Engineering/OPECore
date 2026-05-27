import os
from opecore.storage.record import Record
from opecore.storage.header import Header, HEADER_SIZE

DATA_START = HEADER_SIZE * 2

class FileManager:
    def __init__(self, path):
        self.path = path

        if not os.path.exists(path):
            with open(path, "wb") as f:
                # initialize double headers
                empty = Header().encode()
                f.write(empty)
                f.write(empty)

        self.fd = open(path, "r+b")

        # load header
        self.header = self._load_header()

    # ✅ context manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def _load_header(self):
        self.fd.seek(0)

        h1_data = self.fd.read(HEADER_SIZE)
        h2_data = self.fd.read(HEADER_SIZE)

        h1 = Header.decode(h1_data)
        h2 = Header.decode(h2_data)

        if h1 and h2:
            return h1 if h1.txn_id >= h2.txn_id else h2
        return h1 or h2 or Header()

    def _write_header(self, new_header: Header):
        # alternate header slots
        offset = 0 if new_header.txn_id % 2 == 0 else HEADER_SIZE

        self.fd.seek(offset)
        self.fd.write(new_header.encode())
        self.fd.flush()
        os.fsync(self.fd.fileno())

    def update_root(self, root_offset):
        new_txn = self.header.txn_id + 1

        new_header = Header(
            root_offset=root_offset,
            version=self.header.version,
            txn_id=new_txn,
        )

        self._write_header(new_header)
        self.header = new_header

    def append_record(self, rtype, payload):
        self.fd.seek(0, os.SEEK_END)

        file_offset = self.fd.tell()

        # ✅ logical offset = exclude headers
        logical_offset = file_offset - DATA_START

        data = Record.encode(rtype, payload)
        self.fd.write(data)
        self.fd.flush()
        os.fsync(self.fd.fileno())

        return logical_offset

    def read_at(self, offset):
        # ✅ convert logical → physical
        physical = offset + DATA_START
    
        self.fd.seek(physical)
        return Record.decode(self.fd)

    def close(self):
        if self.fd and not self.fd.closed:
            self.fd.close()

    def scan_records(self):
        """
        Iterate through all records (used for recovery / WAL).
        MUST skip headers.
        """

        self.fd.seek(DATA_START)

        while True:
            pos = self.fd.tell()

            try:
                rec = Record.decode(self.fd)
            except Exception:
                break  # stop on corruption / EOF

            if rec is None:
                break

            # ✅ return LOGICAL offset
            logical_offset = pos - DATA_START

            yield logical_offset, rec

    def append_txn_record(self, rtype, txn_id, payload):
        full_payload = txn_id.to_bytes(8, "little") + payload
        return self.append_record(rtype, full_payload)
    
    def read_txn_record(self, offset):
        rtype, payload = self.read_at(offset)

        txn_id = int.from_bytes(payload[:8], "little")
        data = payload[8:]

        return rtype, txn_id, data
