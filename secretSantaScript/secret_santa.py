# Import
import csv, random, smtplib, ssl, datetime, email, configparser
from typing import List
import string
from dataclasses import dataclass
from enum import IntEnum

# Import the email modules we'll need
from email.message import EmailMessage

#### CSV GLOBAL VARIABLES ####

# csv : id;foyer;nom;email;adresse
class CSV_COLUMNS(IntEnum):
    ID = 0
    FAMILLY = 1
    NAME = 2
    EMAIL = 3
    ADDRESS = 4


@dataclass
class Human:
    id: int
    familly: int
    name: string
    email: string
    address: string

    def __str__(self):
        if hasattr(self, "gift_to"):
            return f"{self.name} -> {self.gift_to.name}"
        return f"{self.name}"


# email to send all email
p_email_secret_santa = "<your@email.com>"

# properties
p_properties = None

# read the properties file for csv, email... properties
def set_properties():
    global p_properties
    config = configparser.ConfigParser()
    config.read("./secretSantaScript/resources/properties/properties.properties")
    p_properties = config
    return config


# open csv file and return the header with the contacts
def read_csv(input_file, sep=";"):
    with open(input_file, newline="") as csvfile:
        csv_data = csv.reader(csvfile, delimiter=sep, quotechar="|")
        header = next(csv_data)
        contacts = [row for row in csv_data]
    return header, contacts


def get_all_id_foyer(contacts):
    return [
        [contact[CSV_COLUMNS.ID], contact[CSV_COLUMNS.FAMILLY]] for contact in contacts
    ]


# function to found a contact to offer a gift
# return id or -1
def gift_to_offer(contact, contacts):
    # exit condition : if no contact anymore
    if len(contacts) == 0:
        return None
    else:
        # get random contact and remove it from contacts list
        random.shuffle(contacts)
        gift_to = contacts.pop()

        # if contact found
        if contact[CSV_COLUMNS.FAMILLY] != gift_to[CSV_COLUMNS.FAMILLY]:
            return gift_to  # found a solution to send answer

        # Restart again with a list without this contact
        gift_to_offer(contact, contacts)


def secret_santa_algo(foyers):
    secret_santa_finished = False

    while not secret_santa_finished:
        # Init
        cp_id_foyer = foyers.copy()
        p_secret_santa_res_id = []

        # for all contact found a contact to offer a gift not in your foyer
        for contact in foyers:
            foyer_id = gift_to_offer(contact, cp_id_foyer.copy())

            # result found
            if foyer_id != None:
                # p_secret_santa_res_id += [[contact, id]]
                p_secret_santa_res_id += [
                    [contact[CSV_COLUMNS.ID], foyer_id[CSV_COLUMNS.ID]]
                ]
                # pop contact in result
                cp_id_foyer.remove(foyer_id)
            # restart because no result found
            else:
                break

        # Secret Santa finished :)
        if len(cp_id_foyer) == 0:
            secret_santa_finished = True
    return p_secret_santa_res_id


"""
def get_contact_by_id(id_contact, contacts_data):
    for contact in contacts_data:
        if contact[CSV_COLUMNS.ID] == id_contact:
            return contact
    return []


def send_email(secret_santa_ids, csv_data):
    now = datetime.datetime.now()

    for secret in secret_santa_ids:
        sender = get_contact_by_id(secret[0], csv_data)
        gift_to = get_contact_by_id(secret[1], csv_data)

        print("Gift : ")
        print(f"Sender: {sender[CSV_COLUMNS.NAME]}")
        print(f"Receiver: {gift_to[CSV_COLUMNS.NAME]}")
        print()

        message = (
            "Salut "
            + sender[CSV_COLUMNS.NAME]
            + "!\n\nTon Secret Santa de cette annee "
            + str(now.year)
            + "\nTu devra donc un cadeau a "
            + gift_to[CSV_COLUMNS.NAME]
            + "\n\n--Pere Noel secret"
        )

        msg = email.message_from_string(message)

        msg["From"] = p_email_secret_santa
        msg["To"] = sender[CSV_COLUMNS.EMAIL]
        msg["Subject"] = "Secret Santa"

        # s = smtplib.SMTP("smtp.office365.com", 587)
        s.ehlo()  # Hostname to send for this command defaults to the fully qualified domain name of the local host.
        s.starttls()  # Puts connection to SMTP server in TLS mode
        s.ehlo()
        s.login(p_email_secret_santa, "<email_password>")

        # TODO seach if encoding in UTF8 is enought
        s.sendmail(p_email_secret_santa, sender[CSV_COLUMNS.EMAIL], msg.encode("utf8"))

        s.quit()
"""


class SecretSanta:
    p_participants: List[Human] = list()
    p_contacts: list()

    def start(self):
        self._init()
        self._parse()
        self._shuffle()

    def _init(self):
        set_properties()

    def _parse(self):
        header, contacts = read_csv(p_properties["csv"]["filename"], sep=";")
        self.contacts = contacts
        for participant in contacts:
            self.p_participants.append(
                Human(
                    participant[CSV_COLUMNS.ID],
                    participant[CSV_COLUMNS.FAMILLY],
                    participant[CSV_COLUMNS.NAME],
                    participant[CSV_COLUMNS.EMAIL],
                    participant[CSV_COLUMNS.ADDRESS],
                )
            )

    # should be done pretier, but it's working
    def _shuffle(self):
        # get id/foyer
        foyer_ids = get_all_id_foyer(self.contacts)
        print("id/foyer : ")
        print(foyer_ids)

        # secretsanta algo
        santa_res_ids = secret_santa_algo(foyer_ids)
        print("\nres id/id gift to")
        print(santa_res_ids)

        for res in santa_res_ids:
            human = self._get_human(res[0])
            human.gift_to = self._get_human(res[1])

    def spoiler(self):
        # spoiler alert, run this command to see the result you sheet
        print(*self.p_participants, sep="\n")

    def _get_human(self, id):
        for participant in self.p_participants:
            if participant.id == id:
                return participant

    def _generate_email_by_id(self):
        ...

    def _send_email(self):
        # TODO
        # send_email(santa_res_ids, contacts)
        ...


def main():

    ss = SecretSanta()
    ss.start()


if __name__ == "__main__":
    main()  # next section explains the use of sys.exit
