class Encoder:
    def __init__(self, string_table, number_table, array_table):
        self.string_table = string_table
        self.number_table = number_table
        self.array_table = array_table

    def encode_value(self, value):
        if isinstance(value, str):
            vid = self.string_table.get_or_create(value)
            return ("str", vid)

        elif isinstance(value, (int, float)):
            vid = self.number_table.get_or_create(value)
            return ("num", vid)

        elif isinstance(value, list):
            encoded = tuple(self.encode_value(v) for v in value)
            vid = self.array_table.get_or_create(encoded)
            return ("arr", vid)

        elif isinstance(value, dict):
            raise Exception("Nested dicts not supported yet")

        else:
            raise Exception(f"Unsupported type: {type(value)}")

    def encode_object(self, obj: dict):
        encoded = {}

        for key, value in obj.items():
            key_id = self.string_table.get_or_create(key)
            encoded[key_id] = self.encode_value(value)

        return encoded
