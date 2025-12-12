import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from .enums import CreditStatus


@dataclass
class AnalysisResult:

    max_loan_amount: float
    credit_attractiveness: str
    risk_level: str
    recommendations: List[str]
    score: int

    def to_dict(self):
        return {
            "max_loan_amount": self.max_loan_amount,
            "credit_attractiveness": self.credit_attractiveness,
            "risk_level": self.risk_level,
            "recommendations": self.recommendations,
            "score": self.score
        }


@dataclass
class CreditReport:
    id: str
    borrower_id: str
    borrower_name: str
    max_loan_amount: float
    credit_attractiveness: str
    risk_level: str
    status: CreditStatus
    created_by: str
    created_by_name: str
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    modified_by: Optional[str] = None
    modified_by_name: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    blacklist_check: bool = False
    blacklist_found: bool = False
    score: int = 0
    notes: Optional[str] = None

    @classmethod
    def create_new(cls, borrower_id: str, borrower_name: str,
                   analysis_result: AnalysisResult, created_by: str, created_by_name: str):

        return cls(
            id=str(uuid.uuid4()),
            borrower_id=borrower_id,
            borrower_name=borrower_name,
            max_loan_amount=analysis_result.max_loan_amount,
            credit_attractiveness=analysis_result.credit_attractiveness,
            risk_level=analysis_result.risk_level,
            status=CreditStatus.IN_PROGRESS,
            created_by=created_by,
            created_by_name=created_by_name,
            recommendations=analysis_result.recommendations,
            score=analysis_result.score
        )

    def to_dict(self):

        return {
            "id": self.id,
            "borrower_id": self.borrower_id,
            "borrower_name": self.borrower_name,
            "max_loan_amount": self.max_loan_amount,
            "credit_attractiveness": self.credit_attractiveness,
            "risk_level": self.risk_level,
            "status": self.status.value,
            "created_by": self.created_by,
            "created_by_name": self.created_by_name,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat() if self.modified_at else None,
            "modified_by": self.modified_by,
            "modified_by_name": self.modified_by_name,
            "recommendations": self.recommendations,
            "blacklist_check": self.blacklist_check,
            "blacklist_found": self.blacklist_found,
            "score": self.score,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict):

        modified_at = None
        if data.get("modified_at"):
            modified_at = datetime.fromisoformat(data["modified_at"])

        return cls(
            id=data["id"],
            borrower_id=data["borrower_id"],
            borrower_name=data["borrower_name"],
            max_loan_amount=data["max_loan_amount"],
            credit_attractiveness=data["credit_attractiveness"],
            risk_level=data["risk_level"],
            status=CreditStatus(data["status"]),
            created_by=data["created_by"],
            created_by_name=data["created_by_name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            modified_at=modified_at,
            modified_by=data.get("modified_by"),
            modified_by_name=data.get("modified_by_name"),
            recommendations=data.get("recommendations", []),
            blacklist_check=data.get("blacklist_check", False),
            blacklist_found=data.get("blacklist_found", False),
            score=data.get("score", 0),
            notes=data.get("notes")
        )