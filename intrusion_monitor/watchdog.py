import logging
import time
import os

from .db import InfluxDB
from .log_parser import LogLine

SLEEP_SECONDS = 1


class Watchdog:

    def __init__(self, log_path):
        self.log_path = log_path
        self.db = InfluxDB()

    def start(self):

        logging.debug('Checking connection status...')
        status = self.db.check_status()
        if status:
            logging.debug(f'Got connection successfully. InfluxDB version {status}')
        else:
            logging.error('Connection timmed out')
            raise ConnectionError('Could not connect. Connection timed out')

        # Start watching logs
        with open(self.log_path, 'r') as log_file:
            logging.debug(f'Opened context manager for file {self.log_path}')
            for new_lines in self.line_watcher(log_file):
                logging.debug(f'Processing the lines found...')
                new_lines = self.filter_lines(new_lines)
                logging.debug(f'\t> Processed lines: {new_lines}')

                for line in new_lines:
                    log_line = LogLine(line)
                    line_class = log_line.is_login_attempt()
                    if line_class[0]:
                        logging.debug(f'Line is a login attempt. Reason: {line_class[1]}. Going to be processed...')
                        ip_info = log_line.get_ip_info()
                        stored_data = self.db.write_log_line(log_line, ip_info)
                        logging.info(f'Log line successfully written: {stored_data}')
                    else:
                        logging.debug(f'Line is not a login attempt. Reason: {line_class[1]}. Skipping...')

        logging.debug(f'Closed context manager to {self.log_path}')
        logging.info(f'Watchdog has stopped')

    def line_watcher(self, file):
        """Generator function that returns the new line entered."""

        file.seek(0, os.SEEK_END)

        while True:
            # Reads last line
            new_lines = file.readlines()
            # sleep if file hasn't been updated
            if not new_lines:
                logging.debug(f'No new lines. Sleeping {SLEEP_SECONDS}')
                time.sleep(SLEEP_SECONDS)
                continue
            logging.debug('New line(s) found!')

            for l in new_lines:
                logging.debug('\t> {}'.format(l.replace('\n', '')))

            yield new_lines

    def filter_lines(self, lines):
        """Filters the log lines to only return the ones that have actual values."""
        return [l for l in lines if l != '\n' and len(l) > 1]
