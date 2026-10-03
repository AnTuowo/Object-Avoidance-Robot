from PyQt5.QtCore import QProcess
import os
import signal


def pause_process(process: QProcess):
    pid = process.processId()
    if pid:
        os.kill(pid, signal.SIGSTOP)

def resume_process(process: QProcess):
    pid = process.processId()
    if pid:
        os.kill(pid, signal.SIGCONT)

def cancel_process(process: QProcess):
        process.kill()




class ProcessManager:
    def __init__(self):
        self.process_list = None
        self.current_index = 0
        self.running_process = None


    def execute(self, processes: list):
        self.process_list = processes
        self.current_index = 0
        self.start_next

    def start_next(self):
        if self.current_index < len(self.process_list):
            self.running_process = self.process_list[self.current_index]
            self.current_index += 1
            
            # Connect the finished signal to automatically start the next one
            self.running_process.finished.connect(self.start_next)
            self.running_process.start()
        else:
            print("All processes completed.")

    def pause_current(self):
        if self.running_process and self.running_process.state() == QProcess.Running:
            # Use the OS-specific pause code discussed previously
            pause_process(self.running_process)

    def resume_current(self):
        if self.running_process:
            resume_process(self.running_process)

    def cancel_process(self):
        self.process_list = None
        self.running_process.terminate()
        self.running_process = None

