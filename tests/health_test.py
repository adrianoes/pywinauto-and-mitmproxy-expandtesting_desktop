import pytest
from pywinauto import Application
import time
import psutil
import json
import os
import subprocess

def test_health_curl_mocked():
    cmder_path = r'Cmder.exe'
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, 'api_output.json'))
    mitm_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mock_500.py'))

    # Ensure 'resources' folder exists
    os.makedirs(output_dir, exist_ok=True)

    # Remove the previous file if it exists
    if os.path.exists(output_file):
        os.remove(output_file)

    # Start mitmproxy in the background
    mitmproxy_proc = subprocess.Popen(
        ['mitmdump', '-s', mitm_script, '--listen-port', '8080'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("MITMProxy started.")
    time.sleep(5)  # Give it time to initialize

    # Start Cmder
    app = Application().start(cmder_path, create_new_console=True, wait_for_idle=False)
    time.sleep(10)

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

    # Curl with proxy
    curl_command = (
        f'curl -x http://127.0.0.1:8080 -k -X "GET" '
        f'"https://practice.expandtesting.com/notes/api/health-check" '
        f'-H "accept: application/json" > "{output_file}"'
    )

    terminal_window.type_keys(curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("cURL command sent with proxy!")

    time.sleep(10)

    # Read and print the raw response from the network
    with open(output_file, "r") as f:
        response_text = f.read().strip()

    print(f"Received Response: {response_text}")  # Print the raw response

    # Try to parse the JSON
    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        raise

    # Extract fields from the response
    success = response_json.get("success")
    status = response_json.get("status")
    message = response_json.get("message")

    print(f"Mocked response: success={success}, status={status}, message='{message}'")

    # Assertions for mock 500
    assert success is False, "Expected 'success' to be False due to server error mock."
    assert status == 500, f"Expected status 500, got: {status}"
    assert message == "Internal Error Server", f"Unexpected error message: {message}"

    # Cleanup output file
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    # Kill Cmder
    def terminate_process_tree(pid):
        process = psutil.Process(pid)
        for child in process.children(recursive=True):
            child.terminate()
        process.terminate()

    cmder_pid = app.process
    terminate_process_tree(cmder_pid)
    print("Cmder closed.")

    # Kill mitmproxy
    mitmproxy_proc.terminate()
    mitmproxy_proc.wait()
    print("MITMProxy terminated.")
