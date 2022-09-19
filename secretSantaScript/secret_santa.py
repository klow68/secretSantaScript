# Import
import configparser, csv
import os
import random

from typing import List
from dataclasses import dataclass
from enum import IntEnum

# EMAIL
import jinja2
import smtplib, ssl, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

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
    name: str
    email: str
    address: str

    def __str__(self):
        if hasattr(self, "gift_to"):
            return f"{self.name} -> {self.gift_to.name}"
        return f"{self.name}"


# properties
p_properties = None

# read the properties file for csv, email... properties
def set_properties():
    global p_properties
    config = configparser.RawConfigParser()
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


class SecretSanta:
    p_participants: List[Human] = list()

    def start(self):
        self._init()

        self._parse()
        self._shuffle()

        self._generate_email_by_id()
        self._send_all_emails()

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

    # SECRET SANTA
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
        # spoiler alert, run this command to see the result like a human being
        print(*self.p_participants, sep="\n")

    def _get_human(self, id):
        for participant in self.p_participants:
            if participant.id == id:
                return participant

    # TEMPLATE
    def _generate_email_by_id(self):
        now = datetime.datetime.now()

        templateLoader = jinja2.FileSystemLoader(
            searchpath=p_properties["email"]["TemplateFolder"]
        )
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(p_properties["email"]["Template"])

        for human in self.p_participants:
            human.mail = template.render(
                name=human.name,
                date=now,
                adresse=human.gift_to.address,
                gift_to=human.gift_to.name,
            )

        return human.mail

    # EMAIL
    def _send_all_emails(self):
        ...
        email_from = p_properties["email"]["Name"]
        password = p_properties["email"]["Password"]
        smtp = p_properties["email"]["Smtp"]
        tls_port = p_properties["email"]["Tls_port"]
        for human in self.p_participants:
            email_to = human.email
            self._send_email(email_from, email_to, password, smtp, tls_port, human.mail)

    def _send_email(self, email_from, email_to, password, smtp, tls_port, html):

        # Create a MIMEMultipart class, and set up the From, To, Subject fields
        email_message = MIMEMultipart("related")
        email_message["From"] = email_from
        email_message["To"] = email_to
        email_message["Subject"] = p_properties["email"]["Subject"]

        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        email_message.attach(MIMEText(html, "html"))

        email_message.attach(
            self._get_MIME_image(p_properties["email"]["Image"], "santa")
        )
        email_message.attach(
            self._get_MIME_image(p_properties["email"]["Image2"], "footer")
        )

        # Convert it as a string
        email_string = email_message.as_string()

        # Connect to the Gmail SMTP server and Send Email
        context = ssl.create_default_context()
        with smtplib.SMTP(smtp, tls_port) as server:
            server.ehlo()  # Can be omitted
            server.starttls(context=context)
            server.ehlo()  # Can be omitted
            server.login(email_from, password)
            server.sendmail(email_from, email_to, email_string)

    def _get_MIME_image(self, image, cid: str):
        with open(image, "rb") as file:
            image = file.read()

        msgImage = MIMEImage(image)
        msgImage.add_header("Content-ID", f"<{cid}>")
        msgImage.add_header("X-Attachment-Id", cid)
        return msgImage


def main():

    ss = SecretSanta()
    ss.start()


if __name__ == "__main__":
    main()  # next section explains the use of sys.exit
