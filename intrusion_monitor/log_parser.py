import os
import re
import logging
from datetime import datetime
import pytz

from .utils import extract_ip_info

TZ = pytz.timezone(os.getenv('TZ', 'Europe/London'))
TZ_UTC = pytz.utc

class LogLine:

    def __init__(self, log_line):
        self.log_line = log_line
        self.prefix, self.message = self._extract_log_parts()

    def _extract_log_parts(self):
        """Splits the line prefix from the message."""

        # Grabs PID within []
        reg_pid = re.compile(r'\[[\d+]*\]')

        pid_grp = reg_pid.findall(self.log_line)

        if len(pid_grp) != 1:
            logging.error(f'Error occurred while splitting the log. Split is {pid_grp}')
            logging.error(f'Log line: {self.log_line}')
            raise ValueError(f'Error occurred while splitting the log. Split is {pid_grp}')

        prefix, message = self.log_line.split(pid_grp[0]+': ')

        logging.debug(f'Log prefix extracted: {prefix}')
        logging.debug(f'Log prefix extracted: {message}')
        return prefix, message

    def is_login_attempt(self):
        """Check if the log line is considered a login attempt"""
        possibilities = ('Connection closed by', 'Failed password for', )

        status = [False, None]
        for p in possibilities:
            if self.message.startswith(p):
                status[0] = True
                status[1] = f'Matches {p}'
                break

        return status

    @property
    def process_id(self):
        """Extracts process ID from prefix."""

        # Grabs PID within []
        reg_pid = re.compile(r'\[[\d+]*\]')

        pid_grp = reg_pid.findall(self.log_line)[0]
        pid = int(pid_grp[1:-1])

        logging.debug(f'Process ID extracted: {pid}')
        return pid

    @property
    def process_name(self):
        """Extracts process name from prefix."""

        process_name = self.prefix.split(' ')[-1]
        logging.debug(f'Process name extracted: {process_name}')
        return process_name

    @property
    def hostname(self):
        """Extracts hostname from prefix."""
        hostname = self.prefix.split(' ')[-2]
        logging.debug(f'Hostname extracted: {hostname}')
        return hostname

    @property
    def timestamp(self):
        """Extracts datetime from log in UTC.

        Converts from TZ env variable timezone to UTC. If TZ is not specified, defaults to Europe/London.
        """

        ts_fmt = '%b %d %H:%M:%S'
        try:
            ts_str = ' '.join(self.prefix.split(' ')[:-2])
            logging.debug(f'Trying to infer format {ts_fmt} from this log portion: {ts_str} in TZ {TZ.zone}')
            timestamp = datetime.strptime(ts_str, ts_fmt).replace(year=datetime.now().year) #System's timezone (defined in env)
        except ValueError:
            logging.error(f'Could not infer timestamp. Returning None')
            return None

        logging.debug(f'Overriding log year to {datetime.now().year}')
        timestamp = TZ.localize(timestamp.replace(year=datetime.now().year))

        logging.debug(f'Converting timestamp from {timestamp.tzname()} to UTC')
        timestamp_utc = timestamp.astimezone(TZ_UTC)

        logging.debug('Timestamp extracted: {}. Timestamp in UTC: {}'.format(timestamp.strftime('%Y-%m-%dT%H:%M:%S %Z%z'),
                                                                             timestamp_utc.strftime('%Y-%m-%dT%H:%M:%S %Z%z')))
        return timestamp_utc

    @property
    def attempt_ip(self):
        """Extracts the IP of the SSH intruder."""
        reg_ip = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
        ips = re.findall(reg_ip, self.message)

        if len(ips) == 0:
            logging.error('No IPs found on this log line')
            ips = None
        elif len(ips) > 1:
            logging.warning('Multiple IPs found on this log line. Only keeping the first: {}'.format(', '.join(ips)))

        ips = ips[0]

        logging.debug(f'IP extracted: {ips}')
        return ips

    @property
    def attempt_port(self):
        """Extracts the port number."""

        ip = self.attempt_ip

        if not ip:
            logging.error('IP was not found in this line, so I cannot determine the port. Returning None')
            return None
        # Port is the imediate sequence after ip, e.g.: 192.168.1.3 port 1234
        try:
            logging.debug(f'Processing the part after the IP...')

            port_str = self.message.split(ip)[-1]
            logging.debug(port_str)

            port_str = port_str.split('port ')[-1]
            logging.debug('Splitting port str 1: {}'.format(port_str.replace('\n', '')))

            port_str = port_str.split(' ')[0]
            logging.debug('Splitting port str 2: {}'.format(port_str.replace('\n', '')))

            port = int(port_str)

        except Exception:
            logging.error(f'Could not infer port. Returning None')
            return None

        logging.debug(f'Port extracted: {port}')
        return port

    @property
    def attempt_username(self):
        """Extracts username.

        So far, I have found 4 types of logs when there is a failed attempt:

        With password authentication on:
            Case: When user exists but password is wrong
                - "Failed password for root (...)"
            Case: When user does not exist
                - "Failed password for invalid user postgres (...)"

        With only pubkey authentication (and root login disabled in sshd)
            Case: Connection rejected because password was sent (?)
                - "Connection closed by invalid user baa (...)"
            Case: Connection rejected because sshd does not allow login with root
                - "Connection closed by authenticating user root (...)"

        In all case, the username is always preceeded by either 'for' or 'user'
        """

        possibilities = ['Failed password for invalid user ', # This one must be tested first, otherwise it isnt caught by the next one
                         'Failed password for ',
                         'Connection closed by invalid user ',
                         'Connection closed by authenticating user '
                         ]

        is_found = False

        for p in possibilities:
            suffix_p = self.message.split(p)
            if len(suffix_p) == 1:
                logging.debug(f'No matches for username prefix: "{p}"')
            else:
                logging.debug(f'Found match for username prefix: "{p}"')
                username = suffix_p[-1].split(' ')[0]
                is_found = True
                break

        if not is_found:
            logging.error(f'No more prefix attempts. Could not infer username. Returning None')
            return None

        logging.debug(f'Username extracted: {username}')
        return username

    def get_ip_info(self):
        return extract_ip_info(self.attempt_ip)
