import phonenumbers

def normalize_phone_number(raw_phone: str) -> str | None:
    try:
        if raw_phone.startswith('+'):
            phone = phonenumbers.parse(raw_phone, None)  # None = автоопределение по коду страны
        else:
            phone = phonenumbers.parse(raw_phone, "RU")  # Локальные без + считаем как RU

        if phonenumbers.is_valid_number(phone):
            return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.E164)

    except phonenumbers.NumberParseException:
        return None