import logging
import os
import signal
from contextlib import contextmanager
from datetime import datetime

from influxdb import InfluxDBClient

from .log_line import LogLine

INFLUXDB_HOST = os.getenv("INFLUXDB_HOST", "localhost")
INFLUXDB_PORT = os.getenv("INFLUXDB_PORT", "8086")
INFLUXDB_DATABASE = os.getenv("INFLUXDB_DATABASE", "intrusion_monitor")
INFLUXDB_USER = os.getenv("INFLUXDB_USER")
INFLUXDB_PASSWORD = os.getenv("INFLUXDB_PASSWORD")


class InfluxDB:
    def __init__(self):
        logging.debug("Creating InfluxDB client instance...")
        self.conn = InfluxDBClient(
            host=INFLUXDB_HOST,
            port=INFLUXDB_PORT,
            database=INFLUXDB_DATABASE,
            username=INFLUXDB_USER,
            password=INFLUXDB_PASSWORD,
        )
        try:
            ver = self.check_status()
            logging.info(f"InfluxDB version: {ver}")
        except TimeoutError:
            err = "Unable to gather InfluxDB version due to a timeout"
            logging.error(err)

        # This is safe to use, even if DB exists
        self.conn.create_database(INFLUXDB_DATABASE)

    def check_status(self):
        """Checks the status of a connection.

        Since the ping() of influxDB may return if there is no valid connecton,
        this forces it to exit after 3 seconds."""

        wait = 3

        logging.debug(f"Attempting connection version. Timeout in {wait} seconds...")
        # Add a timeout block.
        with self.timeout(wait) as e:
            try:
                ver = self.conn.ping()
                logging.debug(f"Got InfluxDB version {ver}")
            except TimeoutError:
                logging.error(f"Function timed out after waiting {wait} seconds")
                raise
            except Exception as e:
                logging.error(f"InfluxDB returned an error: {e}")
                raise

        return ver

    def query_last_stored_ip_data(self, ip, time="1w"):
        q = f"select * from failed_logins where ip='{ip}' and time >  now() - {time} order by time desc limit 1;"

        res = list(self.conn.query(q))

        if len(res) > 0:
            res = res[0][0]

        else:
            # No results
            pass
        return 1

    def write_log_line(self, log_line: LogLine, ip_info: dict):

        #
        measure = {
            "measurement": "failed_logins",
            "tags": {
                "host": log_line.hostname,
                "log_process_name": log_line.process_name,
                "log_process_id": log_line.process_id,
                "log_line": log_line.log_line,
                "username": log_line.attempt_username,
                "port": log_line.attempt_port,
                "ip": log_line.attempt_ip,
            },
            "fields": {"success": 0},
        }

        # If ip_info available, extend tags
        if ip_info:
            measure["api_response"] = ip_info
            measure["tags"] = {**measure["tags"], **ip_info}

        log_line_timestamp = log_line.timestamp
        if log_line_timestamp and isinstance(log_line_timestamp, datetime):
            logging.debug("Setting timestamp, since it is available")
            measure["time"] = log_line_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")

        logging.debug(f"Generated measure to be inserted: {measure}")
        status = self.conn.write_points([measure])

        return status

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
        raise TimeoutError
