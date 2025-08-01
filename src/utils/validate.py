import re


def validate_phone_number(phone_number: str) -> bool:
	phone_pattern = re.compile(r"^(?:\+?38)?[\s\-]?\(?0\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$")

	return bool(re.match(phone_pattern, phone_number))

def validate_telegram_username(username: str):
	pattern = re.compile(r'^(?:@([a-zA-Z][a-zA-Z0-9_]{4,31})|https://t\.me/([a-zA-Z][a-zA-Z0-9_]{4,31})|t\.me/([a-zA-Z][a-zA-Z0-9_]{4,31}))$')
	return bool(pattern.match(username))

def percent_validate(rate: str, percent_with_rate: bool = False):
	if not percent_with_rate:
		pattern = re.compile(r'(?:100|[1-9]?\d)%')
		return bool(pattern.match(rate))
	else:
		pattern = re.compile(r'\d+\s+(?:100|[1-9]?\d)%')
		return bool(pattern.match(rate))