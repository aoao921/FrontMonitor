import multiprocessing
import os
import signal
import sys
import time
import psutil
import win32gui
import win32process
import subprocess
from datetime import datetime


def get_process_id_by_name(process_name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return process.info['pid']


def get_process_id_from_window_title(title):
    handle = win32gui.FindWindow(None, title)
    thread_id, process_id = win32process.GetWindowThreadProcessId(handle)
    return process_id


def monitor_foreground_process():
    current_window = win32gui.GetForegroundWindow()
    current_window_name = win32gui.GetWindowText(current_window)
    pid = get_process_id_from_window_title(current_window_name)
    return pid


if __name__ == '__main__':

    process_list = ['Wireshark.exe', 'wc32.exe', 'Fiddler.exe']
    current_monitored_process = ''
    current_monitor_id = -1
    # 无限循环
    while True:
        # 遍历进程列表
        for process_name in process_list:
            flag = 0
            current_monitor_id = -1
            target_id = get_process_id_by_name(process_name)
            # print("target_id",target_id)
            if target_id and monitor_foreground_process() == target_id:
                current_monitored_process = monitor_foreground_process()
                # print("while True:",current_monitored_process)
                ffmpeg_path = os.path.join(os.getcwd(), "bin", "ffmpeg.exe")
                output_file = process_name + '_' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.mp4'
                output_path = os.path.join(os.getcwd(), "output")
                if not os.path.exists(output_path):
                    # 如果不存在，创建目标文件夹
                    os.makedirs(output_path)
                    print(f"Created folder: {output_path}")
                else:
                    print(f"Folder already exists: {output_path}")
                output_file = output_path + '\\' + output_file
                print(output_file)
                cmd = f"{ffmpeg_path} -f gdigrab -i desktop -c:v libx264 -crf 0 -preset ultrafast {output_file}"
                # print(cmd)
                print("创建进程")
                proc = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                print("start Record")
                current_monitor_id = proc.pid
                # 阻塞在这个地方
                print(current_monitor_id)
                while monitor_foreground_process() == target_id:
                    continue
                flag = 1
            if current_monitor_id != -1 and flag == 1:
                proc.stdin.write('q'.encode("GBK"))
                proc.communicate()
                proc.kill()
                time.sleep(5)
                print("Screen recording generate.")

        time.sleep(2)

