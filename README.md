# COMP3901_Bookworm
Chatbot that is able to answer questions about a document.

INSTRUCTIONS FOR RUNNING THE APP

1. Ensure that your editor and or terminal is run as administrator. (Note --> I find it easier to use the terminal already built in the editor)
2. Ensure that python is installed on your computer. If it isn't, you may download it here --> https://www.python.org/downloads/
3. Clone the repository and navigate to the folder using the terminal.
4. Once in the folder, type the following commands.
    a)    python -m venv venv
    b)   ./venv/Scripts/activate
    c)    pip install -r requirements.txt
    d)    flask --app app --debug run
    **If an error occurs that looks like this --> “...cannot be loaded because running scripts is disabled on this system” follow these steps.
        1. Open start and search powershell and run it as administrator
        2. If already at \WINDOWS\system32 you may enter this command --> Set-ExecutionPolicy RemoteSigned
        2.b. (Skip if you were already at \WINDOWS\system32) To navigate to system32 enter the following then proceed with step 2.
            --> cd \
            --> cd .\Windows\System32\
        3. Enter Y to accept
        4. Go back to your terminal where you received the error and re-enter your last command.
5. Click on http://127.0.0.1:8080 or copy and paste it in your browser to view the webpage.
6**. To stop the server at anytime you can press 'ctrl c' . That would re-enable typing commands.
    -->Additionally to run the server again just type the command at step'4.d.' again.