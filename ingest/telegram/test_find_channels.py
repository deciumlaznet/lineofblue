import unittest
from find_channels import shortlist, proposed_sources
from connector import load_sources
import json, tempfile


class FindChannels(unittest.TestCase):
    FOUND = [("uk news", {"broadcast": True, "username": "UKNewsDesk", "title": "UK News Desk", "subscribers": 900}),
             ("breaking uk", {"broadcast": True, "username": "uknewsdesk", "title": "UK News Desk", "subscribers": 900}),
             ("uk news", {"broadcast": False, "username": "UKChatGroup", "title": "A group", "subscribers": 5000}),
             ("uk news", {"broadcast": True, "username": None, "title": "Private channel", "subscribers": 7000}),
             ("uk riots", {"broadcast": True, "username": "BigChannel", "title": "Big", "subscribers": 20000})]

    def test_keeps_only_public_broadcast_channels_deduped_largest_first(self):
        rows = shortlist(self.FOUND)
        self.assertEqual([r["channel"] for r in rows], ["BigChannel", "UKNewsDesk"])
        self.assertEqual(rows[1]["terms"], ["uk news", "breaking uk"])

    def test_drops_ukraine_and_cyrillic_matches(self):
        found = [("uk news", {"broadcast": True, "username": "ukrpravda_news", "title": "Українська правда", "subscribers": 9}),
                 ("uk police", {"broadcast": True, "username": "PCU_PoliceControlUkraine", "title": "Police Control Ukraine", "subscribers": 9}),
                 ("uk news", {"broadcast": True, "username": "ukbreaking", "title": "UK breaking news", "subscribers": 9})]
        self.assertEqual([r["channel"] for r in shortlist(found)], ["ukbreaking"])

    def test_proposals_are_valid_but_not_approved(self):
        src = proposed_sources(shortlist(self.FOUND))
        self.assertTrue(all(s["status"] == "proposed" and s["mode"] == "channel" for s in src))
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump({"sources": src}, f)
        self.assertEqual(len(load_sources(f.name)), 2)


if __name__ == "__main__":
    unittest.main()
