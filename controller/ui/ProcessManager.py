from __future__ import annotations
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
    def __init__(self, before_each_process: function = None, after_all_process = None):
        self.before_each = before_each_process
        self.after_all_done = after_all_process
        self.command_list = []
        self.current_index = 0
        self.running_process = QProcess()
        self.running_process.finished.connect(self.start_next)

    def execute(self, commands: list[dict]):
        self.command_list = commands
        self.current_index = 0
        self.start_next()

    def build_process(self, args: dict):
        self.running_process.setProgram(args.get("program"))
        self.running_process.setArguments(args.get("arguments"))

    def start_next(self):
        if self.current_index < len(self.command_list):
            if self.before_each:
                self.before_each()
            self.build_process(self.command_list[self.current_index])
            self.current_index += 1
            self.running_process.start()
        else:
            if self.after_all_done:
                self.after_all_done()

    def pause_current(self):
        if self.running_process and self.running_process.state() == QProcess.Running:
            # Use the OS-specific pause code discussed previously
            pause_process(self.running_process)

    def resume_current(self):
        if self.running_process:
            resume_process(self.running_process)

    def cancel_process(self):
        cancel_process(self.running_process)
        self.after_all_done()
        self.command_list.clear()

def build_command_dict(program: str, *args: str):
    arguments = []
    for arg in args:
        arguments.append(arg)
    return {"program": program, "arguments": arguments}