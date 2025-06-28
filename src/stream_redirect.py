import sys
from gi.repository import GLib

class StreamRedirect:
    def __init__(self, write_callback, also_print=True):
        self.write_callback = write_callback
        self.also_print = also_print
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

    def start(self):
        sys.stdout = self
        sys.stderr = self

    def stop(self):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

    def write(self, message):
        for line in message.splitlines():
            if line.strip():
                GLib.idle_add(self.write_callback, line)
                if self.also_print:
                    self._original_stdout.write(line + '\n')

    def flush(self):
        pass
