#!/usr/bin/env python

from commands import *
import requests
from requests.exceptions import SSLError, ConnectionError


def main():
    top_parser = create_cmd_parsers()

    # Quick help
    if len(sys.argv) == 1:
        top_parser.print_help()
        sys.exit(0)

    main_args = top_parser.parse_args()

    # Additional argument parsing that argparse can't handle

    if (main_args.cert and not main_args.key) or (main_args.key and not main_args.cert):
        top_parser.error("--cert and --key are both required together.")

    try:

        # Run function mapped to the selected sub-command
        main_args.func(main_args)

    except SSLError as se:
        print "SSL Error: %s" % main_args.url
        sys.exit(1)

    except ConnectionError as ce:
        print "Connection refused: %s" % main_args.url
        sys.exit(1)

    except aptly_api.AptlyApiError as apte:
        if apte.value == requests.codes.UNAUTHORIZED:
            print 'Unauthorized! %s ' % apte.msg
        elif apte.value == requests.codes.NOT_FOUND:
            print 'Not Found! %s ' % apte.msg
        else:
            print apte.msg
        sys.exit(1)

    except aptly_api.RaptlyError as rapte:
        print rapte.value
        sys.exit(1)

    except Exception as e:
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print message
        raise


if __name__ == "__main__":
    main()
