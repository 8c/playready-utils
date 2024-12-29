import construct

CERT = construct.Struct(
    "constant" / construct.Const(b"CERT"),
    "version" / construct.Int32ub,
    "total_length" / construct.Int32ub,
    "certificate_length" / construct.Int32ub,
    "value" / construct.Bytes(construct.this.total_length - 16)
)

CHAIN = construct.Struct(
    "constant" / construct.Const(b"CHAI"),
    "version" / construct.Int32ub,
    "total_length" / construct.Int32ub,
    "flags" / construct.Int32ub,
    'certs' / construct.Int32ub,
    'data' / construct.Array(
        construct.this.certs,
        CERT
    )
)