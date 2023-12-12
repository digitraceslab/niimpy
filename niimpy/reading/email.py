import email

class MailboxReader():
    def __init__(self, file_handle):
        if type(file_handle) == str:
            self.file = open(file_handle)
        else:
            self.file = file_handle

    @property
    def messages(self):
        lines = []
        while True:
            line = self.file.readline()
            
            if line.startswith(b'From ') or line == b'':
                if lines:
                    message = email.message_from_bytes(b''.join(lines))
                    yield(message)
                
                if line == b'':
                    break
                
                lines = [line]

            lines.append(line)

    def close(self):
        self.file.close()

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.close()
