from collections import UserDict
import re
from datetime import datetime, timedelta

class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value: str):
        if not value:
            raise ValueError("Ім’я не може бути порожнім.")
        super().__init__(value)
        
class Phone(Field):
    def __init__(self, value: str):
        self.value = None
        self.set(value)
        
    def set(self, value: str):
        if not re.fullmatch(r'\d{10}',value):
            raise ValueError("Номер телефону має складатися рівно з 10 цифр")
        self.value = value

class Birthday(Field):
    def __init__(self, value: str):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Неправильний формат дати. Використовуйте DD.MM.YYYY")

class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))
        
    def remove_phone(self, phone: str):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError(f"Телефон {phone} не знайдено")

    def edit_phone(self, old_phone: str, new_phone: str):
        phone_obj = self.find_phone(old_phone)
        if phone_obj:
            phone_obj.set(new_phone)
        else:
            raise ValueError(f"Телефон {old_phone} не знайдено")

    def find_phone(self, phone: str):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.today().date()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones) if self.phones else "немає телефонів"
        birthday_str = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "не вказано"
        return f"Ім’я: {self.name.value}, телефони: {phones_str}, день народження: {birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name, None)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f"Запис з ім’ям {name} не знайдено")

    def get_upcoming_birthdays(self, days: int = 7):
        today = datetime.today().date()
        upcoming = {}
        for record in self.data.values():
            if record.birthday:
                next_bday = record.birthday.value.replace(year=today.year)
                if next_bday < today:
                    next_bday = next_bday.replace(year=today.year + 1)
                delta = (next_bday - today).days
                if 0 <= delta <= days:
                    upcoming[record.name.value] = next_bday.strftime("%d.%m.%Y")
        return upcoming

def input_error(func):
    def inner(args, book):
        try:
            return func(args, book)
        except ValueError as e:
            return f"Error: {str(e)}"
        except IndexError:
            return "Error: Недостатньо аргументів для виконання команди."
    return inner

def parse_input(user_input: str):
    parts = user_input.strip().split()
    command = parts[0].lower()
    args = parts[1:]
    return command, *args

@input_error
def add_contact(args, book):
    if len(args) < 2:
        return "Використання: add [ім'я] [номер]"
    name, phone = args[0], args[1]
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
        message = f"Контакт {name} створено."
    else:
        message = f"Контакт {name} оновлено."
    record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    if len(args) != 3:
        return "Використання: change [ім'я] [старий номер] [новий номер]"
    name, old_phone, new_phone = args
    record = book.find(name)
    if not record:
        return "Контакт не знайдено."
    record.edit_phone(old_phone, new_phone)
    return f"Номер {name} змінено."

@input_error
def show_phone(args, book):
    if len(args) != 1:
        return "Використання: phone [ім'я]"
    name = args[0]
    record = book.find(name)
    if not record:
        return "Контакт не знайдено."
    phones = "; ".join(p.value for p in record.phones)
    return f"{name}: {phones}"

@input_error
def show_all(args, book):
    if not book.data:
        return "Список контактів порожній."
    return "\n".join(str(record) for record in book.data.values())

@input_error
def add_birthday(args, book):
    if len(args) != 2:
        return "Використання: add-birthday [ім'я] [дата у форматі DD.MM.YYYY]"
    name, bday = args
    record = book.find(name)
    if not record:
        record = Record(name)
        book.add_record(record)
    record.add_birthday(bday)
    return f"День народження для {name} додано."

@input_error
def show_birthday(args, book):
    if len(args) != 1:
        return "Використання: show-birthday [ім'я]"
    name = args[0]
    record = book.find(name)
    if not record or not record.birthday:
        return "День народження не знайдено."
    return f"{name}: {record.birthday.value.strftime('%d.%m.%Y')}"

@input_error
def birthdays(args, book):
    result = book.get_upcoming_birthdays()
    if not result:
        return "Немає днів народження протягом наступного тижня."
    return "\n".join(f"{name}: {date}" for name, date in result.items())

def main():
    book = AddressBook()
    print("Вітаю! Я ваш помічник-бот!")

    while True:
        user_input = input("Введіть команду: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("До побачення!!")
            break
        elif command == "hello":
            print("Чим можу допомогти?")
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
            print(birthdays(args, book))
        else:
            print("Invalid command. Спробуйте ще раз.")


if __name__ == "__main__":
    main()
