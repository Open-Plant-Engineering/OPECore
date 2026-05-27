class BTreePage:
    def __init__(self, is_leaf: bool):
        self.is_leaf = is_leaf
        self.keys = []

        if is_leaf:
            self.values = []
        else:
            self.children = []