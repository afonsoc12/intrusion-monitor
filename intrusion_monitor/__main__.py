import os
import sys
import logging
from datetime import date
from pathlib import Path

from ._version import get_versions
from .watchdog import Watchdog

# Environment variables and is required
ENVIRONMENT_VARS = {'TZ': False,
                    'API_KEY': True,
                    'INFLUXDB_HOST': False,
                    'INFLUXDB_PORT': False,
                    'INFLUXDB_DATABASE': False,
                    'INFLUXDB_USER': False,
                    'INFLUXDB_PASSWORD': False,
                    'OPERATION_MODE': False,
                    'SSH_LOG_PATH': False,
                    'LOG_LEVEL': False}


def main():

    # Setup logging
    logging_setup()

    logging.info(f'Copyright {date.today().year} Afonso Costa')
    logging.info('Licensed under the Apache License, Version 2.0 (the "License");')
    logging.info('Version: {}'.format(get_versions()['version']))

    # Unset empty variables
    unset_empty_env(ENVIRONMENT_VARS)

    # Check if required variables are present
    check_vars_exist(ENVIRONMENT_VARS)

    # Select if working as a TCP socket (for rsyslog) or as a log watchdog (default)
    OPERATION_MODE = os.getenv('OPERATION_MODE')
    if not OPERATION_MODE:
        logging.warning('OPERATION_MODE variable is not set. Defaulting to "watchdog"')
        OPERATION_MODE = 'watchdog'
    elif OPERATION_MODE.casefold() not in ('socket', 'watchdog'):
        logging.warning(f'OPERATION_MODE={OPERATION_MODE} is not recognised. Defaulting to "watchdog"')
        OPERATION_MODE = 'watchdog'
    else:
        logging.info(f'Using OPERATION_MODE={OPERATION_MODE}')

    if OPERATION_MODE == 'watchdog':

        log_path = Path(os.getenv('SSH_LOG_PATH', '/watchdog/log/auth.log'))

        # Check if file exists and can be read
        if not log_path.exists():
            logging.critical(f'No file was found and this can\'t continue. Log path provided is: {log_path.absolute()}')
            exit(127)
        elif not os.access(log_path, os.R_OK):
            logging.critical(f'The file cant be opened. Running: "sudo chmod o+r <Log file>" might solve this issue.')
            exit(128)
        else:
            logging.info(f'Log file found at: {log_path.absolute()}')
            with open(log_path, 'r') as f:
                lines = f.readlines()
                logging.debug('Here are the last 5 lines of the log file:\n\t{}'.format('\t'.join(lines[-5:])))

            # Everything seems okay, starting watchdog
            watchdog = Watchdog(log_path)
            logging.debug(f'So far so good, starting log Watchdog...')
            watchdog.start()
    elif OPERATION_MODE == 'socket':
        logging.critical(
            f'This feature is not yet implemented and this can\'t continue. OPERATION_MODE is {OPERATION_MODE}')
        raise NotImplementedError(f'The OPERATION_MODE={OPERATION_MODE} is not yet implemented.')
        # server.start()
    else:
        logging.critical(
            f'A critical problem occurred while handling OPERATION_MODE and this can\'t continue. OPERATION_MODE is {OPERATION_MODE}')
        raise EnvironmentError('A problem occurred while handling OPERATION_MODE environment variable.')

    exit(0)


def unset_empty_env(vars):
    """Unset empty environment variables."""

    for v in vars:
        var = os.getenv(v, None)
        if not var and var is not None and len(var) == 0:
            del os.environ[v]
            logging.warning(f'Environment variable {v} is set but is empty. Unsetted...')


def logging_setup():
    log_level = os.getenv('LOG_LEVEL', 'info')

    if log_level.casefold() == 'debug':
        log_level = logging.DEBUG
    elif log_level.casefold() == 'info':
        log_level = logging.INFO
    else:
        # Default
        log_level = logging.INFO

    logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=log_level)


def check_vars_exist(vars):
    """Checks if the required variables exist."""

    vars_missing = []
    for v in [v for v in vars if vars[v]]:
        var = os.getenv(v, None)
        if not var:
            logging.error(f'Environment variable {v} is not set and its mandatory!')
            vars_missing.append(v)

    if vars_missing:
        logging.critical(
            'Some mandatory environment variables are not set and this can\'t continue. Env variables missing: {}'.format(
                ', '.join(vars_missing)))
        raise EnvironmentError('Some mandatory environment variables are not set. Env variables missing: {}'.format(
            ', '.join(vars_missing)))


def exit(exit_code):
    if exit_code == 0:
        logging.info(f'Exiting with exit code {exit_code}')
    else:
        logging.error(f'Exiting with exit code {exit_code}')

    sys.exit(exit_code)


if __name__ == '__main__':

    try:
        main()
    except Exception as e:
        logging.critical('An exception occurred', exc_info=True)
        exit(250)
