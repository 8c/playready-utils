# playready-utils

playready-utils is a CLI of useful tools made to work with the public pyplayready CDM and corresponding files (PRD).

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install playready-utils.

```bash
pip install git+https://github.com/8c/playready-utils
```

## Usage

```
playready-tools -h
Usage: playready-utils [OPTIONS] COMMAND [ARGS]...                                                                                                                                                                          
                                                                                                             
  Tools built to work with playready

Options:
  --debug     Sets logging to debug
  -h, --help  Show this message and exit.

Commands:
  export   Exports a PRD V3 to bgroupcert and zgpriv
  license  Parse a Playready XMR License Response
  migrate  Converts a V2 PRD to V3 (Won't work with reprovisioning)
  pssh     Load a PSSH and extract the KID/s
  unprovision  Takes a bgroupcert.dat with 4 or more certificates and removes the leaf certificate and exports
```

## Disclaimer

1. This project does not condone piracy or any action against the terms of the DRM systems.
2. Unauthorized decryption or distribution of copyrighted materials is a violation of applicable laws and intellectual property rights.
3. The developers, contributors, and maintainers of this program are not responsible for any misuse or illegal activities performed using this software.
4. By using this program, you agree to comply with all applicable laws and regulations governing digital rights and copyright protections.

## License

[Creative Commons](https://github.com/8c/playready-utils/blob/master/LICENSE)
