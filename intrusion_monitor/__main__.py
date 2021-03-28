import os
import sys
import logging
from datetime import date
from pathlib import Path

import server
from log_parser import LogLine
from watchdog import Watchdog

logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)


def main():

    logging.info(f'Copyright {date.today().year} Afonso Costa')
    logging.info('Licensed under the Apache License, Version 2.0 (the "License");')

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
        #todo: check if has opening permissions
        log_path = Path('test.log')
        if not log_path.exists():
            logging.critical(f'No file was found and this can\'t continue. Log path provided is: {log_path}')
            exit(127)
        else:
            logging.debug(f'Log file found at: {log_path}')
            watchdog = Watchdog(log_path)
            watchdog.start()
    elif OPERATION_MODE == 'socket':
        server.start()
    else:
        logging.critical(f'A critical problem occurred while handling OPERATION_MODE and this can\'t continue. OPERATION_MODE is {OPERATION_MODE}')
        raise EnvironmentError('A problem occurred while handling OPERATION_MODE environment variable.')

    exit(0)

    # for l in lines:
    #     l = l.replace('\n', ' ')
    #
    #     logging.debug(f'============================================================')
    #     logging.debug(f'New log line received!: {l}')
    #     if len(l) > 1:
    #
    #         log_line = LogLine(l)
    #         print('message ', log_line.message)
    #         print('hostname ', log_line.hostname)
    #         print('timestamp ', log_line.timestamp)
    #         print('attempt_ip ', log_line.attempt_ip)
    #         print('attempt_port ', log_line.attempt_port)
    #         print('attempt_username ', log_line.attempt_username)
    #         print('process_id ', log_line.process_id)
    #         print('process_name ', log_line.process_name)
    #
    #     else:
    #         logging.warning(f'Log line discarded: Size is {len(l)} (<=1)')



def exit(exit_code):
    if exit_code == 0:
        logging.info(f'Exiting with exit code {exit_code}')
    else:
        logging.error(f'Exiting with exit code {exit_code}')

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
