from typing import Optional

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
	last_vacancy_name = fields.CharField(max_length=255, null=True, default=None)
	
	on_week = fields.IntField(default=0)
	created_at = fields.DatetimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f'{self.user_id} | {self.username}'
	
class PaymentHistory(Model):
	id = fields.IntField(pk=True)

	payment_type = fields.CharEnumField(PriceOptionEnum)
	amount = fields.IntField()
	invoice_id = fields.CharField(max_length=255, null=True)
	created_at = fields.DatetimeField(auto_now_add=True)

	user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
		"models.User", related_name="history"
	)
	
class Subscription(Model):
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
	subvocation: Optional[str] = fields.CharField(max_length=255, null=True) #type: ignore
	age_group = fields.IntEnumField(AgeGroupEnum)
	experience = fields.CharEnumField(ExperienceEnum)
	city = fields.CharEnumField(CityEnum)
	district = fields.CharField(max_length=255)
	rate = fields.CharField(max_length=255)
	rate_type = fields.CharEnumField(RateTypeEnum)
	salary = fields.IntField()
	additional_information: Optional[str] = fields.CharField(max_length=255, null=True) #type: ignore
	phone_number: Optional[str] = fields.CharField(max_length=255, null=True) #type: ignore
	telegram_link: Optional[str] = fields.CharField(max_length=255, null=True) #type: ignore
	photo_id = fields.CharField(max_length=255, null=True)
	communications = fields.CharEnumField(CommunicationMethodEnum)
	published = fields.BooleanField(default=False)
	resume_sub = fields.BooleanField(default=False)
	bonus = fields.BooleanField(default=False)
	cvs_id = ArrayField("int", default={})
	
	time_expired = fields.DatetimeField(null=True)

class CVs(Model):
	id = fields.IntField(pk=True)
	user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
		"models.User", related_name="cvs"
	)
	experience_enum = fields.CharEnumField(ExperienceEnum, null=True)
	city = fields.CharEnumField(CityEnum)
	district = fields.CharField(max_length=255)
	vocation = fields.CharEnumField(VocationEnum)
	subvocation = fields.CharField(max_length=255, null=True)
	age_group = fields.IntEnumField(AgeGroupEnum)

	min_salary = fields.IntField()
	desired_salary = fields.IntField()
	phone_number = fields.CharField(max_length=255)
	photo_id = fields.CharField(max_length=255, null=True)
	published = fields.BooleanField(default=False)
	vacancies_ids = ArrayField("int", default={})


class ExperienceVacancy(Model):
	id = fields.IntField(pk=True)
	
	name = fields.CharField(max_length=255, null=True)
	city = fields.CharEnumField(CityEnum, null=True)
	district = fields.CharField(max_length=255, null=True)
	vocation = fields.CharEnumField(VocationEnum, null=True)
	subvocation = fields.CharField(max_length=255, null=True)
	rate = fields.CharField(max_length=255, null=True)
	age_group = fields.IntEnumField(AgeGroupEnum, null=True)
	salary = fields.IntField(null=True)
	phone_number = fields.CharField(max_length=255, null=True)
	telegram_link = fields.CharField(max_length=255, null=True)
	photo_id = fields.CharField(max_length=255, null=True)
	communications = fields.CharEnumField(CommunicationMethodEnum, null=True)
	work_schedule = fields.CharField(max_length=255, null=True)
	issuance_salary = fields.CharField(max_length=255, null=True)
	rating = fields.IntField(default=0)
	
	user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
		"models.User", related_name="user"
	)
	cv: fields.ForeignKeyRelation[CVs] = fields.ForeignKeyField(
		"models.CVs", related_name="cv", on_delete=fields.CASCADE
	)
class Comment(Model):
	id = fields.IntField(pk=True)
	author = fields.CharField(max_length=255)
	text = fields.TextField()
	created_at = fields.DatetimeField(auto_now_add=True)
	
	experience: fields.ForeignKeyRelation[ExperienceVacancy] = fields.ForeignKeyField(
		"models.ExperienceVacancy",
		related_name="comments",
		on_delete=fields.CASCADE
	)