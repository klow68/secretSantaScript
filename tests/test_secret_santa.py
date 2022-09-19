import pytest
from secretSantaScript.secret_santa import CSV_COLUMNS, read_csv, set_properties


class TestSecretSanta:

    p_csv_header = ["id", "foyer", "nom", "email", "adresse"]

    def setUp(self):
        """Call before every test case."""
        print("start")

    def tearDown(self):
        """Call after every test case."""
        print("done")

    def test_read_properties(self):
        properties = set_properties()
        assert "csv" in properties
        assert "email" in properties
        assert (
            properties["csv"]["FileName"]
            == "./secretSantaScript/resources/contacts/contacts.csv"
        )
        assert properties["email"]["subject"] == "[Secret Santa] test é%test"

    def test_column_order(self):
        assert CSV_COLUMNS.ID == 0

    @pytest.mark.parametrize(
        "contact_id,expected",
        [
            (
                0,
                [
                    "0",
                    "0",
                    "Prenom1 N",
                    "test2@yopmail.fr",
                    "12 allée des test 56789 JOJO",
                ],
            ),
            (
                1,
                [
                    "1",
                    "0",
                    "Prenom2 N",
                    "test2@yopmail.fr",
                    "12 allée des test 56789 JOJO",
                ],
            ),
        ],
    )
    def test_read_csv(self, contact_id, expected):
        csv_header, contacts = read_csv(
            "./secretSantaScript/resources/contacts/contacts_test.csv"
        )

        assert csv_header == self.p_csv_header
        assert contacts[contact_id] == expected
