from config import config


def get_min_price() -> int:
	return min(value for _, value in config.price_options)