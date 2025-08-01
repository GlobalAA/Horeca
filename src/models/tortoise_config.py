from src.config import config

TORTOISE_ORM = {
	"connections": {
		"default": config.db_url.get_secret_value(), 
	},
	"apps": {
		"models": {
			"models": ["src.models.models", "aerich.models"],  
			"default_connection": "default",
		},
	},
}