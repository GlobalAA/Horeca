from enum import Enum, IntEnum


class UserRoleEnum(Enum):
	ADMIN = "ADMIN"
	EMPLOYER = "employer"
	SEEKER = "seeker"
	USER = "USER"

class CommunicationMethodEnum(Enum):
	TelegramCommunication = "Телеграм"
	PhoneCommunication = "Номер телефону"

class CityEnum(Enum):
	ODESA = "Одеса"
	KYIV = "Київ"
	LVIV = "Львів"
	KHARKIV = "Харків"
	DNIPRO = "Дніпро"

class DistrictEnum(Enum):
	ALL = ("Усі", -1)
	PRYMORSKYI = ("Приморський", 1)
	KYIVSKYI = ("Київський", 1)
	MALYNOVSKYI = ("Малиновський", 1)
	SUVOROVSKYI = ("Суворовський", 1)
	
	PODILSKYI = ("Подільський", 2)
	SHEVCHENKIVSKYI = ("Шевченківський", 2)
	DNIPROVSKYI = ("Дніпровський", 2)
	SOLOMIANSKYI = ("Солом'янський", 2)
	OBOLONSKYI = ("Оболонський", 2)
	HOLOTSIIVSKYI = ("Голосіївський", 2)
	
	ARKHARIVSKYI = ("Адрміністівський", 3)
	ANANIVSKYI = ("Ананьївський", 3)
	HALYTSKYI = ("Галицький", 3)
	ZALIZNYCHNYI = ("Залізничний", 3)
	LYCHAKIVSKYI = ("Личаківський", 3)
	SIKHIVSKYI = ("Сихівський", 3)
	FRANKIVSKYI = ("Франківський", 3)

	KHOLODNOGIRSKYI = ("Холодногірський", 4)
	NEMYSHLIANSKYI = ("Немишлянський", 4)
	INDUSTRIALNYI_KH = ("Індустріальний", 4)
	OLEKSIIVSKYI = ("Олексіївський", 4)
	SLBIDSKYI = ("Слобідський", 4)

	ZHOVTNEVYI = ("Жовтневий", 5)
	SAMARSKYI = ("Самарський", 5)
	INDUSTRIALNYI_DP = ("Індустріальний", 5)
	SOBORNYYI = ("Соборний", 5)
	TARAMSKYI = ("Таромський", 5)

class AgeGroupEnum(IntEnum):
	AGE_18 = 18
	AGE_25 = 25
	AGE_30 = 30
	AGE_35 = 35
	AGE_40 = 40
	AGE_45 = 45
	AGE_60 = 60

class RateTypeEnum(Enum):
	PRECENT = "Відсоток"
	RATE = "Ставка"
	PRECENT_RATE = "Ставка + відсоток"

class ExperienceEnum(Enum):
	NO_EXPERIENCE = "Без досвіду"
	UP_TO_1_YEAR = "До 1 року"
	ONE_TO_TWO_YEARS = "1-2 роки"
	TWO_TO_THREE_YEARS = "2-3 роки"
	THREE_TO_FIVE_YEARS = "3-5 років"
	
class ExperienceTypeEnum(Enum):
	NAME = "NAME"
	VACANCY = "VACANCY"
	SKIP = "SKIP"

class VocationEnum(Enum):
	BARMAN = "Бармен"
	MANAGER = "Менеджер"
	WAITER = "Офіціант"
	HOSTESS = "Хостес"
	CASHIER = "Касир"
	PURCHASER = "Закупник"
	HOOKAH = "Кальянник"
	COOK = "Кухар"
	PORTO = "Порто"
	CLEANER = "Прибиральниця"
	SECURITY = "Охорона"
	ACCOUNTANT = "Бухгалтер"


class SubvocationEnum(Enum):
	BARMAN = ("Бармен", 1)
	BARBEK = ("Барбек", 1)
	BARMAN_HOOKAH = ("Бармен-кальянник", 1)

	MANAGER = ("Менеджер", 2)
	ADMINISTRATOR = ("Адміністратор", 2)
	HEAD_MANAGER = ("Керуючий", 2)

	WAITER = ("Офіціант", 3)
	WAITER_BARMAN = ("Офіціант-бармен", 3)
	WAITER_HOOKAH = ("Офіціант-кальянник", 3)
	WAITER_CASHIER = ("Офіціант-касир", 3)

	COOK_HELPER = ("Помічник повара", 8)
	COLD_KITCHEN = ("Кухар холодного цеху", 8)
	HOT_KITCHEN_8 = ("Кухар гарячого цеху", 8)
	UNIVERSAL_COOK = ("Кухар-універсал", 8)
	SUSHI_CHEF = ("Сушист", 8)
	PIZZAIOLO = ("Піцайоло", 8)
	GRILL_MASTER = ("Мангальщик", 8)
	COOK_DISTRIBUTION = ("Кухар видач", 8)
	CONFECTIONER = ("Кондитер", 8)
	SOUS_CHEF = ("Су-шеф", 8)
	HEAD_CHEF = ("Шеф-кухар", 8)

	PORTO = ("Порто", 9)
	PORTO_WHITE = ("Порто білого посуду", 9)
	PORTO_BLACK = ("Порто чорного посуду", 9)


class PriceOptionEnum(Enum):
	FREE = "free"
	ONE_DAY = "ONE DAY"
	ONE_WEEK = "ONE WEEK"
	VIP = "VIP"
	VIP_PLUS = "VIP_PLUS"
	VIP_MAX = "VIP_MAX"
	VIEW_COMMENTS = "VIEW_COMMENTS"
	RESUME_SUB = "RESUME SUB"

class EditCvEnum(Enum):
	VACATION = "VACATION"
	SALARY = "SALARY"
	PHONE_NUMBER = "PHONE_NUMBER"

class SliderValue:
	NEXT = "next"
	BACK = "back"

class ResumeSliderEnum(Enum):
	NEXT = SliderValue.NEXT
	BACK = SliderValue.BACK

class VocationSliderEnum(Enum):
	NEXT = SliderValue.NEXT
	BACK = SliderValue.BACK