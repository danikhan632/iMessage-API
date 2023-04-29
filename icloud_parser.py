import re
import json

vcards = open("contacts.vcf","r").read()
def parse_vcards(vcards):
    contacts = {}
    vcard_list = re.split(r'BEGIN:VCARD\r?\n|END:VCARD', vcards)

    for vcard in vcard_list:
        if not vcard.strip():
            continue

        full_name_match = re.search(r'FN:(.+)', vcard)
        phone_number_match = re.search(r'TEL;[^:]+:(\+[\d\s\(\)-]+)', vcard)

        if full_name_match and phone_number_match:
            full_name = full_name_match.group(1).strip()
            phone_number = phone_number_match.group(1).strip()
            phone_number = re.sub(r'\D', '', phone_number)  # Remove all non-digit characters from the phone number
            phone_number= str("+") +phone_number 
            contacts[phone_number] = full_name

    return contacts

parsed_contacts = parse_vcards(vcards)
print(json.dumps(parsed_contacts, indent=2))
with open("contacts.json", "w") as f:
    json.dump(parsed_contacts, f, indent=4)