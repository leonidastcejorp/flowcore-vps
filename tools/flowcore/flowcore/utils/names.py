"""
Identity Generator
==================
Generates realistic identity data for form automation.
Provides names, emails, usernames, and passwords.
"""
import random
import string

FIRST_NAMES = [
    'Ahmad', 'Budi', 'Citra', 'Dewi', 'Eko', 'Fitri', 'Gunawan', 'Hendra',
    'Indah', 'Joko', 'Kurnia', 'Lestari', 'Mega', 'Nurul', 'Oka', 'Putri',
    'Rizky', 'Sari', 'Teguh', 'Utami', 'Vina', 'Wahyu', 'Yuli', 'Zainal',
    'Agus', 'Bayu', 'Catur', 'Dimas', 'Elsa', 'Farhan',
    'John', 'Mike', 'Sarah', 'Emma', 'David', 'Lisa', 'Alex', 'Anna',
    'James', 'Kate', 'Mia', 'Noah', 'Olivia', 'Liam', 'Sophia', 'Ethan',
]

LAST_NAMES = [
    'Pratama', 'Wijaya', 'Kusuma', 'Saputra', 'Hidayat', 'Nugroho',
    'Santoso', 'Prabowo', 'Susanto', 'Hartono', 'Gunawan', 'Wibowo',
    'Siregar', 'Nasution', 'Hutapea', 'Sinaga', 'Simanjuntak',
    'Smith', 'Johnson', 'Brown', 'Williams', 'Jones', 'Garcia', 'Miller',
    'Davis', 'Wilson', 'Moore', 'Taylor', 'Anderson', 'Thomas',
]

EMAIL_DOMAINS = [
    'gmail.com', 'yahoo.com', 'outlook.com', 'proton.me',
    'mail.com', 'icloud.com', 'live.com',
]


def random_name():
    """Generate a random full name"""
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def random_username(name=None):
    """Generate a random username from a name or randomly"""
    if not name:
        name = random_name()
    num = random.randint(100, 9999)
    clean = name.lower().replace(' ', '').replace("'", '')
    return f"{clean}{num}"


def random_email(name=None):
    """Generate a random email address"""
    if not name:
        name = random_name()
    base = name.lower().replace(' ', '.').replace("'", '')
    num = random.randint(1, 999)
    domain = random.choice(EMAIL_DOMAINS)
    return f"{base}{num}@{domain}"


def random_password(length=16):
    """Generate a secure random password"""
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(random.choices(chars, k=length))
