# I absolutely HATE the idea of PRD but for the sake of these tools we are going to support them
import construct

V2 = construct.Struct(
    "group_certificate_length" / construct.Int32ub,
    "group_certificate" / construct.Bytes(construct.this.group_certificate_length),
    "encryption_key" / construct.Bytes(96),
    "signing_key" / construct.Bytes(96),
)

V3 = construct.Struct(
    "group_key" / construct.Bytes(96),
    "encryption_key" / construct.Bytes(96),
    "signing_key" / construct.Bytes(96),
    "group_certificate_length" / construct.Int32ub,
    "group_certificate" / construct.Bytes(construct.this.group_certificate_length),
)

PRD = construct.Struct(
    "signature" / construct.Const(b"PRD"),
    "version" / construct.Int8ub,
    "prd" / construct.Switch(
        lambda ctx: ctx.version,
        {
            2: V2,
            3: V3
        }
    )
)