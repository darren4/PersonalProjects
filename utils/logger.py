import os


class Logger:
    def __init__(self, path, print_msg=True):
        self.fh = open(f"{os.environ['PYTHONPATH']}/{path}", "w")

    def __del__(self):
        self.fh.close()

    def log(self, msg, end="\n"):
        print(msg, end=end)
        self.fh.write(f"{msg}{end}")
