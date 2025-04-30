import glob
import pytest
from pywinauto import Application
import time
import psutil
import json
import os
from faker import Faker


def create_user(terminal_window, output_file, test_data_file):
    # Generate random user data using Faker
    user_name = Faker().name()
    user_email = Faker().lexify(text='??').lower() + Faker().company_email().replace("-", "")
    user_password = Faker().password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True)

    # cURL command to create a new user and save the response in the 'resources' folder
    curl_command = f'curl -X "POST" "https://practice.expandtesting.com/notes/api/users/register" ' \
                   f'-H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" ' \
                   f'-d "name={user_name}&email={user_email}&password={user_password}" > "{output_file}"'

    terminal_window.type_keys(curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("cURL command sent successfully!")

    time.sleep(10)

    with open(output_file, "r") as f:
        response_text = f.read().strip()
    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    success = response_json.get("success")
    status = response_json.get("status")
    message = response_json.get("message")
    user_id = response_json.get("data", {}).get("id")

    print(f"Extracted data: success={success}, status={status}, message='{message}', user_id={user_id}")

    # Assertions
    assert success is True, "The 'success' field is not True."
    assert status == 201, f"Expected status 201, but received: {status}"
    assert message == "User account created successfully", f"Unexpected message: {message}"
    assert user_name == response_json.get("data", {}).get("name"), "User name mismatch"
    assert user_email == response_json.get("data", {}).get("email"), "User email mismatch"

    # Save the test data in a JSON file
    test_data = {
        "user_name": user_name,
        "user_email": user_email,
        "user_password": user_password,
        "user_id": user_id
    }

    write_json_test_data_file(test_data_file, test_data)

    delete_json_output_file(output_file)

def login_user(randomData, test_data_file, output_dir, terminal_window):
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    # Extract the user data from the test data file
    user_name = test_data.get("user_name")
    user_email = test_data.get("user_email")
    user_password = test_data.get("user_password")  # We read user_password even if not used yet
    user_id = test_data.get("user_id")  # Read user_id from the JSON file

    # cURL command to login the user and save the response in the 'resources' folder
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    login_curl_command = f'curl -X "POST" "https://practice.expandtesting.com/notes/api/users/login" ' \
                        f'-H "accept: application/json" -H "Content-Type: application/x-www-form-urlencoded" ' \
                        f'-d "email={user_email}&password={user_password}" > "{output_file}"'

    terminal_window.type_keys(login_curl_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Login cURL command sent successfully!")

    time.sleep(10)

    with open(output_file, "r") as f:
        login_response_text = f.read().strip()

    try:
        login_response_json = json.loads(login_response_text)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    login_success = login_response_json.get("success")
    login_status = login_response_json.get("status")
    login_message = login_response_json.get("message")
    user_token_from_response = login_response_json.get("data", {}).get("token")
    login_user_id = login_response_json.get("data", {}).get("id")

    print(f"Login extracted data: success={login_success}, status={login_status}, message='{login_message}', "
        f"user_id={login_user_id}, token={user_token_from_response}")

    # Assertions
    assert login_success is True, "The 'success' field is not True for login."
    assert login_status == 200, f"Expected status 200 for login, but received: {login_status}"
    assert login_message == "Login successful", f"Unexpected message for login: {login_message}"
    assert user_name == login_response_json.get("data", {}).get("name"), "User name mismatch for account deletion."
    assert user_email == login_response_json.get("data", {}).get("email"), "User email mismatch for login."
    assert user_token_from_response is not None, "Token should not be None after login."
    assert user_id == login_user_id, f"User ID mismatch: expected {user_id}, but got {login_user_id}"

    # Update the test data with the token and user_id (just in case we need them later)
    test_data.update({
        "user_token": user_token_from_response
    })

    write_json_test_data_file(test_data_file, test_data) 

    delete_json_output_file(output_file)
    
def delete_user(randomData, test_data_file, output_dir, terminal_window):
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data["user_token"]  # Directly getting the user token without checking for existence

    # cURL command to login the user and save the response in the 'resources' folder
    output_file = os.path.abspath(os.path.join(output_dir, f'output{randomData}.json'))

    # cURL command to delete the user account using the user token
    delete_account_command = f'curl -X "DELETE" "https://practice.expandtesting.com/notes/api/users/delete-account" -H "accept: application/json" -H "x-auth-token: {user_token}" > "{output_file}"'
    
    # Send the cURL command to the terminal to delete the account
    terminal_window.type_keys(delete_account_command, with_spaces=True)
    terminal_window.type_keys("{ENTER}")
    print("Delete account cURL command sent successfully!")

    time.sleep(10)  # Wait for the response to come back

    # Read the response from the output file
    with open(output_file, "r") as f:
        delete_response_text = f.read().strip()

    # Parse the response JSON
    delete_response_json = json.loads(delete_response_text)

    # Extract response details
    delete_success = delete_response_json.get("success")
    delete_status = delete_response_json.get("status")
    delete_message = delete_response_json.get("message")

    print(f"Delete response data: success={delete_success}, status={delete_status}, message='{delete_message}'")

    # Assertions for account deletion
    assert delete_success is True, "The 'success' field is not True."
    assert delete_status == 200, f"Expected status 200, but received: {delete_status}"
    assert delete_message == "Account successfully deleted", f"Unexpected message: {delete_message}"

    delete_json_test_data_file(test_data_file)

    delete_json_output_file(output_file)
    
def delete_json_output_file(output_file):
    if os.path.exists(output_file):
        os.remove(output_file)
    print(f"Removed the JSON file: {output_file}")  
    
def delete_json_test_data_file(test_data_file):
    # Remove the test data JSON file after the test
    if os.path.exists(test_data_file):
        os.remove(test_data_file)
        print(f"Removed the test data file: {test_data_file}")

def write_json_test_data_file(test_data_file, test_data):
    with open(test_data_file, "w") as f:
        json.dump(test_data, f, indent=4)
    print(f"Test data saved in {test_data_file}")
  
def terminate_cmder_process_tree(app):
    """
    Termina o processo do Cmder e todos os subprocessos associados (como cmd.exe).
    Além disso, exclui arquivos temporários relacionados ao Clink.
    """
    cmder_pid = app.process
    try:
        # Termina os processos filhos e o processo principal
        process = psutil.Process(cmder_pid)
        for child in process.children(recursive=True):
            child.terminate()
        process.terminate()
        print("Cmder process and its children have been terminated.")
        
        # Limpeza de arquivos temporários relacionados ao Clink
        config_dir = "config"
        file_patterns = [
            "clink_history_*.local",
            "clink.log",
            "clink_errorlevel_*.txt"
        ]
        
        # Função para excluir os arquivos
        def delete_files(pattern):
            files = glob.glob(os.path.join(config_dir, pattern))
            for file in files:
                try:
                    os.remove(file)
                    print(f"Arquivo excluído: {file}")
                except Exception as e:
                    print(f"Erro ao excluir o arquivo {file}: {e}")

        # Excluir os arquivos com os padrões definidos
        for pattern in file_patterns:
            delete_files(pattern)
        
    except psutil.NoSuchProcess:
        print(f"No such process with PID: {cmder_pid}")
    except Exception as e:
        print(f"Error terminating process tree: {e}")

def create_note(test_data_file, output_dir, randomData, terminal_window):
       # Lê os dados existentes do JSON
    with open(test_data_file, "r") as f:
        test_data = json.load(f)

    user_token = test_data.get("user_token")
    user_id = test_data.get("user_id")

    # Gera dados da nota com Faker
    faker = Faker()
    note_title = faker.sentence(4)
    note_description = faker.sentence(5)
    note_category = faker.random_element(elements=('Home', 'Personal', 'Work'))

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
    
    delete_json_output_file(output_file)