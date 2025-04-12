import phonenumbers


def normalize_phone_number(raw_phone: str) -> str | None:
    try:
        phone = phonenumbers.parse(raw_phone, "RU")
        if phonenumbers.is_valid_number(phone):
            return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)  # +7XXXXXXXXXX
    except phonenumbers.NumberParseException:
        return None
