class Reference:
    TYPE = "ref"

    @staticmethod
    def create(object_id: int):
        return (Reference.TYPE, object_id)

    @staticmethod
    def resolve(value):
        return value[1]