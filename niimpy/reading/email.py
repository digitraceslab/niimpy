from zipfile import ZipFile
import email

class MailboxREader():
    def __init__(self, file_handle):
        if type(file_handle) == str:
            self.file = open(file_handle)
        else:
            self.file = file_handle

    def messages(self):
        lines = []
        while True:
            line = self.file.readline()
            if line == b'' or line.startswith(b'From '):
                if lines:
                    message = email.message_from_bytes(b''.join(lines))
                    yield message
                if line == b'':
                    break
                lines = []
            lines.append(line)

    def close(self):
        self.file.close()

