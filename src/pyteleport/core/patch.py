import os
import subprocess

class Patch:
    def __init__(self, old_file: str, new_file: str):
        self.old_file = old_file
        self.new_file = new_file

    
    def diff(self):
        subprocess.run(['git', 'diff', '--no-index', self.old_file, self.new_file], check=True)

    def apply(self):
        subprocess.run(['patch', self.old_file, self.new_file], check=True)

    
    def remove(self):
        os.remove(self.new_file)