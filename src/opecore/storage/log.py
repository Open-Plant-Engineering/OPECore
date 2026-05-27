import os
from opecore.storage.record import Record

class FileManager:

    def __init__(self, path):
        self.path = path
        self.fd = open(path, "r+b" if os.path.exists(path) else "w+b")

    def append_record(self, rtype, payload):
        self.fd.seek(0, os.SEEK_END)
        offset = self.fd.tell()

        data = Record.encode(rtype, payload)
        self.fd.write(data)
        self.fd.flush()
        os.fsync(self.fd.fileno())

        return offset

    def scan_records(self):
        self.fd.seek(0)
        while True:
            pos = self.fd.tell()
            rec = Record.decode(self.fd)
            if rec is None:
                break
            yield pos, rec
