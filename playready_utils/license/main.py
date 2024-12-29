from playready_utils.license.definitions import *
from playready_utils.license.structs import *

import logging
import base64

class XMRLicense:
    @staticmethod
    def parse(license):
        logger = logging.getLogger("license")
        if isinstance(license, str):
            license = base64.b64decode(license.encode())
        data = XMR.parse(license)
        logger.info('constant: {}'.format(data['constant']))
        logger.info('version: {}'.format(data['version']))
        logger.info('offset: {}'.format(data['offset']))
        logger.info('rights id: {}'.format(data['rightsid'].hex()))
        data = data['data']
        logger.info("\ttype: {}".format(XMRFORMAT(data['type']).name))
        logger.info("\tflags: {}".format(data['flags']))
        logger.info("\tlength: {}".format(data['length']))
        pos = 0

        while True:
            if pos >= data['length'] - 16:
                break
            obj = FTLV.parse(data['value'][pos:])
            logger.info('\t\tflags: {}'.format(obj['flags']))
            logger.info('\t\ttype: {}'.format(XMRFORMAT(obj['type']).name))
            logger.info('\t\tlength: {}'.format(obj['length']))
            logger.info('\t\tvalue: {}'.format(obj['value'].hex()))

            if XMRFORMAT(obj['type']) == XMRFORMAT.GLOBAL_POLICY_CONTAINER_ENTRY_TYPE:
                sum2 = 0
                while True: 
                    if sum2 >= obj['length'] - 16:
                        break
                    obj2 = FTLV.parse(obj['value'][sum2:])
                    logger.info('\t\t\tflags: {}'.format(obj2['flags']))
                    logger.info('\t\t\ttype: {}'.format(XMRFORMAT(obj2['type']).name))
                    logger.info('\t\t\tlength: {}'.format(obj2['length']))
                    logger.info('\t\t\tvalue: {}'.format(obj2['value'].hex()))
                    sum2 += obj2['length']

                    if XMRFORMAT(obj2['type']) == XMRFORMAT.REVOCATION_INFO_VERSION_ENTRY_TYPE:
                        logger.info('\t\t\tsequence: {}'.format(int(obj2['value'].hex(), 16)))

                    if XMRFORMAT(obj2['type']) == XMRFORMAT.SECURITY_LEVEL_ENTRY_TYPE:
                        logger.info('\t\t\tsecurity level: {}'.format(int(obj2['value'].hex(), 16)))

            if XMRFORMAT(obj['type']) == XMRFORMAT.KEY_MATERIAL_CONTAINER_ENTRY_TYPE:
                sum2 = 0
                while True: 
                    if sum2 >= obj['length'] - 16:
                        break
                    obj2 = FTLV.parse(obj['value'][sum2:])
                    logger.info('\t\t\tflags: {}'.format(obj2['flags']))
                    logger.info('\t\t\ttype: {}'.format(XMRFORMAT(obj2['type']).name))
                    logger.info('\t\t\tlength: {}'.format(obj2['length']))
                    logger.info('\t\t\tvalue: {}'.format(obj2['value'].hex()))

                    if XMRFORMAT(obj2['type']) == XMRFORMAT.CONTENT_KEY_ENTRY_TYPE:
                        contentkey =  CONTENT_KEY.parse(obj2['value'])
                        logger.info('\t\t\t\tkid: {}'.format(contentkey['kid'].hex()))
                        logger.info('\t\t\t\tkey type: {}'.format(contentkey['keytype']))
                        logger.info('\t\t\t\tciphertype: {}'.format(contentkey['ciphertype']))
                        logger.info('\t\t\t\tlength: {}'.format(contentkey['length']))
                        logger.info('\t\t\t\tvalue: {}'.format(contentkey['value'].hex()))

                    if XMRFORMAT(obj2['type']) == XMRFORMAT.DEVICE_KEY_ENTRY_TYPE:
                        ecckey = ECC_KEY.parse(obj2['value'])
                        logger.info('\t\t\t\tcurve: {}'.format(ecckey['curve']))
                        logger.info('\t\t\t\tkeylength: {}'.format(ecckey['length']))
                        logger.info('\t\t\t\tvalue: {}'.format(ecckey['value'].hex()))
                    
                    if XMRFORMAT(obj2['type']) == XMRFORMAT.AUX_KEY_ENTRY_TYPE:
                        aux_keys = AUXILIARY_KEY_OBJECT.parse(obj2['value'])
                        logger.info('\t\t\t\tauxiliary count: {}'.format(aux_keys['count']))
                        for location in aux_keys['locations']:
                            logger.info('\t\t\t\taux : {}'.format(location['location']))
                            logger.info('\t\t\t\taux location: {}'.format(location['value'].hex()))

                    sum2 += obj2['length']
            
            if XMRFORMAT(obj['type']) == XMRFORMAT.SIGNATURE_ENTRY_TYPE:
                signature = SIGNATURE.parse(obj["value"])
                logger.info('\t\t\t\tsignature type: {}'.format(signature['type']))
                logger.info('\t\t\t\tsignature length: {}'.format(obj["length"]))
                logger.info('\t\t\t\tsignature: {}'.format(signature['signature'].hex()))

            pos += obj['length']