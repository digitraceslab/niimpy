import os

from niimpy import config
import niimpy.reading.email as email_utils



def test_MailboxReader():
    filename = os.path.join(config.GOOGLE_TAKEOUT_DIR, "Takeout/Mail/All mail Including Spam and Trash.mbox")

    with email_utils.MailboxReader(filename) as mailbox:
        messages = list(mailbox.messages)
        
        assert messages[0]["From"] == "Jarno Rantaharju <jarno.rantaharju@aalto.fi>"
        assert messages[0]["To"] == "example2 <example2@example.com>"

        assert messages[1]["From"] == "Jarno Rantaharju <jarno.rantaharju@aalto.fi>"
        assert messages[1]["To"] == "example <example@example.com>, example2 <example2@example.com>"

        assert messages[0].get_payload() == "Hello! This is a happy message!\n\n"


def test_strip_address():
    stripped = email_utils.strip_address("example examplesdottir <example@example.com>")
    assert stripped == "example@example.com"


def test_parse_address_list():
    as_string = "example <example@example.com>, example2 <example2@example.com>, , example2 <example2@example.com>"
    as_list = email_utils.parse_address_list(as_string)
    assert as_list[0] == "example@example.com"
    assert as_list[1] == "example2@example.com"

    assert email_utils.parse_address_list("") == []
