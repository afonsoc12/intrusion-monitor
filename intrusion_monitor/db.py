import logging
import os
import signal
from asyncio.subprocess import Process
from contextlib import contextmanager
from datetime import datetime

from influxdb import InfluxDBClient

INFLUXDB_HOST = os.getenv('INFLUXDB_HOST', 'localhost')
INFLUXDB_PORT = os.getenv('INFLUXDB_PORT', '8086')
INFLUXDB_DATABASE = os.getenv('INFLUXDB_DATABASE', 'intrusion_monitor')
INFLUXDB_USER = os.getenv('INFLUXDB_USER')
INFLUXDB_PASSWORD = os.getenv('INFLUXDB_PASSWORD')

class InfluxDB:

    def __init__(self):
        logging.debug('Creating InfluxDB client instance...')
        self.conn = InfluxDBClient(host=INFLUXDB_HOST,
                                   port=INFLUXDB_PORT,
                                   database=INFLUXDB_DATABASE,
                                   username=INFLUXDB_USER,
                                   password=INFLUXDB_PASSWORD)
        if self.check_status():
            # This is safe to use, even if DB exists
            self.conn.create_database(INFLUXDB_DATABASE)

    def check_status(self):
        """Checks the status of a connection.

        Since the ping() of influxDB may return if there is no valid connecton,
        this forces it to exit after 2 seconds."""

        wait = 3

        logging.debug(f'Attempting connection version. Timeout in {wait} seconds...')
        # Add a timeout block.
        with self.timeout(wait) as e:
            try:
                ver = self.conn.ping()
                logging.debug(f'Got InfluxDB version {ver}')
            except TimeoutError:
                ver = None
                logging.error(f'Function timed out. Returning {ver}')
            except Exception:
                ver = None
                logging.error(f'InfluxDB returned an error. Returning {ver}')

        return ver



    def write_log_line(self, log_line, ip_info):
        if not ip_info:
            logging.debug('IP info is not available. Discarding')
            measure = [
                {
                    "measurement": "failed_logins",
                    "tags": {
                        "username": log_line.attempt_username,
                        "port": log_line.attempt_port,
                        "ip": log_line.attempt_ip
                    },
                    "fields": {
                        "value": 1
                    }
                }
            ]

        else:
            logging.debug('IP info is available')
            measure = [
                {
                    "measurement": "failed_logins",
                    "tags": {
                        "geohash": ip_info['geohash'],
                        "latitude": ip_info['latitude'],
                        "longitude": ip_info['longitude'],
                        "username": log_line.attempt_username,
                        "port": log_line.attempt_port,
                        "ip": log_line.attempt_ip,
                        'type': ip_info['type'],
                        'continent_code': ip_info['continent_code'],
                        'continent_name': ip_info['continent_name'],
                        'country_code': ip_info['country_code'],
                        'country_name': ip_info['country_name'],
                        'region_code': ip_info['region_code'],
                        'region_name': ip_info['region_name'],
                        'city': ip_info['city'],
                        'zip': ip_info['zip'],
                        'country_flag_emoji': ip_info['location']['country_flag_emoji'],
                        'capital': ip_info['location']['capital'],
                        'calling_code': ip_info['location']['calling_code'],
                        'is_eu': ip_info['location']['is_eu']
                    },
                    "fields": {
                        "value": 1
                    }
                }
            ]

        if log_line.timestamp and isinstance(log_line.timestamp, datetime):
            logging.debug('Setting timestamp, since it is available')
            measure[0]['time'] = log_line.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')

        self.conn.write_points(measure)

        return measure


    @staticmethod
    @contextmanager
    def timeout(time):
        """Context manager for timing out functions."""
        # Register a function to raise a TimeoutError on the signal.
        signal.signal(signal.SIGALRM, InfluxDB.raise_timeout)
        # Schedule the signal to be sent after ``time``.
        signal.alarm(time)

        try:
            yield
        except TimeoutError:
            pass
        finally:
            # Unregister the signal so it won't be triggered
            # if the timeout is not reached.
            signal.signal(signal.SIGALRM, signal.SIG_IGN)

    @staticmethod
    def raise_timeout(signum, frame):
        """Exception for context manager timeout."""
        raise TimeoutError('Functin timed out')

