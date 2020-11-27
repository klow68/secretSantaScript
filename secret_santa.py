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

# email to send all email
p_email_secret_santa = "<your@email.com>"

# open csv file and put it in the global variable p_contacts
def open_csv():
    with open("./res/contacts.csv", newline="") as csvfile:
        csv_data = csv.reader(csvfile, delimiter=";", quotechar="|")
        header = next(csv_data)
        contacts = [row for row in csv_data]
    return header, contacts


def get_all_id_foyer(contacts):
    return [[contact[csv_id], contact[csv_foyer]] for contact in contacts]


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
        if contact[csv_foyer] != gift_to[csv_foyer]:
            return gift_to  # found a solution to send answer

        # Restart again with a list without this contact
        gift_to_offer(contact, contacts)
        
def secret_santa(foyers):
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
                p_secret_santa_res_id += [[contact[csv_id], foyer_id[csv_id]]]
                # pop contact in result
                cp_id_foyer.remove(foyer_id)
            # restart because no result found
            else:
                break

        # Secret Santa finished :)
        if len(cp_id_foyer) == 0:
            secret_santa_finished = True
    return p_secret_santa_res_id


def get_contact_by_id(id_contact, contacts_data):
    for contact in contacts_data:
        if contact[csv_id] == id_contact:
            return contact
    return []


def send_email(secret_santa_ids, csv_data):
    now = datetime.datetime.now()

    for secret in secret_santa_ids:
        sender = get_contact_by_id(secret[0], csv_data)
        gift_to = get_contact_by_id(secret[1], csv_data)

        print("Gift : ")
        print(f"Sender: {sender[csv_nom]}")
        print(f"Receiver: {gift_to[csv_nom]}")
        print()

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
    print("Récupération des données dans le CSV")
    csv_header, contacts = open_csv()
    print(csv_header)
    for contact in contacts:
        print(contact)
    # get id/foyer
    foyer_ids = get_all_id_foyer(contacts)
    print("id/foyer : ")
    print(foyer_ids)

    # secretsanta algo
    santa_res_ids = secret_santa(foyer_ids)
    print("\nres id/id gift to")
    print(santa_res_ids)

    # print/email creation
    send_email(santa_res_ids, contacts)


if __name__ == "__main__":
    # execute only if run as a script
    main()
