import os
import sys
import yaml
import yoci_config
import logging
import logging.config

DEFAULT_BASE_LOGGING_LEVEL = logging.INFO
DEFAULT_VERBOSE_LOGGING_LEVEL = logging.DEBUG

DEFAULT_CONFIG_FILE = 'config.yml'


def init_logger(base_level=DEFAULT_BASE_LOGGING_LEVEL,
                verbose_level=DEFAULT_VERBOSE_LOGGING_LEVEL,
                logging_config=None):
    """initializes a base logger

    you can use this to init a logger in any of your files.
    this will use config.py's LOGGER param and logging.dictConfig to configure
    the logger for you.

    :param int|logging.LEVEL base_level: desired base logging level
    :param int|logging.LEVEL verbose_level: desired verbose logging level
    :param dict logging_dict: dictConfig based configuration.
     used to override the default configuration from config.py
    :rtype: `python logger`
    """
    if logging_config is None:
        logging_config = {}
    logging_config = logging_config or yoci_config.LOGGER
    # TODO: (IMPRV) only perform file related actions if file handler is
    # TODO: (IMPRV) defined.

    log_dir = os.path.expanduser(
        os.path.dirname(
            yoci_config.LOGGER['handlers']['file']['filename']))
    if os.path.isfile(log_dir):
        sys.exit('file {0} exists - log directory cannot be created '
                 'there. please remove the file and try again.'
                 .format(log_dir))
    try:
        logfile = yoci_config.LOGGER['handlers']['file']['filename']
        d = os.path.dirname(logfile)
        if not os.path.exists(d) and not len(d) == 0:
            os.makedirs(d)
        logging.config.dictConfig(logging_config)
        lgr = logging.getLogger('user')
        # lgr.setLevel(base_level) if not feeder_config.VERBOSE \
        lgr.setLevel(base_level)
        return lgr
    except ValueError as e:
        sys.exit('could not initialize logger.'
                 ' verify your logger config'
                 ' and permissions to write to {0} ({1})'
                 .format(logfile, e))


lgr = init_logger()


def import_config(config_file):
    """returns a configuration object

    :param string config_file: path to config file
    """
    # get config file path
    config_file = config_file or os.path.join(os.getcwd(), DEFAULT_CONFIG_FILE)
    lgr.debug('config file is: {}'.format(config_file))
    # append to path for importing
    # sys.path.append(os.path.dirname(config_file))
    try:
        lgr.debug('importing dict...')
        with open(config_file, 'r') as c:
            return yaml.safe_load(c.read())
    # TODO: (IMPRV) remove from path after importing
    except IOError as ex:
        lgr.error(str(ex))
        raise RuntimeError('cannot access config file')
    except ImportError:
        lgr.warning('config file not found: {}.'.format(config_file))
        raise RuntimeError('missing config file')
    except SyntaxError:
        lgr.error('config file syntax is malformatted. please fix '
                  'any syntax errors you might have and try again.')
        raise RuntimeError('bad config file')
