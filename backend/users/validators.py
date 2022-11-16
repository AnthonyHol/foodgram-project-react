import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if re.search(r"^[a-zA-Z0-9_-]{3,16}$", value) is None or value == "me":
        raise ValidationError(
            (f"Не допустимый username: <{value}>!"),
            params={"value": value},
        )
