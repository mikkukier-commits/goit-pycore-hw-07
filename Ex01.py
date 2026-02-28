from collections import UserDict
from datetime import datetime, timedelta


class Field:
    """ Базовий клас для полів контактів."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Клас для зберігання імені контакту."""
    pass


class Phone(Field):
    """ Клас для номера телефону телефону з валідацією."""

    def __init__(self, value: str):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Номер телефону повинен містити 10 цифр.")
        super().__init__(value)


class Birthday(Field):
    """Клас для зберігання дати народження з валідацією."""

    def __init__(self, value: str):
        try:
            date_value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(date_value)


class Record:
    """Клас для зберігання запису контакту, який містить ім'я та список телефонів."""

    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str) -> None:
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> bool:
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return True
        return False

    def edit_phone(self, old_phone: str, new_phone: str) -> bool:
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return True
        return False

    def find_phone(self, phone: str) -> str | None:
        for p in self.phones:
            if p.value == phone:
                return p.value
        return None

    def add_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)

    def __str__(self) -> str:
        birthday = (
            self.birthday.value.strftime("%d.%m.%Y")
            if self.birthday
            else "Not set"
        )
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {birthday}"


class AddressBook(UserDict):
    """ Клас адресної книги"""

    def add_record(self, record: Record) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        return self.data.get(name)

    def get_upcoming_birthdays(self) -> list:
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value.date()

                # Обробка 29.02
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

                if 0 <= (birthday_this_year - today).days <= 7:
                    upcoming.append(record.name.value)

        return upcoming


def input_error(func):
    """ Декоратор для обробки помилок введення користувача."""
    def inner(*args):
        try:
            return func(*args)
        except (ValueError, IndexError):
            return "Invalid input."
        except KeyError:
            return "Contact not found."
    return inner


def parse_input(user_input):
    """ Функція для розбору введення користувача на команду та аргументи."""
    cmd, *args = user_input.split()
    return cmd.lower(), args


@input_error
def add_contact(args, book):
    """ Функція для додавання нового контакту або оновлення існуючого."""
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    """ Зміна першого номера телефону контакту на новий."""
    name, new_phone = args
    record = book.find(name)

    if record is None or not record.phones:
        raise KeyError

    old_phone = record.phones[0].value
    record.edit_phone(old_phone, new_phone)
    return f"{name}'s phone number {old_phone} was updated to {new_phone}."


@input_error
def show_phone(args, book):
    """ Функція для показу номерів телефону контакту."""
    name = args[0]
    record = book.find(name)

    if record is None:
        raise KeyError

    return "; ".join(p.value for p in record.phones)


def show_all(book):
    """ Функція для показу всіх контактів в адресній книзі."""
    if not book.data:
        return "No contacts found."
    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book):
    """ Функція для додавання дати народження до контакту."""
    name, birthday = args
    record = book.find(name)

    if record is None:
        raise KeyError

    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    """ Функція для показу дати народження контакту."""
    name = args[0]
    record = book.find(name)

    if record is None or record.birthday is None:
        raise KeyError

    return record.birthday.value.strftime("%d.%m.%Y")


def birthdays(book):
    """Функція для показу контактів з найближчими днями народження."""
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."

    lines = []
    today = datetime.now().date()

    for name in upcoming:
        try:
            record = book.find(name)
            bd = record.birthday.value
            bd_date = bd.date()

            # Обробка 29.02
            try:
                next_bd = bd_date.replace(year=today.year)
            except ValueError:
                next_bd = bd_date.replace(year=today.year, day=28)

            if next_bd < today:
                try:
                    next_bd = bd_date.replace(year=today.year + 1)
                except ValueError:
                    next_bd = bd_date.replace(year=today.year + 1, day=28)

            days_left = (next_bd - today).days

            lines.append(
                f"{name} — {bd_date.strftime('%d.%m.%Y')} ({days_left} days left)"
            )

        except KeyError:
            lines.append(f"{name} — Birthday not set")

    return "\n".join(lines)


def main():
    """Головна функція для запуску бота."""
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("Hello, how can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()
