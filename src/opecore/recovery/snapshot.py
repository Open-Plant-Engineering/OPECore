import pickle

SNAPSHOT = 9


class SnapshotManager:
    def __init__(self, fm):
        self.fm = fm

    def save(self, txn_id, chunk_store, object_store, last_offset):
        data = {
            "last_offset": last_offset,
            "chunk_index": chunk_store.index,
            "object_index": object_store.index,
        }

        payload = pickle.dumps(data)

        self.fm.append_txn_record(SNAPSHOT, txn_id, payload)

    def load_latest(self):
        latest = None

        for offset, (rtype, payload) in self.fm.scan_records():
            if rtype == SNAPSHOT:
                txn_id = int.from_bytes(payload[:8], "little")
                data = pickle.loads(payload[8:])
                latest = data

        return latest