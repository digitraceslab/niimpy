from zipfile import ZipFile
import email

class MailboxREader():
    def __init__(self, file_handle):
        if type(file_handle) == str:
            self.file = open(file_handle)
        else:
            self.file = file_handle

        self.lines = []
        self.is_done = False

    def __next__(self):
        while not self.is_done:
            line = self.file.readline()
            if line == b'' or line.startswith(b'From '):
                if line == b'':
                    self.is_done = True
                if self.lines:
                    message = email.message_from_bytes(b''.join(self.lines))
                    self.lines = [line]
                    return message
            
            self.lines.append(line)

    def close(self):
        self.file.close()

