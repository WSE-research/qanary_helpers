import threading
import time
import requests
import json
import logging
from requests.auth import HTTPBasicAuth


class Registrator(threading.Thread):
    """
    Class running as thread to contact the Spring Boot Admin Server
    """

    json_headers = {"Content-type": "application/json",
                    "Accept": "application/json"}

    def __init__(self, admin_server_url, admin_server_user, admin_server_password, registration, interval=10):
        """
        registration = None  # passed dict containing relevant information
        interval = None  # in seconds
        """
        threading.Thread.__init__(self)
        self.admin_server_url = admin_server_url + "/instances"
        self.admin_server_user = admin_server_user
        self.admin_server_password = admin_server_password
        self.registration = registration
        self.interval = interval
        self._stop_event = threading.Event()
        logging.basicConfig(level=logging.DEBUG)

    def run(self):
        while not self.is_stopped():
            self.call_admin_server()
            time.sleep(self.interval)

    def stop(self):
        self._stop_event.set()

    def is_stopped(self):
        return self._stop_event.is_set()

    def call_admin_server(self):
        try:
            # prepare POST request data (None values should not been send)
            request_data = {k: v for k, v in vars(self.registration).items() if v is not None}
            response = requests.post(
                url=self.admin_server_url, headers=self.json_headers,
                data=json.dumps(request_data), auth=HTTPBasicAuth(self.admin_server_user, self.admin_server_password)
            )
            if response:
                logging.debug("registration: ok on %s (%d)" %
                              (self.admin_server_url, response.status_code))
            else:
                logging.warning("registration: failed at %s with HTTP status code %d" % (
                    self.admin_server_url, response.status_code))
        except Exception as e:
            logging.warning("registration: failed at %s with exception \"%s\"" % (
                self.admin_server_url, e))
