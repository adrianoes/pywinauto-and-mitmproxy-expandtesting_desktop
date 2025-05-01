# pywinauto-and-mitmproxy-expandtesting_desktop

Desktop testing in [expandtesting](https://practice.expandtesting.com/notes/api/api-docs/) API documentation through pywinauto, mitmproxy and cmder. This project contains basic examples on how to use pywinauto, mitmproxy and Cmder to send curl commands through cmder, mock the network responses to 500 code and assert how cmder behave with it. Good practices such as hooks, custom commands and tags, among others, are used. All the necessary support documentation to develop this project is placed here. 

# Pre-requirements:

| Requirement                     | Version                     | Note                      |
| :------------------------------ |:----------------------------| :------------------------ |
| Visual Studio Code              | 1.96.4                      |                           |
| Python                          | 3.12.5                      |                           |
| Python VSC Extension            | 2024.22.2                   |                           |
| pywinauto                       | 0.6.9                       |                           | 
| Pytest                          | 8.3.4                       |                           |
| Faker                           | 35.2.0                      |                           |
| pytest-html                     | 4.1.1                       |                           |
| Cmder                           | 1.3.25                      |                           |
| mitmproxy                       | 12.0.0                      |                           |
| mitmproxy windows certificate   | 3                           |                           |    
| mitmproxy plugin                | 12.0.0                      |                           |    

# Installation:

- See [Visual Studio Code page](https://code.visualstudio.com/) and install the latest VSC stable version. Keep all the prefereced options as they are until you reach the possibility to check the checkboxes below: 
  - :white_check_mark: Add "Open with code" action to Windows Explorer file context menu. 
  - :white_check_mark: Add "Open with code" action to Windows Explorer directory context menu.
Check then both to add both options in context menu.
- See [python page](https://www.python.org/downloads/) and download the latest Python stable version. Start the installation and check the checkboxes below: 
  - :white_check_mark: Use admin privileges when installing py.exe 
  - :white_check_mark: Add python.exe to PATH
and keep all the other preferenced options as they are.
- Look for Python in the extensions marketplace and install the one from Microsoft.
- See [Cmder | Console Emulator page](https://cmder.app/), donwload the latest Mini version and unzip it in C:\pywinauto-and-mitmproxy-expandtesting_desktop. 
- See [mitmproxy page](https://mitmproxy.org/), download and execute the downloaded file to install. :point_right: **Next**, :point_right: **Install** and :point_right: **Finish**.
  - If there is the need to work with mitmproxy in the terminal, on Windows tool bar, :mag: **proxy**, :point_right: **Proxy Configurations**, :point_right: **Set up** on Use a proxy server frame, :point_right: **Use a proxy server**, :point_right: **Use a proxy server**, type **localhost** and **8080** on Proxy IP address and Port fields respectively and :point_right: **Save**. This proxy configs should be deactivated when running the tests, since test scripts already take care of such configuration. 
  - See [Install mitmproxy's Certificate Authority page](http://mitm.it/) and download the windows one. Execute it, :point_right: **Next**, :point_right: **Next**, :point_right: **Next**, :point_right: **Next**, :point_right: **Finish**, :point_right: **Yes** and :point_right: **Ok**. Remember to undo this step after testing. 
  - Execute ```mitmproxy``` to start mitmproxy, type **f** and type **expandtesting** to filter traffic according to our needs.
- Open windows prompt as admin and execute ```pip install pywinauto``` to install PyAutoGUI.
- Open windows prompt as admin and execute ```pip install pytest``` to install Pytest.
- Open windows prompt as admin and execute ```pip install psutil``` to install psutil.
- Open windows prompt as admin and execute ```pip install Faker``` to install Faker library.
- Open windows prompt as admin and execute ```pip install pytest-html``` to install pytest-html plugin.
- Open windows prompt as admin and execute ```pip install mitmproxy``` to install mitmproxy plugin.

# Tests:

- Execute ```pytest ./tests -v --html=./reports/report.html``` to run tests in verbose mode and generate a report inside reports folder.
- Execute ```pytest .\tests\api\notes_api_test.py -k create_note -v --html=./reports/report.html``` to run tests that contains "create_note" in its structure inside notes_api_test.py file in verbose mode and generate a report inside reports folder.

# Support:

- [expandtesting API documentation page](https://practice.expandtesting.com/notes/api/api-docs/)
- [pywinauto](https://pypi.org/project/pywinauto/)
- [open CMD](https://github.com/pywinauto/pywinauto/issues/559)
- [Windows Desktop Automation Dengan Python PyWinAuto](https://www.youtube.com/playlist?list=PL8q4s70ndvwf3h_3px7s0X-7xGv7zXbwc)
- [ChatGPT](https://chatgpt.com/)
- [pytest](https://pypi.org/project/pytest/)
- [psutil](https://pypi.org/project/psutil/)
- [Faker](https://pypi.org/project/Faker/)
- [pytest-html](https://pypi.org/project/pytest-html/)
- [Reusing output from last command in Bash [duplicate]](https://stackoverflow.com/a/48398357)
- [os](https://docs.python.org/3/library/os.html)
- [json](https://docs.python.org/3/library/json.html)
- [random](https://docs.python.org/3/library/random.html)
- [Installing and getting started with MITMproxy, on Windows 11](https://www.youtube.com/watch?v=MgbVy2PJ52c)
- [mitmproxy](https://pypi.org/project/mitmproxy/)

# Tips:

- API tests to send password reset link to user's email and to verify a password reset token and reset a user's password must be tested manually as they rely on e-mail verification.
- Execute ```mitmproxy``` to start mitmproxy.