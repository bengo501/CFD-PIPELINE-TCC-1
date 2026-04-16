# permite python m cli a partir da pasta dsl com sys path correcto
import sys

from cli.app import dispatch_main

if __name__ == "__main__":
    sys.exit(dispatch_main())
