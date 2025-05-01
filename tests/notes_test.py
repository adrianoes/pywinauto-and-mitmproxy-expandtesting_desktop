import pytest
from pywinauto import Application
import time
import psutil
import json
import os
import subprocess
from faker import Faker
from tests.support import create_note, create_user, delete_json_output_file, delete_json_test_data_file, delete_user, login_user, terminate_cmder_process_tree, write_json_test_data_file


def test_create_note_server_error():
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

    # Create user and login
    create_user(terminal_window, output_file, test_data_file)
    login_user(randomData, test_data_file, output_dir, terminal_window)

    # Reload test data
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data.get("user_token")

    note_title = Faker().sentence(4)
    note_description = Faker().sentence(5)
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))

    # Output file for response
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # Start mitmproxy with 500 mock script
    mitm_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mock_500.py'))
    mitmproxy_proc = subprocess.Popen(
        ['mitmdump', '-s', mitm_script, '--listen-port', '8080', '--', "https://practice.expandtesting.com/notes/api/notes"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("MITMProxy started.")
    time.sleep(5)

    # Build cURL for note creation
    create_note_curl_command = f'''curl -x http://127.0.0.1:8080 -k -X "POST" "https://practice.expandtesting.com/notes/api/notes" \
    -H "accept: application/json" \
    -H "x-auth-token: {user_token}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "title={note_title}&description={note_description}&category={note_category}" > "{output_file}"'''

    # Run command
    terminal_window.type_keys(create_note_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Note creation cURL command sent successfully!")

    time.sleep(10)

    # Read response
    with open(output_file, "r") as f:
        note_response_text = f.read().strip()

    try:
        note_response_json = json.loads(note_response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from note creation response: {e}")
        note_response_json = {}

    note_success = note_response_json.get("success")
    note_status = note_response_json.get("status")
    note_message = note_response_json.get("message")

    print(f"Note creation response: success={note_success}, status={note_status}, message='{note_message}'")

    # Assertions for mock 500
    assert note_success is False, "The 'success' field is not False in note creation response."
    assert note_status == 500, f"Expected status 500 in note creation, but received: {note_status}"
    assert note_message == "Internal Error Server", f"Unexpected message: {note_message}"

    # Cleanup
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    terminate_cmder_process_tree(app)

def test_get_notes_server_error():
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
    output_file = os.path.abspath(os.path.join(output_dir, f"output_get_all_{randomData}.json"))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)
    login_user(randomData, test_data_file, output_dir, terminal_window)

    # Load test data
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data.get("user_token")

    # Start mitmproxy with 500 mock
    mitm_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mock_500.py'))
    mitmproxy_proc = subprocess.Popen(
        ['mitmdump', '-s', mitm_script, '--listen-port', '8080', '--', 'https://practice.expandtesting.com/notes/api/notes'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("MITMProxy started.")
    time.sleep(5)

    # cURL GET all notes (proxied)
    get_all_command = f'''curl -x http://127.0.0.1:8080 -k -X "GET" "https://practice.expandtesting.com/notes/api/notes" \
    -H "accept: application/json" \
    -H "x-auth-token: {user_token}" > "{output_file}"'''

    terminal_window.type_keys(get_all_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("GET ALL NOTES command sent successfully.")

    time.sleep(10)

    with open(output_file, "r") as f:
        response_text = f.read().strip()

    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta do GET ALL: {e}")
        response_json = {}

    # Extract fields
    get_notes_success = response_json.get("success")
    get_notes_status = response_json.get("status")
    get_notes_message = response_json.get("message")

    print(f"GET ALL NOTES response: success={get_notes_success}, status={get_notes_status}, message='{get_notes_message}'")

    # Assertions for mock 500
    assert get_notes_success is False, "The 'success' field is not False in get all notes response."
    assert get_notes_status == 500, f"Expected status 500 in get all notes, but received: {get_notes_status}"
    assert get_notes_message == "Internal Error Server", f"Unexpected message: {get_notes_message}"

    # Cleanup
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    terminate_cmder_process_tree(app)

def test_get_note_server_error():
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
    output_file = os.path.abspath(os.path.join(output_dir, f"output_get_{randomData}.json"))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)
    login_user(randomData, test_data_file, output_dir, terminal_window)
    create_note(test_data_file, output_dir, randomData, terminal_window)

    # Load test data
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Retrieve all necessary variables
    user_token = test_data.get("user_token")
    note_id = test_data.get("note_id")

    # Start mitmproxy with 500 mock
    mitm_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mock_500.py'))
    mitmproxy_proc = subprocess.Popen(
        ['mitmdump', '-s', mitm_script, '--listen-port', '8080', '--', 'https://practice.expandtesting.com/notes/api/notes/{note_id}'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("MITMProxy started.")
    time.sleep(5)

    # cURL GET note by ID (proxied)
    get_note_curl_command = f'''curl -x http://127.0.0.1:8080 -k -X "GET" "https://practice.expandtesting.com/notes/api/notes/{note_id}" \
    -H "accept: application/json" \
    -H "x-auth-token: {user_token}" > "{output_file}"'''

    terminal_window.type_keys(get_note_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Note GET by ID cURL command sent successfully!")

    time.sleep(10)

    with open(output_file, "r") as f:
        get_response_text = f.read().strip()

    try:
        get_response_json = json.loads(get_response_text)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta de GET note: {e}")
        get_response_json = {}

    # Extract fields
    get_success = get_response_json.get("success")
    get_status = get_response_json.get("status")
    get_message = get_response_json.get("message")

    print(f"GET NOTE response: success={get_success}, status={get_status}, message='{get_message}'")

    # Assertions for mock 500
    assert get_success is False, "The 'success' field is not False in GET note response."
    assert get_status == 500, f"Expected status 500 in GET note, but received: {get_status}"
    assert get_message == "Internal Error Server", f"Unexpected message: {get_message}"

    # Cleanup
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    terminate_cmder_process_tree(app)

def test_update_note_server_error():
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
    output_file = os.path.abspath(os.path.join(output_dir, f"output_update_{randomData}.json"))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)
    login_user(randomData, test_data_file, output_dir, terminal_window)
    create_note(test_data_file, output_dir, randomData, terminal_window)

    # Load test data
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Retrieve necessary variables
    user_token = test_data.get("user_token")
    note_id = test_data.get("note_id")

    # Generate updated values with Faker
    note_title = Faker().sentence(4)
    note_description = Faker().sentence(5)
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))
    note_completed = True

    # Start mitmproxy with 500 mock
    mitm_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mock_500.py'))
    mitmproxy_proc = subprocess.Popen(
        ['mitmdump', '-s', mitm_script, '--listen-port', '8080', '--', 'https://practice.expandtesting.com/notes/api/notes/{note_id}'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("MITMProxy started.")
    time.sleep(5)

    # cURL update note (proxied)
    update_note_command = f'''curl -x http://127.0.0.1:8080 -k -X "PUT" "https://practice.expandtesting.com/notes/api/notes/{note_id}" \
    -H "accept: application/json" \
    -H "x-auth-token: {user_token}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "title={note_title}&description={note_description}&completed=true&category={note_category}" > "{output_file}"'''

    terminal_window.type_keys(update_note_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Note UPDATE cURL command sent successfully.")

    time.sleep(10)

    with open(output_file, "r") as f:
        update_response_text = f.read().strip()

    try:
        update_response_json = json.loads(update_response_text)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta de update: {e}")
        update_response_json = {}

    # Extract fields from the response
    update_success = update_response_json.get("success")
    update_status = update_response_json.get("status")
    update_message = update_response_json.get("message")

    print(f"UPDATE NOTE response: success={update_success}, status={update_status}, message='{update_message}'")

    # Assertions for mock 500
    assert update_success is False, "The 'success' field is not False in update note response."
    assert update_status == 500, f"Expected status 500 in update note, but received: {update_status}"
    assert update_message == "Internal Error Server", f"Unexpected message: {update_message}"

    # Cleanup
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    terminate_cmder_process_tree(app)

def test_update_note_status_server_error():
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
    output_file = os.path.abspath(os.path.join(output_dir, f"output_patch_{randomData}.json"))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)
    login_user(randomData, test_data_file, output_dir, terminal_window)
    create_note(test_data_file, output_dir, randomData, terminal_window)

    # Load test data
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Retrieve necessary variables
    user_token = test_data.get("user_token")
    note_id = test_data.get("note_id")

    # Start mitmproxy with 500 mock
    mitm_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mock_500.py'))
    mitmproxy_proc = subprocess.Popen(
        ['mitmdump', '-s', mitm_script, '--listen-port', '8080', '--', 'https://practice.expandtesting.com/notes/api/notes/{note_id}'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("MITMProxy started.")
    time.sleep(5)

    # cURL PATCH update note status (proxied)
    patch_command = f'''curl -x http://127.0.0.1:8080 -k -X "PATCH" "https://practice.expandtesting.com/notes/api/notes/{note_id}" \
    -H "accept: application/json" \
    -H "x-auth-token: {user_token}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "completed=true" > "{output_file}"'''

    terminal_window.type_keys(patch_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("PATCH cURL command sent successfully.")

    time.sleep(10)

    with open(output_file, "r") as f:
        response_text = f.read().strip()

    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta do PATCH: {e}")
        response_json = {}

    # Extract fields from the response
    success = response_json.get("success")
    status = response_json.get("status")
    message = response_json.get("message")

    print(f"PATCH NOTE response: success={success}, status={status}, message='{message}'")

    # Assertions for mock 500
    assert success is False, "The 'success' field is not False in update note status response."
    assert status == 500, f"Expected status 500, but received: {status}"
    assert message == "Internal Error Server", f"Unexpected message: {message}"

    # Cleanup
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    terminate_cmder_process_tree(app)

def test_delete_note_server_error():
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
    output_file = os.path.abspath(os.path.join(output_dir, f"output_delete_{randomData}.json"))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)
    login_user(randomData, test_data_file, output_dir, terminal_window)
    create_note(test_data_file, output_dir, randomData, terminal_window)

    # Load test data
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Retrieve necessary variables
    user_token = test_data.get("user_token")
    note_id = test_data.get("note_id")

    # Start mitmproxy with 500 mock
    mitm_script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'mock_500.py'))
    mitmproxy_proc = subprocess.Popen(
        ['mitmdump', '-s', mitm_script, '--listen-port', '8080', '--', 'https://practice.expandtesting.com/notes/api/notes/{note_id}'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("MITMProxy started.")
    time.sleep(5)

    # cURL DELETE delete note (proxied)
    delete_command = f'''curl -x http://127.0.0.1:8080 -k -X "DELETE" "https://practice.expandtesting.com/notes/api/notes/{note_id}" \
    -H "accept: application/json" \
    -H "x-auth-token: {user_token}" > "{output_file}"'''

    terminal_window.type_keys(delete_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("DELETE cURL command sent successfully.")

    time.sleep(10)

    with open(output_file, "r") as f:
        response_text = f.read().strip()

    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta do DELETE: {e}")
        response_json = {}

    # Extract fields from the response
    success = response_json.get("success")
    status = response_json.get("status")
    message = response_json.get("message")

    print(f"DELETE NOTE response: success={success}, status={status}, message='{message}'")

    # Assertions for mock 500
    assert success is False, "The 'success' field is not False in delete note response."
    assert status == 500, f"Expected status 500, but received: {status}"
    assert message == "Internal Error Server", f"Unexpected message: {message}"

    # Cleanup
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"Removed the JSON file: {output_file}")

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    terminate_cmder_process_tree(app)




















