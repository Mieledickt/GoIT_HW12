from collections import UserDict
from datetime import date
import re
import pickle


class Field:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return self.value == other.value and self.value == other.value

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value


class Name(Field):
    def __init__(self, value):
        self.name = value
        super().__init__(value=value)


class Phone(Field):
    def __init__(self, value=''):
        self.phone = value
        super().__init__(value=value)

    @Field.value.setter
    def value(self, new_value):
        if not self.is_valid_phone(new_value):
            while True:
                try:
                    new_value = input(
                        "Invalid phone number. Enter the correct number: ")
                    if self.is_valid_phone(new_value):
                        break
                except ValueError:
                      pass
        self._value = new_value

    def is_valid_phone(self, value):
        pattern = r'^(\+?[0-9]{1,3})[-. ]?(\(?[0-9]{1,4}\)?)[-. ]?([0-9]{1,3})[-. ]?([0-9]{1,4})$'
        match = re.match(pattern, str(value))
        return bool(match)


class Birthday(Field):
    def __init__(self, value=''):
        self.birthday = value
        super().__init__(value=value)

    @Field.value.setter
    def value(self, new_value):
        if not self.is_valid_birthday(new_value):
            while True:
                    try:
                        new_value = input(
                            "Invalid date of birth. Enter again: ")
                        if self.is_valid_birthday(new_value):
                            break
                    except ValueError:
                        pass
        self._value = self.is_valid_birthday(new_value)

    def is_valid_birthday(self, value):
        pattern = r"^([0-9]{2})[\\\/\-\., ]?([0-9]{2})[\\\/\-\., ]?([0-9]{4})$"
        match = re.match(pattern, value)
        if not match:
            return False
        else:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
        if not (1900 <= year <= 2100) or not (1 <= month <= 12):
            return False
        birthday = date(year, month, day)
        return birthday


class Record:
    def __init__(self, name, phones=None, birthday=None):
        self.name = name
        self.phones = phones if phones is not None else []
        self.birthday = birthday

    def add_phone(self, phone):
        if phone.value not in [p.value for p in self.phones]:
            self.phones.append(phone)

    def delete_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != str(phone)]

    def change_phone(self, old_phone, new_phone):
        index = [str(phone) for phone in self.phones].index(str(old_phone))
        self.phones[index] = new_phone

    def days_to_birthday(self):
        if self.birthday:
            today = date.today()
            comming_birthday = date(
                today.year, self.birthday.value.month, self.birthday.value.day)
        if comming_birthday < today:
            comming_birthday = date(
                today.year + 1, self.birthday.value.month, self.birthday.value.day)
        return (comming_birthday - today).days

    def __str__(self):
        return f"Birthday: {self.birthday}\nPhones: {self.phones}\n"

    def __repr__(self):
        return str(self)


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def update_record(self, record):
        if record.birthday:
            self.data[record.name.value].birthday = record.birthday
        self.data[record.name.value].phones.extend(record.phones)

    def serialize(self, file_path):
        with open(file_path, "wb") as file:
            pickle.dump(self.data, file)

    def deserialize(self, file_path):
        with open(file_path, "rb") as file:
            self.data = pickle.load(file)

    def search(self, search_str):
        results = {}
        for record in self.data.values():
            if search_str in str(record.name) or any(search_str in str(phone) for phone in record.phones):
                results[str(record.name)] = record
        return results


class Iterator:
    def __init__(self, address_book):
        self.address_book = address_book
        self.current_value = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_value < len(self.address_book):
            name = list(self.address_book.data.keys())[self.current_value]
            record = list(self.address_book.data.values())[self.current_value]
            self.current_value += 1
            return f"Name: {name}\n{record}"
        raise StopIteration("End")
