import phonenumbers


def normalize_phone_number(raw_phone: str) -> str | None:
    try:
        phone = phonenumbers.parse(raw_phone)  # Библиотека сама определит страну
        if phonenumbers.is_valid_number(phone):
            return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        return None
