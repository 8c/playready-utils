from uuid import UUID 

import construct
import xmltodict
import base64

PLAYREADY_OBJECT = construct.Struct(
    "type" / construct.Int16ul,
    "length" / construct.Int16ul,
    "header" / construct.GreedyString(encoding='utf-16')
)

PLAYREADY_HEADER = construct.Struct(
    "length" / construct.Int32ul,
    "count" / construct.Int16ul,
    "records" / construct.Array(
        construct.this.count,
        PLAYREADY_OBJECT
    )
)

PSSH_BOX = construct.Struct(
    "length" / construct.Int32ub,
    "pssh" / construct.Const(b"pssh"),
    "fullbox" / construct.Int32ub,
    "system_id" / construct.Bytes(16),
    "data_length" / construct.Int32ub,
    "data" / construct.Bytes(construct.this.data_length)
)

class PSSH:
    def __init__(self, pssh):
        if pssh.startswith("<WRM"): 
            self.WRMHEADER = xmltodict.parse(pssh)
        else: 
            if isinstance(pssh, str):
                pssh = base64.b64decode(pssh.encode("utf-8"))
            if pssh.startswith(b"<WRM"): 
                pssh = pssh.decode("utf-8")
                # pssh is just a wrm header
                self.WRMHEADER = xmltodict.parse(pssh)
            else:
                if isinstance(pssh, str):
                    pssh = base64.b64decode(pssh.encode("utf-8"))
                # assume that PSSH returned is a pssh box
                try:
                    pssh_box = PSSH_BOX.parse(pssh)
                    if pssh_box.system_id.hex() != "9a04f07998404286ab92e65be0885f95":
                        raise ValueError("Playready PSSH not parsed through")

                    parsed = PLAYREADY_HEADER.parse(pssh_box.data)
                except:
                    parsed = PLAYREADY_HEADER.parse(pssh)
                self.WRMHEADER = xmltodict.parse(parsed.records[0].header)

        self.version = self.WRMHEADER['WRMHEADER']['@version']

        if self.version == "4.0.0.0":
            kids = self.WRMHEADER['WRMHEADER']['DATA']['KID']
        if self.version == "4.1.0.0":
            kids = self.WRMHEADER['WRMHEADER']['DATA']['PROTECTINFO']['KID']['@VALUE']
        if self.version == "4.2.0.0" or self.version == "4.3.0.0":
            kids = self.WRMHEADER['WRMHEADER']['DATA']['PROTECTINFO']['KIDS']['KID']

        if isinstance(kids, dict):
            kids = [kids]

        self.kid_list = []

        for kid in kids:
            if isinstance(kid, dict):
                kid = kid['@VALUE']
            decoded_kid = base64.b64decode(kid.encode('utf-8'))
            
            self.kid_list.append({ "value_hex": UUID(bytes_le=decoded_kid).hex, "value_base64": kid})