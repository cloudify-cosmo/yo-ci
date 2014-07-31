import logging
from utils import import_config
from utils import init_logger
from utils import DEFAULT_CONFIG_FILE

import travis

lgr = init_logger()


def _set_global_verbosity_level(is_verbose_output=False):
    """sets the global verbosity level for console and the lgr logger.

    :param bool is_verbose_output: should be output be verbose
    """
    global verbose_output
    # TODO: (IMPRV) only raise exceptions in verbose mode
    verbose_output = is_verbose_output
    if verbose_output:
        lgr.setLevel(logging.DEBUG)
    else:
        lgr.setLevel(logging.INFO)
    # print 'level is: ' + str(lgr.getEffectiveLevel())


def call_yoci(config=None, ci=None, req_type=None, name=None, verbose=False):
    _set_global_verbosity_level(verbose)
    config = config if config else DEFAULT_CONFIG_FILE
    if not ci:
        ci = 'Travis'
    if not req_type:
        req_type = 'repos'
    ci_config = import_config(config)
    if ci.lower() == 'Travis'.lower():
        if hasattr(travis, req_type.title()):
            getattr(travis, req_type.title())(
                lgr, ci_config[ci.title()], id=name)
            # getattr(ci_instance, req_type)
        else:
            raise RuntimeError('type not found')
    else:
        raise RuntimeError('ci {} not supported'.format(ci))

# i = travis.Repo(lgr, id='cloudify-cosmo/cloudify-plugins-common')
# for job in i.last_build.jobs:
#     print job.log
