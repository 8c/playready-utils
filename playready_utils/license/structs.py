import construct

CONTENT_KEY = construct.Struct(
    'kid' / construct.Bytes(16),
    'keytype' / construct.Int16ub,
    'ciphertype' / construct.Int16ub,
    'length' /  construct.Int16ub,
    'value' / construct.Bytes(construct.this.length)
)

ECC_KEY = construct.Struct(
    'curve' / construct.Int16ub,
    'length' / construct.Int16ub,
    'value' / construct.Bytes(construct.this.length)
)

FTLV = construct.Struct(
    'flags' / construct.Int16ub,
    'type' / construct.Int16ub,
    'length' / construct.Int32ub,
    'value' / construct.Bytes(construct.this.length - 8)
)

AUXILIARY_LOCATIONS = construct.Struct(
    "location" / construct.Int32ub,
    'value' / construct.Bytes(16)
)

AUXILIARY_KEY_OBJECT = construct.Struct(
    'count' / construct.Int16ub,
    'locations' / construct.Array(
        construct.this.count,
        AUXILIARY_LOCATIONS
    )
)

SIGNATURE = construct.Struct(
    "type" / construct.Int16ub,
    "siglength" / construct.Int16ub,
    "signature" / construct.Bytes(construct.this.siglength)
)

XMR = construct.Struct(
    "constant" / construct.Const(b'XMR\00'),
    "offset" / construct.Int16ub,
    "version" / construct.Int16ub,
    "rightsid" / construct.Bytes(16),
    'data' / FTLV
)