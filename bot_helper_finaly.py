from newclasses import Record, Name, Phone, Birthday, AddressBook, Iterator
import re


STOP_LIST = ("good bye", "close", "exit")
FILE_PATH = "./address.book"

address_book = AddressBook()


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact or phone number not found."
        except (IndexError, AttributeError):
            return "Wrong command."
        except ValueError:
            return "The entered data is incorrect."
    return inner


def user_input_split(user_input):
    matches = re.match(r'\w+\s+(\D+)\s([+]?\d{7,15})', user_input)
    if matches:
        name = Name(matches.group(1))
        phone = Phone(matches.group(2))
        return name, phone
    else:
        return "No data."


def handle_hello():
    return "Good day. How can I help?"


@input_error
def handle_add(*args):
    args = args[0].split(' ')
    name = Name(args[1])
    birthday = ''
    record = Record(name, birthday=birthday)
    if len(args) >= 4:
        match = re.match(
            r"^([0-9]{2})[\\\/\-\., ]?([0-9]{2})[\\\/\-\., ]?([0-9]{4})$", args[-1])
        if bool(match):
            birthday = Birthday(args[-1])
            record = Record(name, birthday=birthday)
            for p in args[2:-1]:
                phone = Phone(p)
                record.add_phone(phone)
        else:
            for p in args[2:]:
                phone = Phone(p)
                record.add_phone(phone)
    else:
        phone = Phone(args[2])
        record.add_phone(phone)
    if str(name) not in address_book.data.keys():
        address_book.add_record(record)
        address_book.serialize(FILE_PATH)
    else:
        current_rec = address_book.data[str(name)].phones
        for p in record.phones:
            if p in current_rec:
                current_rec.remove(p)
        address_book.update_record(record)
        address_book.serialize(FILE_PATH)
    return f"Name: {str(name)}\n{address_book.data[str(name)]}\n"


@input_error
def handle_change(user_input):
    matches = re.match(
        r'\w+\s+(\D+)\s([+]?\d{7,15})\s([+]?\d{7,15})', user_input)
    name, old_phone, new_phone = matches.group(1), Phone(
        matches.group(2)), Phone(matches.group(3))
    if name in address_book.data.keys():
        record = address_book.data[name]
        record.change_phone(old_phone, new_phone)
        address_book.add_record(record)
        address_book.serialize(FILE_PATH)
        return f"Contact {name} has been changed. New phone number {new_phone}.\n"
    else:
        raise KeyError


@input_error
def handle_delete(user_input):
    matches = re.match(r'\w+\s+(\D+)\s([+]?\d{7,15})', user_input)
    if matches:
        name, phone = matches.group(1), matches.group(2)
    if name in address_book.data.keys():
        record = address_book.data[name]
        record.delete_phone(phone)
        if record.phones:
            address_book.add_record(record)
            address_book.serialize(FILE_PATH)
        else:
            del address_book.data[name]
            address_book.serialize(FILE_PATH)
        return f"Contact {name} has been changed. Phone number {phone} has been deleted.\n"
    else:
        return f"The phone number {phone} was not found for the contact {name}.\n"


@input_error
def handle_phone(user_input):
    name = re.match(r'\w+\s+(\D+)', user_input).group(1)
    if name in address_book.data.keys():
        return f"Contact {name}: {address_book.data[name]}\n"
    else:
        raise KeyError


@input_error
def handle_search(user_input):
    search_str = re.match(r'\w+\s+(\w+)$', user_input).group(1)
    search_results = address_book.search(search_str)
    if search_results:
        return search_results
    else:
        print("No matching contacts found.")


@input_error
def handle_birthday(user_input):
    name = re.match(r'\w+\s+(\D+)', user_input).group(1)
    if name in address_book.data.keys():
        record = address_book.data[name]
        days = record.days_to_birthday()
        return f"There are {days} days until {name}'s birthday. Birthday {record.birthday}\n"
    else:
        raise KeyError


def handle_showall():
    if not address_book.data:
        return "The contact book is empty."
    else:
        iterator = Iterator(address_book)
        for record in iterator:
            print(record)
            try:
                input("Press 'Enter' to continue\n")
            except KeyboardInterrupt:
                break
    return "End\n"


def commands(user_input):
        if user_input.lower() == "Good day!":
            response = handle_hello()
        elif re.search(r"^add ", user_input, re.IGNORECASE):
            response = handle_add(user_input)
        elif re.search(r"^change ", user_input, re.IGNORECASE):
            response = handle_change(user_input)
        elif re.search(r"^delete ", user_input, re.IGNORECASE):
            response = handle_delete(user_input)
        elif re.search(r"^phone ", user_input, re.IGNORECASE):
            response = handle_phone(user_input)
        elif re.search(r"^birthday ", user_input, re.IGNORECASE):
            response = handle_birthday(user_input)
        elif re.search(r"^search ", user_input, re.IGNORECASE):
            response = handle_search(user_input)
        elif user_input.lower() == "show all":
            response = handle_showall()
        else:
            response = "Wrong command."
        if response:
            print(response)


def main():
    try:
        address_book.deserialize(FILE_PATH)
    except FileNotFoundError:
        print("Data file not found. A new address book has been created.")

    while True:
        user_input = input("Please enter the command: ")
        if user_input in STOP_LIST:
            address_book.serialize(FILE_PATH)
            print("The data is saved. Goodbye!")
            break
        else:
            commands(user_input)


if __name__ == "__main__":
        main()
