def get_children(db, parent_refno):
    """
    Return all direct children of a node
    """
    result = []

    for node in db.list_nodes():
        if node.attributes.get("parent") == parent_refno:
            result.append(node)

    return result


def get_parent(db, refno):
    node = db.get_node(refno)
    if not node:
        return None

    parent_ref = node.attributes.get("parent")
    if not parent_ref:
        return None

    return db.get_node(parent_ref)


def get_subtree(db, parent_refno):
    """
    Recursively fetch all descendants
    """
    result = []

    def dfs(current):
        children = get_children(db, current)
        for c in children:
            result.append(c)
            dfs(c.refno)

    dfs(parent_refno)
    return result