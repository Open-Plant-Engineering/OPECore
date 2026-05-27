from opecore.version.store import VersionStore


class VersionManager:
    def __init__(self):
        self.version = VersionStore()

        # logical mappings
        self.object_versions = {}   # object_id → latest version
        self.version_objects = {}   # version_id → physical object_id

    # ✅ create new version
    def create_version(self, object_id, parent, physical_obj_id):
        vid = self.version.create(object_id, parent)

        self.object_versions[object_id] = vid
        self.version_objects[vid] = physical_obj_id

        return vid

    # ✅ get latest version
    def get_latest(self, object_id):
        return self.object_versions.get(object_id)

    # ✅ resolve object data (version chain)
    def resolve(self, storage, object_id, version_id):
        result = {}
        visited = set()

        while version_id:
            if version_id in visited:
                break
            visited.add(version_id)

            obj_id = self.version_objects.get(version_id)

            if obj_id:
                obj = storage.obj.get(obj_id)

                for k, _, v in obj["fields"]:
                    key = storage.chunk.get(k).decode()
                    val = storage.chunk.get(v)

                    if key not in result:
                        result[key] = val

            meta = self.version.get(version_id)
            version_id = meta["parent"] if meta else None

        return result

    # ✅ version history
    def get_versions(self, object_id):
        versions = []
        vid = self.object_versions.get(object_id)

        while vid:
            versions.append(vid)
            meta = self.version.get(vid)
            vid = meta["parent"] if meta else None

        return versions

    # ✅ time travel
    def get_as_of(self, storage, object_id, timestamp):
        vid = self.object_versions.get(object_id)

        while vid:
            meta = self.version.get(vid)

            if meta and meta["timestamp"] <= timestamp:
                return self.resolve(storage, object_id, vid)

            vid = meta["parent"] if meta else None

        return None
