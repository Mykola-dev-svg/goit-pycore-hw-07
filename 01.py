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
            raise ValueError("Назва не може бути пустою")
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
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name, None)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f"Запис з назвою {name} не знайдено")

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

