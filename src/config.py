import logging
from pathlib import Path

from pydantic import BaseModel, SecretStr
from pydantic_settings import SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings

logger = logging.getLogger('scraper')
ROOT_DIR = Path(__file__).parent.parent

class PriceOptionConfig(BaseModel):
	ONE_DAY: int
	ONE_WEEK: int
	RESUME_SUB: int
	VIEW_COMMENTS: int
	VIP: int
	VIP_PLUS: int
	VIP_MAX: int

class Redis(BaseModel):
	username: str
	password: SecretStr
	host: str
	port: int
	
class Config(YamlBaseSettings):
	bot_token: SecretStr
	db_url: SecretStr 
	redis: Redis
	monobank_token: SecretStr

	price_options: PriceOptionConfig

	model_config = SettingsConfigDict(
		yaml_file=ROOT_DIR  / "config.yaml",
		env_file_encoding='utf-8',
		secrets_dir='.'
	)

	
config = Config() #type: ignore