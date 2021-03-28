import logging
import time
import os

from log_parser import LogLine

SLEEP_SECONDS = 1


class Watchdog:

    def __init__(self, log_path):
        self.log_path = log_path

    def start(self):
        with open(self.log_path, 'r') as log_file:
            logging.debug(f'Opened context manager for file {self.log_path}')
            for new_lines in self.line_watcher(log_file):
                logging.debug(f'Processing the lines found...')
                new_lines = self.filter_lines(new_lines)
                logging.debug(f'\t> Processed lines: {new_lines}')

                for line in new_lines:
                    log_line = LogLine(line)

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
