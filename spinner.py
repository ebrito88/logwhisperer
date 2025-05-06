import threading
import sys
import time

class Spinner:
    def __init__(self, message="Processing"):
        self._running = False
        self._thread = None
        self.message = message

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._spin)
        self._thread.start()

    def _spin(self):
        while self._running:
            for c in "|/-\\":
                sys.stdout.write(f"\r{self.message}... {c}")
                sys.stdout.flush()
                time.sleep(0.1)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        sys.stdout.write("\r" + " " * 40 + "\r")  # clear line

