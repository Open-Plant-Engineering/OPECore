import os
from opecore.storage.record import Record


class FileManager:
    def __init__(self, path):
        self.path = path

        # Ensure file exists
        if not os.path.exists(path):
            open(path, "wb").close()

        # Open in read+write binary mode
        self.fd = open(path, "r+b")

    # ✅ Context manager support
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def append_record(self, rtype, payload):
        self.fd.seek(0, os.SEEK_END)
        offset = self.fd.tell()

        data = Record.encode(rtype, payload)
        self.fd.write(data)
        self.fd.flush()
        os.fsync(self.fd.fileno())

        return offset

    def read_at(self, offset):
        self.fd.seek(offset)
        return Record.decode(self.fd)

    def scan_records(self):
        self.fd.seek(0)
        while True:
            pos = self.fd.tell()
            rec = Record.decode(self.fd)
            if rec is None:
                break
            yield pos, rec

    def close(self):
        if self.fd and not self.fd.closed:
            self.fd.close()
        
