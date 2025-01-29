from faker import Faker
from faker_enum import EnumProvider


fake = Faker()
fake.add_provider(EnumProvider)


def fake_username():
    return fake.user_name()


def fake_phone_number():
    return fake.phone_number()


def fake_email():
    return fake.email()
