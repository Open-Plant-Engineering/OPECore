class Attr:
    NAME = 1
    OWNER = 2
    TYPE = 3
    PRESSURE = 4
    ACTIVE = 5
    DELETED = 999


ATTR_TYPES = {
    Attr.NAME: "str",
    Attr.OWNER: "str",
    Attr.TYPE: "str",
    Attr.PRESSURE: "num",
    Attr.ACTIVE: "bool",
    Attr.DELETED: "bool",
}

REQUIRED_ATTRS = {
    Attr.NAME,
    Attr.OWNER,
    Attr.TYPE
}