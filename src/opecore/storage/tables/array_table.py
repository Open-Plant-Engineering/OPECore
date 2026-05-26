class ArrayTable:
    def __init__(self, id_gen):
        self.id_gen = id_gen
        self.value_to_id = {}
        self.id_to_value = {}

    def get_or_create(self, value_tuple):
        if value_tuple in self.value_to_id:
            return self.value_to_id[value_tuple]

        new_id = self.id_gen.generate()
        self.value_to_id[value_tuple] = new_id
        self.id_to_value[new_id] = value_tuple

        return new_id

    def get(self, value_id):
        return self.id_to_value.get(value_id)
