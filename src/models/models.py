from tortoise import fields
from tortoise.contrib.postgres.fields import ArrayField
from tortoise.models import Model

from .enums import (AgeGroupEnum, CityEnum, CommunicationMethodEnum,
                    ExperienceEnum, PriceOptionEnum, RateTypeEnum,
                    UserRoleEnum, VocationEnum)


def empty_list():
	return []

class User(Model):
	id = fields.IntField(pk=True)
	user_id = fields.BigIntField(unique=True)
	username = fields.CharField(max_length=255, null=True)
	full_name = fields.CharField(max_length=255)
	role = fields.CharEnumField(UserRoleEnum)
	balance = fields.FloatField()
	last_msg_id = fields.IntField(default=0)
	
	on_week = fields.IntField(default=0)
	created_at = fields.DatetimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f'{self.user_id} | {self.username}'
	
class Subscriptions(Model):
	id = fields.IntField(pk=True)
	status = fields.CharEnumField(PriceOptionEnum, default=PriceOptionEnum.FREE)
	time_expired = fields.DatetimeField(null=True)

	user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
		"models.User", related_name="subscriptions"
	)
	
class Vacancies(Model):
	id = fields.IntField(pk=True)
	user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
		"models.User", related_name="vacancies"
	)
	address = fields.CharField(max_length=255)
	name = fields.CharField(max_length=255)
	work_schedule = fields.CharField(max_length=255)
	issuance_salary = fields.CharField(max_length=255)
	vocation = fields.CharEnumField(VocationEnum)
	subvocation = fields.CharField(max_length=255, null=True)
	age_group = fields.IntEnumField(AgeGroupEnum)
	experience = fields.CharEnumField(ExperienceEnum)
	city = fields.CharEnumField(CityEnum)
	district = fields.CharField(max_length=255)
	rate = fields.CharField(max_length=255)
	rate_type = fields.CharEnumField(RateTypeEnum)
	salary = fields.IntField()
	phone_number = fields.CharField(max_length=255, null=True)
	telegram_link = fields.CharField(max_length=255, null=True)
	photo_id = fields.CharField(max_length=255, null=True)
	communications = fields.CharEnumField(CommunicationMethodEnum)
	published = fields.BooleanField(default=False)
	resume_sub = fields.BooleanField(default=False)
	cvs_id = ArrayField("int", default={})
	
	time_expired = fields.DatetimeField(null=True)

class ExperienceVacancy(Model):
	id = fields.IntField(pk=True)
	
	experience = fields.CharEnumField(ExperienceEnum)
	name = fields.CharField(max_length=255)
	rating = fields.IntField(default=0)
	vacancy: fields.ForeignKeyNullableRelation[Vacancies] = fields.ForeignKeyField(
		"models.Vacancies", related_name="epv", null=True
	)
	cv_user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
		"models.User", related_name="cv_user"
	)
	
class CVs(Model):
	id = fields.IntField(pk=True)
	user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
		"models.User", related_name="cvs"
	)
	city = fields.CharEnumField(CityEnum)
	district = fields.CharField(max_length=255)
	vocation = fields.CharEnumField(VocationEnum)
	subvocation = fields.CharField(max_length=255, null=True)
	age_group = fields.IntEnumField(AgeGroupEnum)
	experience: fields.ForeignKeyRelation[ExperienceVacancy] = fields.ForeignKeyField(
		"models.ExperienceVacancy", related_name="ev"
	)
	min_salary = fields.IntField()
	desired_salary = fields.IntField()
	phone_number = fields.CharField(max_length=255)
	photo_id = fields.CharField(max_length=255, null=True)
	published = fields.BooleanField(default=False)
	vacancies_ids = ArrayField("int", default={})