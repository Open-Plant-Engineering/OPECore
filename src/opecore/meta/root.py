import struct

ROOT_RECORD = 6


class RootIndex:
    def __init__(self, file_manager):
        self.fm = file_manager

    def write_root(self, root_offset: int):
        payload = struct.pack("<Q", root_offset)
        self.fm.append_record(ROOT_RECORD, payload)

    def load_latest_root(self):
        latest = None

        for offset, (rtype, payload) in self.fm.scan_records():
            if rtype == ROOT_RECORD:
                root_offset = struct.unpack("<Q", payload)[0]
                latest = root_offset

        return latest