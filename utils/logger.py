class Logger:
    def __init__(self, path, print_msg=True):
        self.fh = open(path, "w")
        self.print_msg = print_msg

    def __del__(self):
        self.fh.close()

    def log(self, msg, end="\n"):
        if self.print_msg:
            print(msg, end=end)
        self.fh.write(f"{msg}{end}")
