import base64
import unittest
from datetime import date
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from zoneinfo import ZoneInfo

from outbound_sender.sender import (
    FOOTER_MARKER,
    add_compliance_footer,
    generate_schedule,
    single_recipient,
)


class ScheduleTests(unittest.TestCase):
    def test_campaign_ramp_and_weekdays(self):
        slots = generate_schedule(398, date(2026, 7, 27))
        self.assertEqual(len(slots), 398)
        eastern = ZoneInfo("America/New_York")
        local_days = [slot.astimezone(eastern).date() for slot in slots]
        counts = {}
        for day in local_days:
            counts[day] = counts.get(day, 0) + 1
        ordered = list(counts.values())
        self.assertEqual(ordered[:3], [10, 15, 20])
        self.assertTrue(all(value <= 25 for value in ordered))
        self.assertEqual(len(ordered), 18)
        self.assertTrue(all(day.weekday() < 5 for day in counts))

    def test_weekend_start_moves_to_monday(self):
        slots = generate_schedule(1, date(2026, 7, 26))
        eastern = ZoneInfo("America/New_York")
        self.assertEqual(slots[0].astimezone(eastern).date().isoformat(), "2026-07-27")


class RecipientTests(unittest.TestCase):
    def test_single_recipient(self):
        record = {
            "source_message_id": "one",
            "to": "Prospect <prospect@example.com>",
            "cc": None,
            "bcc": None,
        }
        self.assertEqual(single_recipient(record), "prospect@example.com")

    def test_no_recipient(self):
        record = {"source_message_id": "one", "to": None, "cc": None, "bcc": None}
        self.assertIsNone(single_recipient(record))


class FooterTests(unittest.TestCase):
    def make_message(self) -> bytes:
        message = EmailMessage()
        message["From"] = "Nate McGuire <nate@eastbayprojects.com>"
        message["To"] = "prospect@example.com"
        message["Subject"] = "A quick note"
        message.set_content("Hello there.")
        message.add_alternative("<html><body><p>Hello there.</p></body></html>", subtype="html")
        return message.as_bytes(policy=policy.SMTP)

    def test_adds_footer_and_unsubscribe_header_idempotently(self):
        address = "123 Example Street, Alexandria, VA 22314"
        once = add_compliance_footer(
            self.make_message(), address, "nate@eastbayprojects.com"
        )
        twice = add_compliance_footer(once, address, "nate@eastbayprojects.com")
        parsed = BytesParser(policy=policy.default).parsebytes(twice)
        plain = parsed.get_body(preferencelist=("plain",)).get_content()
        rendered_html = parsed.get_body(preferencelist=("html",)).get_content()
        self.assertEqual(plain.count("This is a business solicitation"), 1)
        self.assertEqual(rendered_html.count(FOOTER_MARKER), 1)
        self.assertIn(address, plain)
        self.assertIn("mailto:nate@eastbayprojects.com", parsed["List-Unsubscribe"])


if __name__ == "__main__":
    unittest.main()
