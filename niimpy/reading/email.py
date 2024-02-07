import email
import re

'''
Contains a reader for mailbox files, MailboxReader, and utility functions for parsing
email addresses. Read from the mailbox.

The MailboxReader class functions as a context manager that opens a mailbox file. The
messages property returns an iterator of email.message objects.

The strip_address function returns the first actual email address contained in a string
and the parse_address_list returns a list of addresses in a comma separated list.
'''

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
            self.local_handle = False

    @property
    def messages(self):
        """Reads messages from the mailbox file.
        
        Yields:
            email.message.Message: An email message object.
        """
        lines = []

        for line in self.file:
            if isinstance(line, bytes):
                if line.startswith(b'From '):
                    if lines:
                        message = email.message_from_bytes(b''.join(lines))
                        yield(message)
                        lines = [line]
            else:
                if line.startswith('From '):
                    if lines:
                        message = email.message_from_string(''.join(lines))
                        yield(message)
                        lines = [line]
            
            lines.append(line)
            
        # Handle last message
        if lines:
            if isinstance(lines[0], bytes):
                message = email.message_from_bytes(b''.join(lines))
            else:
                message = email.message_from_bytes(b''.join(lines))
            yield(message)

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


def parse_address_list(email_list_string):
    """ Parse a string containing a list of email addresses.
    
    Arguments
    ---------
      email_list_string: str
        A string of comma separated email addresses formatted as "name <address>"

    Returns
    ------
      List[str]
    """
    email_list = email_list_string.split(',')
    email_list = [strip_address(email) for email in email_list]
    email_list = [email for email in email_list if email != ""]
    return email_list


def strip_address(address_string):
    """ Strip the name part of an email address"""
    embedded_emails = re.findall(r'<(.*?)>', address_string)
    if len(embedded_emails):
        return embedded_emails[0]
    return address_string


def extract_content(message):
    content = ""
    for part in message.walk():
        if part.get_content_type() == "text/plain":
            payload = part.get_payload(decode=True)
            charset = part.get_content_charset()
            try:
                if charset:
                    content += payload.decode(charset)
                else:
                    content += payload.decode()
            except UnicodeDecodeError:
                # Failed to decode the string. Could use charder
                pass
            
    return content

