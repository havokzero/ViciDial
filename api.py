import requests
from base64 import b64encode
import colorama
from colorama import Fore, Style


class VicidialAPI:
    def __init__(self, target_url, username, password):
        """
        Initialize API class with target URL, admin username, and password.
        """
        self.TARGET_URL = target_url
        self.USERNAME = username
        self.PASSWORD = password
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification for testing purposes

        self.auth_header = self._build_auth_header()
        self.request_headers = {"Authorization": self.auth_header}

    def _build_auth_header(self):
        """
        Build the authorization header for API requests.
        """
        credentials = f"{self.USERNAME}:{self.PASSWORD}"
        credentials_base64 = b64encode(credentials.encode()).decode()
        auth_header = f"Basic {credentials_base64}"
        return auth_header

    def custom_print(self, message: str, header: str) -> None:
        """
        Print messages with color-coded headers.
        """
        header_colors = {
            "+": Fore.GREEN, "-": Fore.RED, "!": Fore.YELLOW, "*": Fore.BLUE, "~": Fore.MAGENTA
        }
        print(header_colors.get(header, Fore.WHITE) + Style.BRIGHT + f"[{header}] {message}" + Style.RESET_ALL)

    def make_api_call(self, endpoint, method="GET", params=None, data=None):
        """
        Make an API call to a specified endpoint with better error handling.
        """
        try:
            url = f"{self.TARGET_URL}/{endpoint}"
            self.custom_print(f"Making {method} request to {url}", "*")

            if method == "GET":
                response = self.session.get(url, headers=self.request_headers, params=params)
            elif method == "POST":
                response = self.session.post(url, headers=self.request_headers, data=data)

            response.raise_for_status()

            # Attempt to parse JSON
            try:
                return response.json()  # Assuming the API returns JSON
            except ValueError:
                self.custom_print("Received a non-JSON response. Here is the raw content:", "~")
                self.custom_print(response.text, "~")
                return None

        except requests.exceptions.HTTPError as http_err:
            self.custom_print(f"HTTP error occurred: {http_err}", "-")
        except requests.exceptions.ConnectionError:
            self.custom_print("Connection error occurred. Please check the server's availability.", "-")
        except requests.exceptions.Timeout:
            self.custom_print("Request timed out. Consider increasing the timeout.", "-")
        except Exception as err:
            self.custom_print(f"An error occurred: {err}", "-")

        return None

    def get_server_info(self):
        """
        Example: Get server information or statistics.
        """
        endpoint = "vicidial/server_info"
        response = self.make_api_call(endpoint)

        if response:
            self.custom_print(f"Server Info: {response}", "+")
        else:
            self.custom_print("Failed to retrieve server info.", "-")

    def list_campaigns(self):
        """
        Example: List campaigns available on the server.
        """
        endpoint = "vicidial/list_campaigns"
        response = self.make_api_call(endpoint)

        if response:
            self.custom_print(f"Campaigns: {response}", "+")
        else:
            self.custom_print("Failed to retrieve campaigns.", "-")

    def make_call(self, phone_number, campaign_id):
        """
        Example: Initiate a call using the Vicidial API.
        """
        endpoint = "vicidial/make_call"
        data = {
            "phone_number": phone_number,
            "campaign_id": campaign_id
        }

        response = self.make_api_call(endpoint, method="POST", data=data)

        if response:
            self.custom_print(f"Call initiated: {response}", "+")
        else:
            self.custom_print("Failed to initiate call.", "-")


if __name__ == "__main__":
    # Example usage of the API class
    target_url = input(Fore.CYAN + Style.BRIGHT + "Enter the Vicidial Server URL: " + Style.RESET_ALL)
    username = input(Fore.CYAN + Style.BRIGHT + "Enter admin username: " + Style.RESET_ALL)
    password = input(Fore.CYAN + Style.BRIGHT + "Enter admin password: " + Style.RESET_ALL)

    api = VicidialAPI(target_url, username, password)

    # Example API calls
    api.get_server_info()
    api.list_campaigns()
    phone_number = input(Fore.CYAN + Style.BRIGHT + "Enter phone number to call: " + Style.RESET_ALL)
    campaign_id = input(Fore.CYAN + Style.BRIGHT + "Enter campaign ID: " + Style.RESET_ALL)
    api.make_call(phone_number, campaign_id)
