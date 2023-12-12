import email

class MailboxReader():
    def __init__(self, file_handle):
        """A reader for mailbox files.
    
        If the file_handle input is a string, it opens the file. Otherwise,
        it assumes it's a file handle.

        The class can be used as a context manager in a "with" statement.
    
        Arguments:
            file_handle: A file handle to the mailbox file.
        """
        if type(file_handle) == str:
            self.file = open(file_handle)
            self.local_handle = True
        else:
            self.file = file_handle

    @property
    def messages(self):
        """Reads messages from the mailbox file.
        
        Yields:
            email.message.Message: An email message object.
        """
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
        """Closes the file handle."""
        self.file.close()

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        """Closes the file handle when exiting a with statement if it was
           opened by this object."""
        if self.local_handle:
            self.close()
