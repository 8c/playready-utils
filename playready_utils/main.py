from playready_utils.license.main import XMRLicense
from playready_utils.prd import PRD
from playready_utils.bcert import CHAIN
from playready_utils.pssh import PSSH

from pathlib import Path

import collections
import coloredlogs
import logging
import cloup
import os

# Monkey-patch Sequence for Python 3.10+
try:
    collections.Sequence
except AttributeError:
    import collections.abc

    collections.Sequence = collections.abc.Sequence

LOG_FORMAT_CLI = "{asctime} - {levelname} - {name} - {message}"
LOG_FORMAT_FILE = "{asctime} [{levelname}] {name}: {message}"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_STYLE = "{"


@cloup.group(invoke_without_command=True,
             context_settings={
                 "help_option_names": ["-h", "--help"],
                 "max_content_width": 116,  # max PEP8 line-width, -4 to adjust for initial indent
             },
             )
@cloup.option("--debug", type=bool, is_flag=True, default=False, help="Sets logging to debug")
def cli(debug):
    """Tools built to work with playready"""
    global logger
    logging.basicConfig(
        level=logging.DEBUG,
        format=LOG_FORMAT_FILE,
        datefmt=LOG_DATE_FORMAT,
        style=LOG_STYLE,
        handlers=[
        ],
    )

    coloredlogs.install(
        level=logging.DEBUG if debug else logging.INFO,
        fmt=LOG_FORMAT_CLI,
        datefmt=LOG_DATE_FORMAT,
        style=LOG_STYLE,
        handlers=[logging.StreamHandler()],
        field_styles={
            "asctime": {"color": 244},
            "levelname": {"color": 248},
            "name": {"color": 81},
        },
        level_styles={
            "debug": {"color": 244},
            "verbose": {"color": 246},
            "warning": {"color": "yellow"},
            "error": {"color": "red"},
            "critical": {"color": "red", "bold": True},
        },
    )

    logger = logging.getLogger("playready-utils")
    logger.info("Tools built to work with playready.")


@cli.command("load")
@cloup.argument('prd', type=Path, required=True, help="pyplayready PRD")
def load(prd):
    if not prd.is_file():
        logger.error("File does not exist")
        return

    prd_name = prd.name.replace(prd.suffix, "")

    logger.info(f"Loading file: {prd_name}")

    with open(prd, "rb") as f:
        prd_raw = f.read()
    data = PRD.parse(prd_raw)

    print(data)


@cli.command("migrate")
@cloup.argument('prd', type=Path, required=True, help="pyplayready PRD")
@cloup.option('--output', '-o', type=Path, required=False, help="Output to store the PRD")
def migrate(prd, output):
    """Converts a V2 PRD to V3 (Won't work with reprovisioning)"""
    if not prd.is_file():
        logger.error("File does not exist")
        return

    prd_name = prd.name.replace(prd.suffix, "")
    output = output or prd.parent

    logger.info(f"Loading file: {prd_name}")

    with open(prd, "rb") as f:
        prd_raw = f.read()
    data = PRD.parse(prd_raw)

    if data.version == 3:
        logger.error("PRD is Already V3. Exiting")
        return
    logger.info("Updating PRD to v3.")
    logger.info("Since a V2 PRD does not contain the group key filling with padded data")

    new_prd = PRD.build(
        {
            "constant": b"PRD",
            "version": 3,
            "prd": {
                "group_key": b"0" * 96,
                "encryption_key": data.prd.encryption_key,
                "signing_key": data.prd.signing_key,
                "group_certificate_length": data.prd.group_certificate_length,
                "group_certificate": data.prd.group_certificate
            }
        }
    )

    logger.info("Created V3 PRD")

    logger.info(f"Storing PRD in {output}\\{prd_name}_v3.prd")

    if not os.path.exists(output):
        logger.info(f"Created Directory {output}")
        os.makedirs(output)

    with open(f'{output}/{prd_name}_v3.prd', "wb") as f:
        f.write(new_prd)

    logger.info("Stored successfully")


@cli.command("export")
@cloup.argument('prd', type=Path, required=True, help="pyplayready PRD")
@cloup.option('--output', '-o', type=Path, required=False, help="Output to store the PRD")
def export(prd, output):
    """Exports a PRD V3 to bgroupcert and zgpriv"""
    if not prd.is_file():
        logger.error("File does not exist")
        return

    prd_name = prd.name.replace(prd.suffix, "")
    output = output or prd.parent

    logger.info(f"Loading file: {prd_name}")

    with open(prd, "rb") as f:
        prd_raw = f.read()
    data = PRD.parse(prd_raw)

    logger.info("Attempting to export as bgroupcert.dat and zgpriv.dat")

    if data.version != 3:
        logger.error("PRD is not V3. Exiting")
        return

    bgroupcert = data.prd.group_certificate

    zgpriv = data.prd.group_key

    if zgpriv == b"0" * 96:
        logger.error("Group Key is filled with dummy data, unable to extract.")
        return

    logger.info("Found bgroupcert and zgpriv")

    cert_chain = CHAIN.parse(bgroupcert)

    if cert_chain.certs != 4:
        logger.error("Invalid amount of certificates. Failing.")
        return

    unprovisioned_cert = {
        'constant': b'CHAI',
        'version': cert_chain.version,
        'total_length': cert_chain.total_length - cert_chain.data[0]['total_length'],
        'flags': cert_chain.flags,
        'certs': cert_chain.certs - 1,
        'data': [
            dict(cert_chain.data[len(cert_chain.data) - 3]),
            dict(cert_chain.data[len(cert_chain.data) - 2]),
            dict(cert_chain.data[len(cert_chain.data) - 1])
        ]
    }

    logger.info(f"Exporting bgroupcert.dat into {output}\\bgroupcert.dat")

    if not os.path.exists(output):
        logger.info(f"Created Directory {output}")
        os.makedirs(output)

    with open(f'{output}/bgroupcert.dat', 'wb') as f:
        f.write(CHAIN.build(unprovisioned_cert))

    logger.info(f'Exporting zgpriv.dat into {output}\\zgpriv.dat')

    with open(f'{output}/zgpriv.dat', 'wb') as f:
        f.write(zgpriv[:32])


