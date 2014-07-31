# flake8: NOQA
"""Script to run feeder via command line

Usage:
    yo-ci get <ci> <type> [--config=<path> -v]
    yo-ci get <ci> <type> <name> [--config=<path> -v]
    yo-ci --version

Arguments:
    get                 Gets info for type

Options:
    -h --help                   Show this screen.
    -c --config=<path>          Path to generator config file.
    -w --ci=<string>     transport to use (e.g. File)
    -v --verbose                a LOT of output
    --version                   Display current version of yoci and exit

"""

from __future__ import absolute_import
from docopt import docopt
from yoci.yoci import init_logger
from yoci.yoci import _set_global_verbosity_level
from yoci.yoci import call_yoci

lgr = init_logger()


def ver_check():
    import pkg_resources
    version = None
    try:
        version = pkg_resources.get_distribution('yoci').version
    except Exception as e:
        print(e)
    finally:
        del pkg_resources
    return version


def yoci_run(o):
    print o
    if o['get']:
        call_yoci(config=o.get('--config'),
                  ci=o.get('<ci>'),
                  req_type=o.get('<type>'),
                  name=o.get('<name>'),
                  verbose=o.get('--verbose'))
    # elif o['get'] and o['<name>']:
    #     call_yoci(config=o.get('--config'),
    #               ci=o.get('<ci>'),
    #               req_type=o.get('<type>'),
    #               verbose=o.get('--verbose'))


def yoci(test_options=None):
    """Main entry point for script."""
    version = ver_check()
    options = test_options or docopt(__doc__, version=version)
    _set_global_verbosity_level(options.get('--verbose'))
    lgr.debug(options)
    yoci_run(options)


def main():
    yoci()


if __name__ == '__main__':
    main()
