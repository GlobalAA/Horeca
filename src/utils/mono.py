from enum import Enum
from typing import TypedDict, Union

import aiohttp

from config import config

TOKEN = config.monobank_token.get_secret_value()


class MonoBankApi:
	class Status(Enum):
		CREATED = "created"
		PROCESSING = "processing"
		SUCCESS = "success"
		FAILURE = "failure"
		REVERSED = "reversed"
		EXPIRED = "expired"
		NONE = "NONE"

	class ErrorDict(TypedDict):
		success: bool
		errCode: str
		errText: str

	SuccessDict = TypedDict("SuccessDict", {"success": bool})

	def __init__(self, token: str) -> None:
		self.TOKEN = token
		self.headers = {
			'X-Token': token
		}
		self.session: aiohttp.ClientSession | None = None

	async def __aenter__(self):
		self.session = aiohttp.ClientSession(headers=self.headers)
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		if self.session:
			await self.session.close()

	async def get_invoice_status(self, invoice_id: str) -> tuple[Status, dict[str, str]]:
		url = "https://api.monobank.ua/api/merchant/invoice/status"
		params = {"invoiceId": invoice_id}

		async with self.session.get(url, params=params) as response:
			data = await response.json()
			if response.status != 200:
				return self.Status.NONE, {
					'errCode': data['errCode'],
					'errText': data['errText']
				}

			self.invoice_id = data['invoiceId']
			status = self.Status(data['status'])

			match status:
				case self.Status.SUCCESS:
					return await self.success_status(data)
				case self.Status.FAILURE:
					return await self.failure_status(data)
				case self.Status.PROCESSING:
					return await self.processing_status(data)
				case self.Status.EXPIRED:
					return await self.expired_status()
				case _:
					return status, {}


	async def success_status(self, data: dict) -> tuple[Status, dict[str, str]]:
		return self.Status.SUCCESS, {
			"bank":  data['paymentInfo']['bank'],
			"paymentSystem": data['paymentInfo']['paymentSystem'],
			"maskedPan": data['paymentInfo']['maskedPan'],
			"amount": data['amount'] / 100,
			"reference": data['reference'],
			"destination": data['destination']
		}

	async def failure_status(self, data: dict) -> tuple[Status, dict[str, str]]:
		return self.Status.FAILURE, {
			"bank":  data['paymentInfo']['bank'],
			"paymentSystem": data['paymentInfo']['paymentSystem'],
			"maskedPan": data['paymentInfo']['maskedPan'],
			"amount": data['amount'] / 100,
			"failureReason": data['failureReason']
		}

	async def processing_status(self, data: dict) -> tuple[Status, dict[str, str]]:
		return self.Status.PROCESSING, {
			"bank":  data['paymentInfo']['bank'],
			"paymentSystem": data['paymentInfo']['paymentSystem'],
			"maskedPan": data['paymentInfo']['maskedPan'],
			"amount": data['amount'] / 100,
			"reference": data['reference'],
			"destination": data['destination']
		}

	async def expired_status(self) -> tuple[Status, dict[str, str]]:
		return self.Status.EXPIRED, {}
			
	async def create_invoice(self, data: dict):
		url = "https://api.monobank.ua/api/merchant/invoice/create"
		async with self.session.post(url, json=data) as response:
			return await response.json()
		
	async def invalidate_invoice(self, invoice_id: str) -> Union[SuccessDict, ErrorDict]:
		url = "https://api.monobank.ua/api/merchant/invoice/remove"
		async with self.session.post(url, json={"invoiceId": invoice_id}) as response:
			if response.status == 200:
				return {
					"success": True
				}

			data = await response.json()
			return {
				"success": False,
				"errCode": data["errCode"],
				"errText": data["errText"]
			}