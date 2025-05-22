from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0)
    category: str
    description: Optional[str]
    expense_date: date

    @field_validator("expense_date")
    def validate_date(cls, v):
        if v > date.today():
            raise ValueError("Expense date cannot be in the future")
        return v

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str]
    description: Optional[str]
    expense_date: Optional[date]

class ExpenseOut(ExpenseCreate):
    id: int
    created_at: datetime
