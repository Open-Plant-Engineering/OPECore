class QueryEngine:
    def __init__(self, db):
        self.db = db

    def filter(self, query: dict):
        # ✅ try optimized path first
        candidates = self._get_index_candidates(query)

        # fallback to full scan
        if candidates is None:
            candidates = self.db.list_nodes()

        result = []

        for node in candidates:
            if self._evaluate(node, query):
                result.append(node)

        return result

    def _evaluate(self, node, query):
        # ✅ NOT condition
        if "not" in query:
            return not self._evaluate(node, query["not"])
    
        # ✅ OR condition
        if "or" in query:
            for sub in query["or"]:
                if self._evaluate(node, sub):
                    return True
            return False
    
        # ✅ AND condition
        if "and" in query:
            for sub in query["and"]:
                if not self._evaluate(node, sub):
                    return False
            return True
    
        # ✅ simple condition
        return self._match_simple(node, query)

    def _match_simple(self, node, conditions):
        for k, condition in conditions.items():
            node_value = node.attributes.get(k)

            # ✅ simple equality
            if not isinstance(condition, dict):
                if node_value != condition:
                    return False
                continue

            # ✅ operator-based condition
            if not self._apply_operator(node_value, condition):
                return False

        return True

    def _apply_operator(self, value, condition: dict):
        for op, expected in condition.items():

            # ✅ equality
            if op == "eq":
                if value != expected:
                    return False

            # ✅ greater than
            elif op == "gt":
                if value <= expected:
                    return False

            # ✅ less than
            elif op == "lt":
                if value >= expected:
                    return False

            # ✅ greater or equal
            elif op == "gte":
                if value < expected:
                    return False

            # ✅ less or equal
            elif op == "lte":
                if value > expected:
                    return False

            # ✅ IN operator
            elif op == "in":
                if value not in expected:
                    return False

            # ✅ wildcard match (very simple)
            elif op == "like":
                if not isinstance(value, str):
                    return False

                pattern = expected.replace("*", "")
                if expected.startswith("*") and expected.endswith("*"):
                    if pattern not in value:
                        return False
                elif expected.startswith("*"):
                    if not value.endswith(pattern):
                        return False
                elif expected.endswith("*"):
                    if not value.startswith(pattern):
                        return False
                else:
                    if value != expected:
                        return False

            else:
                raise ValueError(f"Unknown operator: {op}")

        return True
    def _get_index_candidates(self, query):
        conditions = self._extract_simple_conditions(query)

        indexed_results = []

        for k, op, v in conditions:

            # ✅ name index (only eq supported)
            if k == "name" and op == "eq":
                ref = self.db.name_index.get(v)
                if not ref:
                    return []
                indexed_results.append({ref})
                continue

            # ✅ generic index
            if op == "eq":
                refs = self.db.generic_index.get(k, v)
                if refs:
                    indexed_results.append(set(refs))

            # ✅ RANGE SUPPORT 🔥
            elif op in ["gt", "lt", "gte", "lte"]:
                refs = self._range_lookup(k, op, v)
                if refs:
                    indexed_results.append(set(refs))

        if not indexed_results:
            return None

        # ✅ pick smallest first
        indexed_results.sort(key=len)

        result = indexed_results[0]

        for s in indexed_results[1:]:
            result = result & s

        if not result:
            return []

        return [self.db.get_node(ref) for ref in result]

    def _extract_simple_conditions(self, query):
        conditions = []

        for k, v in query.items():
            if k in ["and", "or", "not"]:
                continue

            # ✅ simple equality
            if not isinstance(v, dict):
                conditions.append((k, "eq", v))
            else:
                # ✅ operator extraction
                for op, val in v.items():
                    if op in ["gt", "lt", "gte", "lte"]:
                        conditions.append((k, op, val))

        if "and" in query:
            for sub in query["and"]:
                conditions.extend(self._extract_simple_conditions(sub))

        return conditions

    def _range_lookup(self, attr, op, value):
        """
        Scan index keys for range queries
        """
    
        data = self.db.generic_index._load()
    
        if attr not in data:
            return []
    
        matched_refs = []
    
        for key, refs in data[attr].items():
            try:
                key_val = float(key)
                val = float(value)
            except:
                continue
            
            if op == "gt" and key_val > val:
                matched_refs.extend(refs)
            elif op == "lt" and key_val < val:
                matched_refs.extend(refs)
            elif op == "gte" and key_val >= val:
                matched_refs.extend(refs)
            elif op == "lte" and key_val <= val:
                matched_refs.extend(refs)
    
        return matched_refs
    