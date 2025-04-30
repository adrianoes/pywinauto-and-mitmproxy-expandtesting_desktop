import pytest
from pywinauto import Application
import time
import psutil
import json
import os
import glob
from faker import Faker
from tests.support import create_note, create_user, delete_json_output_file, delete_json_test_data_file, delete_user, login_user, terminate_cmder_process_tree, write_json_test_data_file


def test_crete_note_unauthorized():
    #start random data number
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

    #define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, f'output-{randomData}.json'))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)

    login_user(randomData, test_data_file, output_dir, terminal_window)

    # Lê os dados existentes do JSON
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data.get("user_token")
    user_id = test_data.get("user_id")

    note_title = Faker().sentence(4)
    note_description = Faker().sentence(5)
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))

    # Define o caminho para salvar a resposta do cURL
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # Monta comando cURL para criar nota
    create_note_curl_command = f'''curl -X "POST" "https://practice.expandtesting.com/notes/api/notes" \
    -H "accept: application/json" \
    -H "x-auth-token: @{user_token}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "title={note_title}&description={note_description}&category={note_category}" > "{output_file}"'''

    # Executa o comando no terminal
    terminal_window.type_keys(create_note_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Note creation cURL command sent successfully!")

    time.sleep(10)

    # Lê e processa a resposta
    with open(output_file, "r") as f:
        note_response_text = f.read().strip()

    try:
        note_response_json = json.loads(note_response_text)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta de criação de nota: {e}")
        return

    # Extrai dados da resposta
    note_success = note_response_json.get("success")
    note_status = note_response_json.get("status")
    note_message = note_response_json.get("message")

    print(f"Note creation response: success={note_success}, status={note_status}, message='{note_message}'")

    # Assertions
    assert note_success is False, "The 'success' field is not False in note creation response."
    assert note_status == 401, f"Expected status 401 in note creation, but received: {note_status}"
    assert note_message == "Access token is not valid or has expired, you will need to login", f"Unexpected message: {note_message}"

    delete_json_output_file(output_file)

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    
    terminate_cmder_process_tree(app)

def test_get_notes_unauthorized():
    #start random data number
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

    #define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, f'output-{randomData}.json'))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)

    login_user(randomData, test_data_file, output_dir, terminal_window)

    # Lê os dados existentes do JSON
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data.get("user_token")
    user_id = test_data.get("user_id")

    note_title = Faker().sentence(4)
    note_description = Faker().sentence(5)
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))

    note_title_2 = Faker().sentence(4)
    note_description_2 = Faker().sentence(5)
    note_category_2 = Faker().random_element(elements=('Home', 'Personal', 'Work'))

    # Define o caminho para salvar a resposta do cURL
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # Monta comando cURL para criar nota
    create_note_curl_command = f'''curl -X "POST" "https://practice.expandtesting.com/notes/api/notes" \
    -H "accept: application/json" \
    -H "x-auth-token: {user_token}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "title={note_title}&description={note_description}&category={note_category}" > "{output_file}"'''

    # Executa o comando no terminal
    terminal_window.type_keys(create_note_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Note creation cURL command sent successfully!")

    time.sleep(10)

    # Lê e processa a resposta
    with open(output_file, "r") as f:
        note_response_text = f.read().strip()

    try:
        note_response_json = json.loads(note_response_text)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta de criação de nota: {e}")
        return

    # Extrai dados da resposta
    note_success = note_response_json.get("success")
    note_status = note_response_json.get("status")
    note_message = note_response_json.get("message")
    note_data = note_response_json.get("data", {})

    note_id = note_data.get("id")
    note_completed = note_data.get("completed")
    note_created_at = note_data.get("created_at")
    note_updated_at = note_data.get("updated_at")
    note_user_id_resp = note_data.get("user_id")
    note_title_resp = note_data.get("title")
    note_description_resp = note_data.get("description")
    note_category_resp = note_data.get("category")

    print(f"Note creation response: success={note_success}, status={note_status}, message='{note_message}'")

    # Assertions
    assert note_success is True, "The 'success' field is not True in note creation response."
    assert note_status == 200, f"Expected status 200 in note creation, but received: {note_status}"
    assert note_message == "Note successfully created", f"Unexpected message: {note_message}"
    assert note_id is not None, "Note ID is missing in the response."
    assert note_user_id_resp == user_id, f"User ID mismatch: expected {user_id}, got {note_user_id_resp}"
    assert note_title_resp == note_title, f"Note title mismatch: expected {note_title}, got {note_title_resp}"
    assert note_description_resp == note_description, f"Note description mismatch: expected {note_description}, got {note_description_resp}"
    assert note_category_resp == note_category, f"Note category mismatch: expected {note_category}, got {note_category_resp}"

    # Atualiza JSON com dados da nota e dados de usuário
    test_data.update({
        "user_id": user_id,
        "user_token": user_token,
        "note_id": note_id,
        "note_title": note_title,
        "note_description": note_description,
        "note_category": note_category,
        "note_completed": note_completed,
        "note_created_at": note_created_at,
        "note_updated_at": note_updated_at
    })

    with open(test_data_file, "w") as f:
        json.dump(test_data, f, indent=4)

    print("Note creation data saved successfully in JSON.")

    # Define o caminho para salvar a resposta do cURL
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # Monta comando cURL para criar nota
    create_note_curl_command_2 = f'''curl -X "POST" "https://practice.expandtesting.com/notes/api/notes" \
    -H "accept: application/json" \
    -H "x-auth-token: {user_token}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "title={note_title_2}&description={note_description_2}&category={note_category_2}" > "{output_file}"'''

    # Executa o comando no terminal
    terminal_window.type_keys(create_note_curl_command_2, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Note creation cURL command sent successfully!")

    time.sleep(10)

    # Lê e processa a resposta
    with open(output_file, "r") as f:
        note_response_text_2 = f.read().strip()

    try:
        note_response_json_2 = json.loads(note_response_text_2)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta de criação de nota: {e}")
        return

    # Extrai dados da resposta
    note_success = note_response_json_2.get("success")
    note_status = note_response_json_2.get("status")
    note_message = note_response_json_2.get("message")
    note_data_2 = note_response_json_2.get("data", {})

    note_id_2 = note_data_2.get("id")
    note_completed_2 = note_data_2.get("completed")
    note_created_at_2 = note_data_2.get("created_at")
    note_updated_at_2 = note_data_2.get("updated_at")
    note_user_id_resp_2 = note_data_2.get("user_id")
    note_title_resp_2 = note_data_2.get("title")
    note_description_resp_2 = note_data_2.get("description")
    note_category_resp_2 = note_data_2.get("category")

    print(f"Note creation response: success={note_success}, status={note_status}, message='{note_message}'")

    # Assertions
    assert note_success is True, "The 'success' field is not True in note creation response."
    assert note_status == 200, f"Expected status 200 in note creation, but received: {note_status}"
    assert note_message == "Note successfully created", f"Unexpected message: {note_message}"
    assert note_id_2 is not None, "Note ID is missing in the response."
    assert note_user_id_resp_2 == user_id, f"User ID mismatch: expected {user_id}, got {note_user_id_resp}"
    assert note_title_resp_2 == note_title_2, f"Note title mismatch: expected {note_title}, got {note_title_resp}"
    assert note_description_resp_2 == note_description_2, f"Note description mismatch: expected {note_description}, got {note_description_resp}"
    assert note_category_resp_2 == note_category_2, f"Note category mismatch: expected {note_category}, got {note_category_resp}"

    # Atualiza JSON com dados da nota e dados de usuário
    test_data.update({
        "note_id_2": note_id_2,
        "note_title_2": note_title_2,
        "note_description_2": note_description_2,
        "note_category_2": note_category_2,
        "note_completed_2": note_completed_2,
        "note_created_at_2": note_created_at_2,
        "note_updated_at_2": note_updated_at_2
    })

    with open(test_data_file, "w") as f:
        json.dump(test_data, f, indent=4)

    print("Note creation data saved successfully in JSON.")

    delete_json_output_file(output_file)

    # Lê dados salvos do JSON
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data["user_token"]
    user_id = test_data["user_id"]

    # Dados da nota 2 (mais recente, index 0)
    note_id_2 = test_data["note_id_2"]
    note_title_2 = test_data["note_title_2"]
    note_description_2 = test_data["note_description_2"]
    note_category_2 = test_data["note_category_2"]
    note_completed_2 = test_data["note_completed_2"]
    note_created_at_2 = test_data["note_created_at_2"]
    note_updated_at_2 = test_data["note_updated_at_2"]

    # Dados da nota 1 (mais antiga, index 1)
    note_id = test_data["note_id"]
    note_title = test_data["note_title"]
    note_description = test_data["note_description"]
    note_category = test_data["note_category"]
    note_completed = test_data["note_completed"]
    note_created_at = test_data["note_created_at"]
    note_updated_at = test_data["note_updated_at"]

    # Caminho para salvar a resposta
    output_file = os.path.abspath(os.path.join(output_dir, f"output_get_all_{randomData}.json"))

    # cURL de GET ALL NOTES
    get_all_command = f'''curl -X "GET" "https://practice.expandtesting.com/notes/api/notes" \
    -H "accept: application/json" \
    -H "x-auth-token: @{user_token}" > "{output_file}"'''

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
        return

    assert response_json.get("success") is False
    assert response_json.get("status") == 401
    assert response_json.get("message") == "Access token is not valid or has expired, you will need to login"

    delete_json_output_file(output_file)

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    
    terminate_cmder_process_tree(app)

def test_get_note_unauthorized():
    #start random data number
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

    #define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, f'output-{randomData}.json'))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)

    login_user(randomData, test_data_file, output_dir, terminal_window)

    create_note(test_data_file, output_dir, randomData, terminal_window)

        # Lê os dados existentes do JSON
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Recupera todas as variáveis
    user_token = test_data.get("user_token")
    user_id = test_data.get("user_id")
    note_id = test_data.get("note_id")
    note_title = test_data.get("note_title")
    note_description = test_data.get("note_description")
    note_category = test_data.get("note_category")
    note_completed = test_data.get("note_completed")
    note_created_at = test_data.get("note_created_at")
    note_updated_at = test_data.get("note_updated_at")

    # Define o caminho para salvar a resposta do cURL
    output_file = os.path.abspath(os.path.join(output_dir, f'output_get_{randomData}.json'))

    # Monta comando cURL para buscar nota por ID
    get_note_curl_command = f'''curl -X "GET" "https://practice.expandtesting.com/notes/api/notes/{note_id}" \
    -H "accept: application/json" \
    -H "x-auth-token: @{user_token}" > "{output_file}"'''

    # Executa o comando no terminal
    terminal_window.type_keys(get_note_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Note GET by ID cURL command sent successfully!")

    time.sleep(10)

    # Lê e processa a resposta
    with open(output_file, "r") as f:
        get_response_text = f.read().strip()

    try:
        get_response_json = json.loads(get_response_text)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta de GET note: {e}")
        return

    # Extrai dados da resposta
    get_success = get_response_json.get("success")
    get_status = get_response_json.get("status")
    get_message = get_response_json.get("message")

    # Assertions
    assert get_success is False, "The 'success' field is not False in GET note response."
    assert get_status == 401, f"Expected status 401 in GET note, but received: {get_status}"
    assert get_message == "Access token is not valid or has expired, you will need to login", f"Unexpected message: {get_message}"

    delete_json_output_file(output_file)

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    
    terminate_cmder_process_tree(app)

def test_update_note_unauthorized():
    #start random data number
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

    #define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, f'output-{randomData}.json'))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)

    login_user(randomData, test_data_file, output_dir, terminal_window)

    create_note(test_data_file, output_dir, randomData, terminal_window)

    # Lê dados existentes do JSON
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Lê valores existentes
    user_token = test_data.get("user_token")
    user_id = test_data.get("user_id")
    note_id = test_data.get("note_id")
    note_created_at = test_data.get("note_created_at")

    # Gera valores atualizados com Faker
    note_title = Faker().sentence(4)
    note_description = Faker().sentence(5)
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))
    note_completed = True

    # Define caminho do output
    output_file = os.path.abspath(os.path.join(output_dir, f"output_update_{randomData}.json"))

    # Monta comando cURL de update
    update_note_command = f'''curl -X "PUT" "https://practice.expandtesting.com/notes/api/notes/{note_id}" \
    -H "accept: application/json" \
    -H "x-auth-token: @{user_token}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "title={note_title}&description={note_description}&completed=true&category={note_category}" > "{output_file}"'''

    # Executa no terminal
    terminal_window.type_keys(update_note_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Note UPDATE cURL command sent successfully.")

    time.sleep(10)

    # Lê a resposta
    with open(output_file, "r") as f:
        update_response_text = f.read().strip()

    try:
        update_response_json = json.loads(update_response_text)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta de update: {e}")
        return

    # Extrai dados da resposta
    update_success = update_response_json.get("success")
    update_status = update_response_json.get("status")
    update_message = update_response_json.get("message")

    # Assertions
    assert update_success is False, "Update 'success' flag is not False."
    assert update_status == 401, f"Expected status 401, got {update_status}"
    assert update_message == "Access token is not valid or has expired, you will need to login", f"Unexpected update message: {update_message}"

    delete_json_output_file(output_file)

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    
    terminate_cmder_process_tree(app)

def test_update_note_status_unauthorized():
    #start random data number
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

    #define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, f'output-{randomData}.json'))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)

    login_user(randomData, test_data_file, output_dir, terminal_window)

    create_note(test_data_file, output_dir, randomData, terminal_window)

     # Lê dados existentes do JSON
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Lê valores do JSON
    user_token = test_data.get("user_token")
    user_id = test_data.get("user_id")
    note_id = test_data.get("note_id")
    note_title = test_data.get("note_title")
    note_description = test_data.get("note_description")
    note_category = test_data.get("note_category")
    note_created_at = test_data.get("note_created_at")

    # Caminho para salvar a resposta
    output_file = os.path.abspath(os.path.join(output_dir, f"output_patch_{randomData}.json"))

    # Monta o comando cURL PATCH
    patch_command = f'''curl -X "PATCH" "https://practice.expandtesting.com/notes/api/notes/{note_id}" \
    -H "accept: application/json" \
    -H "x-auth-token: @{user_token}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "completed=true" > "{output_file}"'''

    # Executa o comando
    terminal_window.type_keys(patch_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("PATCH cURL command sent successfully.")

    time.sleep(10)

    # Lê e processa a resposta
    with open(output_file, "r") as f:
        response_text = f.read().strip()

    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta do PATCH: {e}")
        return

    # Extrai dados
    success = response_json.get("success")
    status = response_json.get("status")
    message = response_json.get("message")

    # Assertions
    assert success is False, "PATCH 'success' should be False."
    assert status == 401, f"Expected status 401, got {status}"
    assert message == "Access token is not valid or has expired, you will need to login", f"Unexpected message: {message}"

    delete_json_output_file(output_file)

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    
    terminate_cmder_process_tree(app)

def test_delete_note_unauthorized():
    #start random data number
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

    #define paths
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'resources')
    output_file = os.path.abspath(os.path.join(output_dir, f'output-{randomData}.json'))
    test_data_file = os.path.abspath(os.path.join(output_dir, f'test_data-{randomData}.json'))
    os.makedirs(output_dir, exist_ok=True)

    create_user(terminal_window, output_file, test_data_file)

    login_user(randomData, test_data_file, output_dir, terminal_window)

    create_note(test_data_file, output_dir, randomData, terminal_window)

     # Lê dados necessários do JSON
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data.get("user_token")
    note_id = test_data.get("note_id")

    # Caminho para salvar a resposta
    output_file = os.path.abspath(os.path.join(output_dir, f"output_delete_{randomData}.json"))

    # Comando cURL DELETE
    delete_command = f'''curl -X "DELETE" "https://practice.expandtesting.com/notes/api/notes/{note_id}" \
    -H "accept: application/json" \
    -H "x-auth-token: @{user_token}" > "{output_file}"'''

    # Executa o comando
    terminal_window.type_keys(delete_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("DELETE cURL command sent successfully.")

    time.sleep(10)

    # Lê a resposta
    with open(output_file, "r") as f:
        response_text = f.read().strip()

    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON da resposta do DELETE: {e}")
        return

    # Validações
    success = response_json.get("success")
    status = response_json.get("status")
    message = response_json.get("message")

    assert success is False, "DELETE 'success' should be False."
    assert status == 401, f"Expected status 401, got {status}"
    assert message == "Access token is not valid or has expired, you will need to login", f"Unexpected message: {message}"

    delete_json_output_file(output_file)

    delete_user(randomData, test_data_file, output_dir, terminal_window)
    
    terminate_cmder_process_tree(app)



















