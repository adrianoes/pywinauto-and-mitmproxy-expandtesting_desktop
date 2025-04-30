import pytest
from pywinauto import Application
import time
import psutil
import json
import os
import glob
import subprocess
from faker import Faker

from faker import Faker
from tests.support import create_user, delete_json_output_file, delete_json_test_data_file, delete_user, login_user, terminate_cmder_process_tree, write_json_test_data_file


def test_login_user_server_error():
    # Start random data number
    randomData = Faker().hexify(text='^^^^^^^^^^^^')

    # Start Cmder
    cmder_path = r'Cmder.exe'        
    app = Application().start(cmder_path, create_new_console=True, wait_for_idle=False)
    time.sleep(10)

    # Find the process ID of ConEmu
    def find_conemu_pid():
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'ConEmu64.exe':
                return proc.info['pid']
        return None

    pid = find_conemu_pid()
    app = Application().connect(process=pid)
    time.sleep(2)
    terminal_window = app.window(title_re=".*Cmder.*")
    terminal_window.wait('visible', timeout=15)
    terminal_window.maximize()

    # Define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, f'output-{randomData}.json'))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    # Create user (we'll assume this function works as expected)
    create_user(terminal_window, output_file, test_data_file)

    # Load test data for login
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Extract the user data from the test data file
    user_email = test_data.get("user_email")
    user_password = test_data.get("user_password")  # We read user_password even if not used yet

    # cURL command to login the user and save the response in the 'resources' folder
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # Define the endpoint to mock (login endpoint)
    login_endpoint = "https://practice.expandtesting.com/notes/api/users/login"

    # Start mitmproxy in the background with the mock script and pass the login endpoint
    mitm_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mock_500.py'))
    mitmproxy_proc = subprocess.Popen(
        ['mitmdump', '-s', mitm_script, '--listen-port', '8080', '--', login_endpoint],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("MITMProxy started.")
    time.sleep(5)  # Give it time to initialize

    login_curl_command = f'curl -x http://127.0.0.1:8080 -k -X "POST" "{login_endpoint}" ' \
                     f'-H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" ' \
                     f'-d "email={user_email}&password={user_password}" > "{output_file}"'

    # Send the cURL command
    terminal_window.type_keys(login_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Login cURL command sent successfully!")

    time.sleep(10)

    # Read the response
    with open(output_file, "r") as f:
        login_response_text = f.read().strip()

    try:
        login_response_json = json.loads(login_response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    # Extract response fields
    login_success = login_response_json.get("success")
    login_status = login_response_json.get("status")
    login_message = login_response_json.get("message")

    print(f"Login extracted data: success={login_success}, status={login_status}, message='{login_message}'")

    # Assertions for mock 500
    assert login_success is False, "The 'success' field is not False."
    assert login_status == 500, f"Expected status 500, but received: {login_status}"
    assert login_message == "Internal Error Server", f"Unexpected message: {login_message}"

    # Cleanup output file
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    # Terminate Cmder
    def terminate_process_tree(pid):
        process = psutil.Process(pid)
        for child in process.children(recursive=True):
            child.terminate()
        process.terminate()

    cmder_pid = app.process
    terminate_process_tree(cmder_pid)
    print("Cmder closed.")

    # Terminate mitmproxy
    mitmproxy_proc.terminate()
    mitmproxy_proc.wait()
    print("MITMProxy terminated.")

def test_get_user_server_error():
    # Start random data number
    randomData = Faker().hexify(text='^^^^^^^^^^^^')

    # Start Cmder
    cmder_path = r'Cmder.exe'
    app = Application().start(cmder_path, create_new_console=True, wait_for_idle=False)
    time.sleep(10)

    # Find the process ID of ConEmu
    def find_conemu_pid():
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'ConEmu64.exe':
                return proc.info['pid']
        return None

    pid = find_conemu_pid()
    app = Application().connect(process=pid)
    time.sleep(2)
    terminal_window = app.window(title_re=".*Cmder.*")
    terminal_window.wait('visible', timeout=15)
    terminal_window.maximize()

    # Define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, f'output-{randomData}.json'))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    # Create and login user (reutiliza função existente)
    create_user(terminal_window, output_file, test_data_file)
    login_user(randomData, test_data_file, output_dir, terminal_window)

    # Read user_token
    with open(test_data_file, "r") as f:
        test_data = json.load(f)
    user_token = test_data.get("user_token")

    # Mock endpoint (GET profile)
    get_profile_endpoint = "https://practice.expandtesting.com/notes/api/users/profile"

    # Start mitmproxy with mock script (same logic as in login test)
    mitm_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mock_500.py'))
    mitmproxy_proc = subprocess.Popen(
        ['mitmdump', '-s', mitm_script, '--listen-port', '8080', '--', get_profile_endpoint],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("MITMProxy started.")
    time.sleep(5)

    # Re-define output_file to store GET profile response
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    get_profile_curl_command = f'curl -x http://127.0.0.1:8080 -k -X "GET" "{get_profile_endpoint}" ' \
                            f'-H "accept: application/json" ' \
                            f'-H "x-auth-token: {user_token}" > "{output_file}"'

    terminal_window.type_keys(get_profile_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("GET profile cURL command sent successfully!")

    time.sleep(10)

    # Read and parse response
    with open(output_file, "r") as f:
        get_response_text = f.read().strip()

    try:
        get_response_json = json.loads(get_response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from GET profile response: {e}")
        raise

    # Extract fields
    get_success = get_response_json.get("success")
    get_status = get_response_json.get("status")
    get_message = get_response_json.get("message")

    print(f"GET Profile extracted: success={get_success}, status={get_status}, message='{get_message}'")

    # Assertions for mock 500
    assert get_success is False, "The 'success' field is not False."
    assert get_status == 500, f"Expected status 500, but received: {get_status}"
    assert get_message == "Internal Error Server", f"Unexpected message: {get_message}"

    # Cleanup
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    delete_user(randomData, test_data_file, output_dir, terminal_window)

    def terminate_process_tree(pid):
        process = psutil.Process(pid)
        for child in process.children(recursive=True):
            child.terminate()
        process.terminate()

    cmder_pid = app.process
    terminate_process_tree(cmder_pid)
    print("Cmder closed.")

    mitmproxy_proc.terminate()
    mitmproxy_proc.wait()
    print("MITMProxy terminated.")

def test_update_user_server_error():
    # Start random data number
    randomData = Faker().hexify(text='^^^^^^^^^^^^')

    # Start Cmder
    cmder_path = r'Cmder.exe'
    app = Application().start(cmder_path, create_new_console=True, wait_for_idle=False)
    time.sleep(10)

    # Find the process ID of ConEmu
    def find_conemu_pid():
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'ConEmu64.exe':
                return proc.info['pid']
        return None

    pid = find_conemu_pid()
    app = Application().connect(process=pid)
    time.sleep(2)
    terminal_window = app.window(title_re=".*Cmder.*")
    terminal_window.wait('visible', timeout=15)
    terminal_window.maximize()

    # Define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, f'output-{randomData}.json'))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)
    login_user(randomData, test_data_file, output_dir, terminal_window)

    # Reload test data
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data.get("user_token")

    updated_name = Faker().name()
    updated_phone = Faker().bothify(text='############')
    updated_company = Faker().company()[:24]

    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # Endpoint
    update_endpoint = "https://practice.expandtesting.com/notes/api/users/profile"

    # Start mitmproxy with mock
    mitm_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mock_500.py'))
    mitmproxy_proc = subprocess.Popen(
        ['mitmdump', '-s', mitm_script, '--listen-port', '8080', '--', update_endpoint],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("MITMProxy started.")
    time.sleep(5)

    # PATCH command through mitmproxy
    update_profile_curl_command = f'curl -x http://127.0.0.1:8080 -k -X "PATCH" "{update_endpoint}" ' \
                                  f'-H "accept: application/json" ' \
                                  f'-H "x-auth-token: {user_token}" ' \
                                  f'-H "Content-Type: application/x-www-form-urlencoded" ' \
                                  f'-d "name={updated_name}&phone={updated_phone}&company={updated_company}" > "{output_file}"'

    terminal_window.type_keys(update_profile_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("PATCH profile cURL command sent successfully!")

    time.sleep(10)

    # Read response
    with open(output_file, "r") as f:
        patch_response_text = f.read().strip()

    try:
        patch_response_json = json.loads(patch_response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from PATCH profile response: {e}")
        patch_response_json = {}

    patch_success = patch_response_json.get("success")
    patch_status = patch_response_json.get("status")
    patch_message = patch_response_json.get("message")

    print(f"PATCH Profile extracted: success={patch_success}, status={patch_status}, message='{patch_message}'")

    # Assertions
    assert patch_success is False, "The 'success' field is not False in PATCH profile response."
    assert patch_status == 500, f"Expected status 500 in PATCH profile, but received: {patch_status}"
    assert patch_message == "Internal Error Server", f"Unexpected message: {patch_message}"

    # Cleanup
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    delete_user(randomData, test_data_file, output_dir, terminal_window)

    def terminate_process_tree(pid):
        process = psutil.Process(pid)
        for child in process.children(recursive=True):
            child.terminate()
        process.terminate()

    cmder_pid = app.process
    terminate_process_tree(cmder_pid)
    print("Cmder closed.")

    mitmproxy_proc.terminate()
    mitmproxy_proc.wait()
    print("MITMProxy terminated.")

def test_update_user_password_server_error():
    # Start random data number
    randomData = Faker().hexify(text='^^^^^^^^^^^^')

    # Start Cmder
    cmder_path = r'Cmder.exe'
    app = Application().start(cmder_path, create_new_console=True, wait_for_idle=False)
    time.sleep(10)

    # Find the process ID of ConEmu
    def find_conemu_pid():
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'ConEmu64.exe':
                return proc.info['pid']
        return None

    pid = find_conemu_pid()
    app = Application().connect(process=pid)
    time.sleep(2)
    terminal_window = app.window(title_re=".*Cmder.*")
    terminal_window.wait('visible', timeout=15)
    terminal_window.maximize()

    # Define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, f'output-{randomData}.json'))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)
    login_user(randomData, test_data_file, output_dir, terminal_window)

    # Reload test data
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data.get("user_token")
    current_password = test_data.get("user_password")
    
    new_password = Faker().password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True)

    # Define output file path for password change response
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # Endpoint
    change_password_endpoint = "https://practice.expandtesting.com/notes/api/users/change-password"

    # Start mitmproxy with mock
    mitm_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mock_500.py'))
    mitmproxy_proc = subprocess.Popen(
        ['mitmdump', '-s', mitm_script, '--listen-port', '8080', '--', change_password_endpoint],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("MITMProxy started.")
    time.sleep(5)

    # POST command for changing password through mitmproxy
    change_password_curl_command = f'curl -x http://127.0.0.1:8080 -k -X "POST" "{change_password_endpoint}" ' \
                                   f'-H "accept: application/json" ' \
                                   f'-H "x-auth-token: {user_token}" ' \
                                   f'-H "Content-Type: application/x-www-form-urlencoded" ' \
                                   f'-d "currentPassword={current_password}&newPassword={new_password}" > "{output_file}"'

    terminal_window.type_keys(change_password_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Password change cURL command sent successfully!")

    time.sleep(10)

    # Read and process password change response
    with open(output_file, "r") as f:
        password_response_text = f.read().strip()

    try:
        password_response_json = json.loads(password_response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from password change response: {e}")
        password_response_json = {}

    password_change_success = password_response_json.get("success")
    password_change_status = password_response_json.get("status")
    password_change_message = password_response_json.get("message")

    print(f"Password change response: success={password_change_success}, status={password_change_status}, message='{password_change_message}'")

    # Assertions for mock 500
    assert password_change_success is False, "The 'success' field is not False in password change response."
    assert password_change_status == 500, f"Expected status 500 in password change, but received: {password_change_status}"
    assert password_change_message == "Internal Error Server", f"Unexpected message: {password_change_message}"

    # Cleanup
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    delete_user(randomData, test_data_file, output_dir, terminal_window)

    def terminate_process_tree(pid):
        process = psutil.Process(pid)
        for child in process.children(recursive=True):
            child.terminate()
        process.terminate()

    cmder_pid = app.process
    terminate_process_tree(cmder_pid)
    print("Cmder closed.")

    mitmproxy_proc.terminate()
    mitmproxy_proc.wait()
    print("MITMProxy terminated.")

def test_logout_user_server_error():
    # Start random data number
    randomData = Faker().hexify(text='^^^^^^^^^^^^')

    # Start Cmder
    cmder_path = r'Cmder.exe'
    app = Application().start(cmder_path, create_new_console=True, wait_for_idle=False)
    time.sleep(10)

    # Find the process ID of ConEmu
    def find_conemu_pid():
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'ConEmu64.exe':
                return proc.info['pid']
        return None

    pid = find_conemu_pid()
    app = Application().connect(process=pid)
    time.sleep(2)
    terminal_window = app.window(title_re=".*Cmder.*")
    terminal_window.wait('visible', timeout=15)
    terminal_window.maximize()

    # Define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, f'output-{randomData}.json'))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    # Create user (we'll assume this function works as expected)
    create_user(terminal_window, output_file, test_data_file)

    # Login user (we'll assume login_user works as expected)
    login_user(randomData, test_data_file, output_dir, terminal_window)

    # Read the user data from the test file
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data.get("user_token")

    # Define output file path for logout response
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # Endpoint for the logout action
    logout_endpoint = "https://practice.expandtesting.com/notes/api/users/logout"

    # Start mitmproxy in the background with the mock script and pass the logout endpoint
    mitm_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mock_500.py'))
    mitmproxy_proc = subprocess.Popen(
        ['mitmdump', '-s', mitm_script, '--listen-port', '8080', '--', logout_endpoint],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("MITMProxy started.")
    time.sleep(5)  # Give it time to initialize

    # DELETE command for logout with proxy
    logout_curl_command = f'curl -x http://127.0.0.1:8080 -k -X "DELETE" "{logout_endpoint}" ' \
                          f'-H "accept: application/json" ' \
                          f'-H "x-auth-token: {user_token}" > "{output_file}"'

    # Send the cURL command
    terminal_window.type_keys(logout_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Logout cURL command sent successfully!")

    time.sleep(10)

    # Read and process the logout response
    with open(output_file, "r") as f:
        logout_response_text = f.read().strip()

    try:
        logout_response_json = json.loads(logout_response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        logout_response_json = {}

    logout_success = logout_response_json.get("success")
    logout_status = logout_response_json.get("status")
    logout_message = logout_response_json.get("message")

    print(f"Logout response: success={logout_success}, status={logout_status}, message='{logout_message}'")

    # Assertions for mock 500
    assert logout_success is False, "The 'success' field is not False in logout response."
    assert logout_status == 500, f"Expected status 500 in logout, but received: {logout_status}"
    assert logout_message == "Internal Error Server", f"Unexpected message: {logout_message}"

    # Cleanup output file
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    #login again to grab a new token
    login_user(randomData, test_data_file, output_dir, terminal_window)

    # Delete user (cleanup)
    delete_user(randomData, test_data_file, output_dir, terminal_window)

    def terminate_process_tree(pid):
        process = psutil.Process(pid)
        for child in process.children(recursive=True):
            child.terminate()
        process.terminate()

    cmder_pid = app.process
    terminate_process_tree(cmder_pid)
    print("Cmder closed.")

    # Terminate mitmproxy
    mitmproxy_proc.terminate()
    mitmproxy_proc.wait()
    print("MITMProxy terminated.")

def test_delete_user_server_error():
    # Start random data number
    randomData = Faker().hexify(text='^^^^^^^^^^^^')

    # Start Cmder
    cmder_path = r'Cmder.exe'
    app = Application().start(cmder_path, create_new_console=True, wait_for_idle=False)
    time.sleep(10)

    # Find the process ID of ConEmu
    def find_conemu_pid():
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'ConEmu64.exe':
                return proc.info['pid']
        return None

    pid = find_conemu_pid()
    app = Application().connect(process=pid)
    time.sleep(2)
    terminal_window = app.window(title_re=".*Cmder.*")
    terminal_window.wait('visible', timeout=15)
    terminal_window.maximize()

    # Define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, f'output-{randomData}.json'))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    # Create user (we'll assume this function works as expected)
    create_user(terminal_window, output_file, test_data_file)

    # Login user (we'll assume login_user works as expected)
    login_user(randomData, test_data_file, output_dir, terminal_window)

    # Read the user data from the test file
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data["user_token"]

    # Define the output file path for delete account response
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # Endpoint for deleting user account
    delete_account_endpoint = "https://practice.expandtesting.com/notes/api/users/delete-account"

    # Start mitmproxy in the background with the mock script and pass the delete account endpoint
    mitm_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mock_500.py'))
    mitmproxy_proc = subprocess.Popen(
        ['mitmdump', '-s', mitm_script, '--listen-port', '8080', '--', delete_account_endpoint],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("MITMProxy started.")
    time.sleep(5)  # Give it time to initialize

    # cURL command to delete the user account with proxy
    delete_account_curl_command = f'curl -x http://127.0.0.1:8080 -k -X "DELETE" "{delete_account_endpoint}" ' \
                                 f'-H "accept: application/json" ' \
                                 f'-H "x-auth-token: {user_token}" > "{output_file}"'

    # Send the cURL command
    terminal_window.type_keys(delete_account_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Delete account cURL command sent successfully!")

    time.sleep(10)

    # Read and process the delete account response
    with open(output_file, "r") as f:
        delete_response_text = f.read().strip()

    try:
        delete_response_json = json.loads(delete_response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        delete_response_json = {}

    delete_success = delete_response_json.get("success")
    delete_status = delete_response_json.get("status")
    delete_message = delete_response_json.get("message")

    print(f"Delete response data: success={delete_success}, status={delete_status}, message='{delete_message}'")

    # Assertions for mock 500
    assert delete_success is False, "The 'success' field is not False."
    assert delete_status == 500, f"Expected status 500 in delete account, but received: {delete_status}"
    assert delete_message == "Internal Error Server", f"Unexpected message: {delete_message}"

    # Cleanup output file
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    def terminate_process_tree(pid):
        process = psutil.Process(pid)
        for child in process.children(recursive=True):
            child.terminate()
        process.terminate()

    cmder_pid = app.process
    terminate_process_tree(cmder_pid)
    print("Cmder closed.")

    # Terminate mitmproxy
    mitmproxy_proc.terminate()
    mitmproxy_proc.wait()
    print("MITMProxy terminated.")
