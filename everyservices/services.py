import re


def clean_phone(phone):
    clear_phone = re.findall(r"\d+", phone)[0]
    if clear_phone.startswith("8"):
        clear_phone = re.sub("8", "7", clear_phone, 1)
    return clear_phone