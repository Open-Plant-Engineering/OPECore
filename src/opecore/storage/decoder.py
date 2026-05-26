class Decoder:
    def __init__(self, string_table, number_table, array_table):
        self.string_table = string_table
        self.number_table = number_table
        self.array_table = array_table

    def decode_value(self, value):
        vtype, vid = value

        if vtype == "str":
            return self.string_table.get(vid)

        elif vtype == "num":
            return self.number_table.get(vid)

        elif vtype == "arr":
            arr = self.array_table.get(vid)
            return [self.decode_value(v) for v in arr]

        elif vtype == "ref":
            return vid

        else:
            raise Exception(f"Unknown type: {vtype}")

    def decode_object(self, obj: dict):
        decoded = {}

        for key_id, value in obj.items():
            key = self.string_table.get(key_id)
            decoded[key] = self.decode_value(value)

        return decoded
