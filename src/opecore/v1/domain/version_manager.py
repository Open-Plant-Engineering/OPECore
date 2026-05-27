class VersionManager:
    """
    SOLID v1 VersionManager

    Responsibility:
    - Track object → version chain
    - Map version → physical object
    - Resolve object state via version chain

    Does NOT:
    - write to storage
    - manage WAL
    """

    def __init__(self):
        # object_id → latest version_id
        self.object_versions = {}

        # version_id → parent version
        self.parents = {}

        # version_id → physical object_id
        self.version_objects = {}

        self._vid_counter = 1

    # ------------------------
    # VERSION CREATION
    # ------------------------

    def create(self, object_id, parent_version, physical_object_id):
        vid = self._next_version_id()

        self.parents[vid] = parent_version
        self.version_objects[vid] = physical_object_id
        self.object_versions[object_id] = vid

        return vid

    def latest(self, object_id):
        return self.object_versions.get(object_id)

    # ------------------------
    # RESOLUTION
    # ------------------------

    def resolve(self, storage, object_id, version_id):
        """
        Resolve final object view by walking version chain
        """
        result = {}
        visited = set()

        while version_id:
            if version_id in visited:
                break
            visited.add(version_id)

            phys_id = self.version_objects.get(version_id)

            if phys_id:
                obj = storage.obj.get(phys_id)

                for k, _, v in obj["fields"]:
                    key = storage.chunk.get(k).decode()
                    val = storage.chunk.get(v)

                    if key not in result:
                        result[key] = val

            version_id = self.parents.get(version_id)

        return result

    # ------------------------
    # HISTORY
    # ------------------------

    def history(self, object_id):
        versions = []

        vid = self.object_versions.get(object_id)

        while vid:
            versions.append(vid)
            vid = self.parents.get(vid)

        return versions

    # ------------------------
    # TIME TRAVEL
    # ------------------------

    def resolve_as_of(self, storage, object_id, timestamp):
        """
        NOTE:
        Simple implementation (no timestamp tracking yet)
        Placeholder for future extension
        """
        vid = self.latest(object_id)

        return self.resolve(storage, object_id, vid)

    # ------------------------
    # INTERNAL
    # ------------------------

    def _next_version_id(self):
        vid = self._vid_counter
        self._vid_counter += 1
        return vid