@cli.command("downgrade")
@cloup.argument('prd', type=Path, required=True, help="pyplayready PRD")
@cloup.option('--output', '-o', type=Path, required=False, help="Output to store the PRD")
def downgrade(prd, output):
    """Downgrades a V3 PRD to V2"""
    if not prd.is_file():
        logger.error("File does not exist")
        return

    prd_name = prd.name.replace(prd.suffix, "")
    output = output or prd.parent

    logger.info(f"Loading file: {prd_name}")

    with open(prd, "rb") as f:
        prd_raw = f.read()

    data = PRD.parse(prd_raw)

    logger.info("Attempting to Downgrade PRD")

    if data.version != 3:
        logger.error("PRD is not V3. Exiting")
        return

    new_prd = PRD.build(
        {
            "constant": b"PRD",
            "version": 2,
            "prd": {
                "group_certificate_length": data.prd.group_certificate_length,
                "group_certificate": data.prd.group_certificate,
                "encryption_key": data.prd.encryption_key,
                "signing_key": data.prd.signing_key

            }
        }
    )

    logger.info("Created V2 PRD")

    logger.info(f"Storing PRD in {output}\\{prd_name}_v2.prd")

    if not os.path.exists(output):
        logger.info(f"Created Directory {output}")
        os.makedirs(output)

    with open(f'{output}/{prd_name}_v2.prd', "wb") as f:
        f.write(new_prd)

    logger.info("Stored successfully")


@cli.command("pssh")
@cloup.argument('pssh_data', type=str, required=True, help="Base64 PSSH")
def pssh(pssh_data):
    """Load a PSSH and extract the KID/s"""
    try:
        _pssh = PSSH(pssh_data)

        logger.info("Loaded PSSH")
        logger.info(f"Version: {_pssh.version}")
        logger.info(f"Found {len(_pssh.kid_list)} KID/s")
        for idx, kid in enumerate(_pssh.kid_list):
            logger.info(f"KID {idx}: Hex: {kid['value_hex']} - Base64: {kid['value_base64']}")
    except Exception as e:
        logger.error(f"Failed to load PSSH: {str(e)}")
        return


@cli.command("license")
@cloup.argument('xmr_data', type=str, required=True, help="XMR data from a License Response as Base64")
def license(xmr_data):
    """Parse a Playready XMR License Response"""
    try:
        logger.info("Parsing License Response")
        XMRLicense.parse(xmr_data)

    except Exception as e:
        logger.error(f"Failed to load XMR License: {str(e)}")
        return


@cli.command("unprovision")
@cloup.argument('bgroupcert', type=Path, required=True, help="provisioned bgroupcert.dat")
@cloup.option('--output', '-o', type=Path, required=False, help="Output to store the unprovisioned device")
def unprovision(bgroupcert, output):
    """Takes a bgroupcert.dat with 4 or more certificates and removes the leaf certificate and exports."""
    if not bgroupcert.is_file():
        logger.error("File does not exist")
        return

    bgroup = bgroupcert.name.replace(bgroupcert.suffix, "")
    output = output or bgroupcert.parent

    logger.info(f"Loading file: {bgroup}")

    with open(bgroupcert, "rb") as f:
        bgroupcert_raw = f.read()
    cert_chain = CHAIN.parse(bgroupcert_raw)

    if cert_chain.certs <= 3:
        logger.error("bgroupcert is not provisioned. Exiting")
        return

    unprovisioned_cert = {
        'constant': b'CHAI',
        'version': cert_chain.version,
        'total_length': cert_chain.total_length - cert_chain.data[0]['total_length'],
        'flags': cert_chain.flags,
        'certs': 3,
        'data': [
            dict(cert_chain.data[len(cert_chain.data) - 3]),
            dict(cert_chain.data[len(cert_chain.data) - 2]),
            dict(cert_chain.data[len(cert_chain.data) - 1])
        ]
    }

    logger.info(f"Exporting bgroupcert.dat into {output}\\bgroupcert.dat")

    if not os.path.exists(output):
        logger.info(f"Created Directory {output}")
        os.makedirs(output)

    with open(f'{output}/bgroupcert.dat', 'wb') as f:
        f.write(CHAIN.build(unprovisioned_cert))


if __name__ == "__main__":
    cli()
