import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Borrower:

    id: str
    full_name: str
    passport_number: str
    passport_series: str
    birth_date: datetime
    income: float
    expenses: float
    credit_history_score: int  # 0-100
    existing_loans: float
    employment_years: int
    employer_name: str
    position: str
    address: str
    phone: str
    email: Optional[str] = None
    blacklisted: bool = False
    blacklist_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None

    @classmethod
    def create_new(cls, full_name: str, passport_number: str, passport_series: str,
                   birth_date: datetime, income: float, expenses: float,
                   credit_history_score: int, existing_loans: float,
                   employment_years: int, employer_name: str, position: str,
                   address: str, phone: str, email: str = "", created_by: str = None):
        """Создание нового заемщика"""
        return cls(
            id=str(uuid.uuid4()),
            full_name=full_name,
            passport_number=passport_number,
            passport_series=passport_series,
            birth_date=birth_date,
            income=income,
            expenses=expenses,
            credit_history_score=credit_history_score,
            existing_loans=existing_loans,
            employment_years=employment_years,
            employer_name=employer_name,
            position=position,
            address=address,
            phone=phone,
            email=email,
            created_by=created_by
        )

    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            "id": self.id,
            "full_name": self.full_name,
            "passport_number": self.passport_number,
            "passport_series": self.passport_series,
            "birth_date": self.birth_date.isoformat(),
            "income": self.income,
            "expenses": self.expenses,
            "credit_history_score": self.credit_history_score,
            "existing_loans": self.existing_loans,
            "employment_years": self.employment_years,
            "employer_name": self.employer_name,
            "position": self.position,
            "address": self.address,
            "phone": self.phone,
            "email": self.email,
            "blacklisted": self.blacklisted,
            "blacklist_reason": self.blacklist_reason,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Создание из словаря"""
        return cls(
            id=data["id"],
            full_name=data["full_name"],
            passport_number=data["passport_number"],
            passport_series=data["passport_series"],
            birth_date=datetime.fromisoformat(data["birth_date"]),
            income=data["income"],
            expenses=data["expenses"],
            credit_history_score=data["credit_history_score"],
            existing_loans=data["existing_loans"],
            employment_years=data["employment_years"],
            employer_name=data["employer_name"],
            position=data["position"],
            address=data["address"],
            phone=data["phone"],
            email=data.get("email"),
            blacklisted=data.get("blacklisted", False),
            blacklist_reason=data.get("blacklist_reason"),
            created_at=datetime.fromisoformat(data["created_at"]),
            created_by=data.get("created_by")
        )