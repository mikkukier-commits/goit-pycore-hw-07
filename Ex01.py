from datetime import datetime, date


def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except KeyError:
            return "Contact not found."
        except ValueError:
            return "Invalid input."
        except IndexError:
            return "Give me name and phone please."
    return inner


class Field:
    def __init__(self, value):
        self.value = value


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            date_value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError
        super().__init__(date_value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = Phone(new_phone).value
                return True
        return False

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        birthday = (
            self.birthday.value.strftime("%d.%m.%Y")
            if self.birthday
            else "No birthday"
        )
        return f"{self.name.value}: {phones}, Birthday: {birthday}"


class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming = []

        for record in self.data.values():
            if not record.birthday:
                continue

            birthday = record.birthday.value.date()

            try:
                birthday_this_year = birthday.replace(year=today.year)
            except ValueError:
                birthday_this_year = birthday.replace(
                    year=today.year, day=28
                )

            if birthday_this_year < today:
                try:
                    birthday_this_year = birthday.replace(
                        year=today.year + 1
                    )
                except ValueError:
                    birthday_this_year = birthday.replace(
                        year=today.year + 1, day=28
                    )

            days_left = (birthday_this_year - today).days

            if 0 <= days_left <= 7:
                upcoming.append(
                    f"{record.name.value} — "
                    f"{birthday_this_year.strftime('%d.%m.%Y')} "
                    f"({days_left} days left)"
                )

        return upcoming


@input_error
def add_contact(args, book):
    name, phone = args
    record = book.find(name)

    if record is None:
        record = Record(name)
        book.add_record(record)

    record.add_phone(phone)
    return "Contact added."


@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)

    if record is None:
        raise KeyError

    if not record.edit_phone(old_phone, new_phone):
        raise ValueError

    return "Phone updated."


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)

    if record is None:
        raise KeyError

    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)

    if record is None or record.birthday is None:
        raise KeyError

    return record.birthday.value.strftime("%d.%m.%Y")


def show_all(book):
    if not book.data:
        return "No contacts."
    return "\n".join(str(record) for record in book.data.values())


def birthdays(book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(upcoming)


def parse_input(user_input):
    parts = user_input.split()
    command = parts[0]
    args = parts[1:]
    return command, args


def main():
    book = AddressBook()

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            record = book.find(args[0])
            if record:
                print("; ".join(p.value for p in record.phones))
            else:
                print("Contact not found.")

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()