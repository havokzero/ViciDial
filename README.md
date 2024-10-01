# ViciDial Exploit Suite

**Author**: Havok
**Project URL**: [ViciDial Exploit Suite](https://github.com/havokzero/ViciDial)

## Overview

The ViciDial Exploit Suite is a comprehensive toolset designed for penetration testers and security researchers targeting vulnerabilities in ViciDial installations. This suite leverages **SQL Injection (SQLi)** and **Remote Code Execution (RCE)** vulnerabilities to gain unauthorized access and execute commands. Additionally, the tool allows interaction with the **ViciDial API** for post-exploitation control after acquiring valid credentials.

## Features

- **SQL Injection (SQLi)**: Extract administrative credentials via time-based SQLi attacks.
- **Remote Code Execution (RCE)**: Execute remote shell commands on compromised ViciDial systems, with reverse shell capability.
- **ViciDial API Integration**: Authenticate to the ViciDial API using the extracted credentials, allowing further system control.

## Modules

### SQL Injection (SQLi)

The SQL Injection module exploits time-based SQLi to extract sensitive data, such as admin usernames and passwords. It works by enumerating credentials one character at a time, providing live feedback during the extraction process.

#### Example Output:
- [+] Target appears vulnerable to time-based SQL injection. 
- [-] Enumerating administrator credentials... 
- [-] Username: admin 
- [*] Password: Test@123 
- [+] SQLi successful: 
- [+]Username: admin, Password: Test@123


### Remote Code Execution (RCE)

The RCE module enables remote shell command execution on the compromised ViciDial server. It can also be used to launch a reverse shell, allowing full access to the server for post-exploitation activities. 

### ViciDial API Integration

After obtaining administrative credentials, the tool provides direct interaction with the ViciDial API. This allows users to:
- List campaigns
- Make API calls
- Retrieve server information
- (Maybe more will be added later)

## Installation

To set up the ViciDial Exploit Suite, follow these steps:

1. **Clone the repository**:

    ```bash
    git clone https://github.com/havokzero/ViciDial.git
    cd ViciDial
    ```

2. **Install the required dependencies**:

    Ensure `pip` is installed and run:

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the tool**:

    ```bash
    python main.py
    ```

## Usage

Once launched, the tool presents you with a menu where you can choose between SQLi, RCE, or API functionalities:

### SQL Injection (SQLi)

1. Select `[1]` for SQL Injection.
2. Provide the target ViciDial server URL.
3. Watch as the tool extracts admin credentials through time-based SQLi.

### Remote Code Execution (RCE)

1. Select `[2]` for Remote Code Execution.
2. Provide details such as the webserver host, port, and listener configuration.
3. Choose whether to launch a reverse shell or execute a command.

### Vicidial API Interaction

1. Once credentials are obtained, select `[3]` to use the Vicidial API.
2. You can retrieve server information, list campaigns, or initiate calls.

## Example Scenarios

### SQL Injection & API Interaction

1. Run the tool:

    ```bash
    python main.py
    ```

2. Choose the **SQL Injection** option (Option 1).
3. Enter the ViciDial server URL.
4. Once credentials are retrieved, select the **API** option (Option 3) to interact with the system.

### Remote Code Execution

1. Run the tool:

    ```bash
    python main.py
    ```

2. Select the **RCE** option (Option 2).
3. Provide the necessary webserver and listener details to launch a reverse shell or execute a command.

## Disclaimer

This tool is untested and intended for educational purposes only. The author is not responsible for any misuse of this software. Always ensure that you have explicit permission before running this tool on any systems.


### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
