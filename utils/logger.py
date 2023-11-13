import os


class Logger:
    def __init__(self, path):
        self.fh = open(f"{os.environ['PYTHONPATH']}/{path}", "w")

    def __del__(self):
        self.fh.close()

    def log(self, msg, end="\n"):
        self.fh.write(f"{msg}{end}")
