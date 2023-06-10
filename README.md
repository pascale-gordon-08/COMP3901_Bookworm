# COMP3901_Bookworm
Chatbot that is able to answer questions about a document.

### INSTRUCTIONS TO GET STARTED
1. Ensure that your editor and or terminal is run as administrator. (Note --> I find it easier to use the terminal already built in the editor)
2. Ensure that python is installed on your computer. If it isn't, you may download it here --> [Download Python](https://www.python.org/downloads/) 
3. Using the terminal navigate to a folder you would like to have all your files.
4. Clone the repository then navigate to the cloned folder using these commands.
    ```bash
    git clone https://github.com/pascale-gordon-08/COMP3901_Bookworm.git
    cd COMP3901_Bookworm
    ```
5. Once in the folder, type the following commands.
    ```bash
    python -m venv venv
    ./venv/Scripts/activate
    pip install -r requirements.txt
    flask --app app --debug run
    ```
    ### In Case of Script Error
    
    If an error occurs that looks like this --> “...cannot be loaded because running scripts is disabled on this system” follow these steps.
    
        1. Open start and search powershell and run it as administrator
        2. If already at \WINDOWS\system32 you may enter this command --> Set-ExecutionPolicy RemoteSigned
        2.b. (Skip if already at \WINDOWS\system32) To navigate to system32 enter the following then proceed with this section's step 2.
            --> cd \
            --> cd .\Windows\System32\
        3. Enter Y to accept
        4. Go back to your terminal where you received the error and re-enter the last command that was typed before you got the error.
       
6. Click on the address that looks like this --> http://127.0.0.1:8080 or copy and paste it in your browser to view the webpage.
    ```
    To stop the server at anytime you can press 'ctrl c' . That would re-enable typing commands.
    Additionally, to run the server again just type the command 'flask --app app --debug run' again.
   ```
