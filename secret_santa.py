# Import
import csv, random, smtplib, datetime, email

# Import the email modules we'll need
from email.message import EmailMessage

#### CSV GLOBAL VARIABLES ####

# csv : id;foyer;nom;email;adresse
csv_id = 0
csv_foyer = 1
csv_nom = 2
csv_email = 3
csv_adresse = 4

#### GLOBAL VARIABLES ####

# list of all participant with all there informations
p_contacts = []
# list of id/foyer by participant
p_id_foyer = []
# CSV column names
p_column_name = []
# secret santa result by id [id sender, id gift]
p_secret_santa_res_id = []

# email to send all email
p_email_secret_santa = "<your@email.com>"

# open csv file and put it in the global variable p_contacts
def open_csv():
    global p_contacts
    with open("./res/contacts.csv", newline="") as csvfile:
        contact = csv.reader(csvfile, delimiter=";", quotechar="|")
        for row in contact:
            p_contacts += [row]


def cut_first_contacts_line():
    global p_contacts, p_column_name
    p_column_name = p_contacts.pop(0)


def get_all_id_foyer():
    global p_contacts, p_id_foyer, csv_id, csv_foyer
    for row in p_contacts:
        p_id_foyer += [[row[csv_id], row[csv_foyer]]]


# function to found a contact to offer a gift
# return id or -1
def gift_to_offer(contact, contacts):
    global csv_foyer, csv_id

    # exit condition : if no contact anymore
    if len(contacts) == 0:
        return None
    else:
        # get random contact and remove it from contacts list
        random.shuffle(contacts)
        gift_to = contacts.pop()

        # if contact found
        if contact[csv_foyer] != gift_to[csv_foyer]:
            return gift_to  # found a solution to send answer

        # Restart again with a list without this contact
        gift_to_offer(contact, contacts)


def secret_santa():
    global p_id_foyer, p_secret_santa_res_id, csv_foyer, csv_id

    secret_santa_finished = False

    while not secret_santa_finished:
        # Init
        cp_id_foyer = p_id_foyer.copy()
        p_secret_santa_res_id = []

        # for all contact found a contact to offer a gift not in your foyer
        for contact in p_id_foyer:
            id = gift_to_offer(contact, cp_id_foyer.copy())

            # result found
            if id != None:
                # p_secret_santa_res_id += [[contact, id]]
                p_secret_santa_res_id += [[contact[csv_id], id[csv_id]]]
                # pop contact in result
                cp_id_foyer.remove(id)
            # restart because no result found
            else:
                break

        # Secret Santa finished :)
        if len(cp_id_foyer) == 0:
            secret_santa_finished = True


def get_contact_by_id(id_contact):
    global p_contacts
    for contact in p_contacts:
        if contact[csv_id] == id_contact:
            return contact
    return []


def send_email():
    global p_contacts, p_secret_santa_res_id, csv_id, csv_foyer, csv_adresse, csv_email, csv_nom, p_email_secret_santa

    now = datetime.datetime.now()

    for secret in p_secret_santa_res_id:
        sender = get_contact_by_id(secret[0])
        gift_to = get_contact_by_id(secret[1])

        print("Gift : ")
        print(sender)
        print(gift_to)

        message = (
            "Salut "
            + sender[csv_nom]
            + "!\n\nTon Secret Santa de cette annee "
            + str(now.year)
            + "\nTu devra donc un cadeau a "
            + gift_to[csv_nom]
            + "\n\n--Pere Noel secret"
        )

        msg = email.message_from_string(message)

        msg["From"] = p_email_secret_santa
        msg["To"] = sender[csv_email]
        msg["Subject"] = "Secret Santa"

        s = smtplib.SMTP("smtp.office365.com", 587)
        s.ehlo()  # Hostname to send for this command defaults to the fully qualified domain name of the local host.
        s.starttls()  # Puts connection to SMTP server in TLS mode
        s.ehlo()
        s.login(p_email_secret_santa, "<email_password>")

        s.sendmail(p_email_secret_santa, sender[csv_email], msg.as_string())

        s.quit()


def main():
    #### MAIN ####

    # initialize csv variables
    open_csv()
    cut_first_contacts_line()
    print("CSV")
    print(p_column_name)
    print("Contacts")
    print(p_contacts)

    # get id/foyer
    get_all_id_foyer()
    print("id/foyer : ")
    print(p_id_foyer)

    # secretsanta algo
    secret_santa()
    print("\nres id/id gift to")
    print(p_secret_santa_res_id)

    # print/email creation
    send_email()


if __name__ == "__main__":
    # execute only if run as a script
    main()
