from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    currency: str = Field(min_length=3, max_length=3)
    opening_balance: Decimal = Decimal("0")

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class AccountResponse(AccountCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    is_archived: bool


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    kind: str
    icon: str | None = Field(default=None, max_length=20)

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, value: str) -> str:
        if value not in {"income", "expense"}:
            raise ValueError("kind must be income or expense")
        return value


class CategoryResponse(CategoryCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str


class TransactionCreate(BaseModel):
    account_id: str
    category_id: str | None = None
    type: str
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    description: str = Field(default="", max_length=500)
    transaction_date: date
    notes: str | None = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, value: str) -> str:
        if value not in {"income", "expense"}:
            raise ValueError("type must be income or expense")
        return value

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class TransactionResponse(TransactionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str


class SummaryResponse(BaseModel):
    from_date: date
    to_date: date
    income: Decimal
    expenses: Decimal
    net: Decimal
    transaction_count: int
