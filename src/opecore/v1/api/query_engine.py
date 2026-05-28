class QueryEngine:
    def __init__(self, db):
        self.db = db

    # ------------------------
    # PUBLIC API
    # ------------------------

    def query(self, q: dict):
        """
        Example:

        {
            "or": [
                {"name": {"eq": b"A"}},
                {"type": {"match": b"PIPE"}}
            ],
            "status": {"not": {"eq": b"D"}},
            "sort": ("name", "asc")
        }
        """

        # ✅ extract sort
        sort = q.pop("sort", None)

        # ✅ evaluate
        result = self._eval_query(q)

        # ✅ sorting
        if sort:
            field, direction = sort
            result = self._sort(result, field, direction)

        return result

    # ------------------------
    # QUERY EVALUATION
    # ------------------------
    def _eval_query(self, q):
        result_sets = []
    
        # ✅ handle OR first (but DO NOT return early)
        if "or" in q:
            or_results = set()
            for sub in q["or"]:
                or_results.update(self._eval_query(sub))
            result_sets.append(or_results)
    
        # ✅ handle normal conditions
        for field, condition in q.items():
            if field == "or":
                continue
            
            matches = self._eval_condition(field, condition)
            result_sets.append(set(matches))
    
        if not result_sets:
            return []
    
        # ✅ APPLY AND across everything
        result = result_sets[0]
        for s in result_sets[1:]:
            result = result.intersection(s)
    
        return list(result)

    # ------------------------
    # CONDITIONS
    # ------------------------

    def _eval_condition(self, field, condition):

        if "match" in condition:
            return self.db.find(field, condition["match"])

        if "matchwild" in condition:
            return self._matchwild(field, condition["matchwild"])

        if "inset" in condition:
            return self._inset(field, condition["inset"])

        if "not" in condition:
            return self._not(field, condition["not"])

        # ✅ Comparisons
        if "eq" in condition:
            return self._compare(field, condition["eq"], "eq")

        if "ne" in condition:
            return self._compare(field, condition["ne"], "ne")

        if "gt" in condition:
            return self._compare(field, condition["gt"], "gt")

        if "gte" in condition:
            return self._compare(field, condition["gte"], "gte")

        if "lt" in condition:
            return self._compare(field, condition["lt"], "lt")

        if "lte" in condition:
            return self._compare(field, condition["lte"], "lte")

        return []

    # ------------------------
    # OPERATORS
    # ------------------------

    def _inset(self, field, values):
        results = set()
        for v in values:
            results.update(self.db.find(field, v))
        return list(results)

    def _matchwild(self, field, prefix):
        results = []

        for oid in self.db.range(0, (1 << 63) - 1):
            obj = self.db.get(oid)
            if obj and field in obj:
                if obj[field].startswith(prefix):
                    results.append(oid)

        return results

    def _not(self, field, inner):
        all_ids = set(self.db.range(0, (1 << 63) - 1))
        matched = set(self._eval_condition(field, inner))
        return list(all_ids - matched)

    # ------------------------
    # COMPARISON ENGINE
    # ------------------------

    def _compare(self, field, value, op):
        results = []

        # scan all
        for oid in self.db.range(0, (1 << 63) - 1):
            obj = self.db.get(oid)

            if not obj or field not in obj:
                continue

            v = obj[field]

            try:
                # ✅ byte-safe comparison
                if op == "eq" and v == value:
                    results.append(oid)
                elif op == "ne" and v != value:
                    results.append(oid)
                elif op == "gt" and v > value:
                    results.append(oid)
                elif op == "gte" and v >= value:
                    results.append(oid)
                elif op == "lt" and v < value:
                    results.append(oid)
                elif op == "lte" and v <= value:
                    results.append(oid)
            except:
                continue

        return results

    # ------------------------
    # SORTING
    # ------------------------

    def _sort(self, ids, field, direction):
        data = []

        for oid in ids:
            obj = self.db.get(oid)
            val = obj.get(field) if obj else None
            data.append((oid, val))

        reverse = direction == "desc"

        data.sort(key=lambda x: (x[1] is None, x[1]), reverse=reverse)

        return [oid for oid, _ in data]