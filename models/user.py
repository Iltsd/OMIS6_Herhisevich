import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from .enums import UserRole


@dataclass
class User:

    id: str
    username: str
    password: str
    role: UserRole
    full_name: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

    @classmethod
    def create_new(cls, username: str, password: str, role: UserRole,
                   full_name: str, email: str, phone: str = "", department: str = ""):

        return cls(
            id=str(uuid.uuid4()),
            username=username,
            password=password,
            role=role,
            full_name=full_name,
            email=email,
            phone=phone,
            department=department
        )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
            "role": self.role.value,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "department": self.department,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }

    @classmethod
    def from_dict(cls, data: dict):

        return cls(
            id=data["id"],
            username=data["username"],
            password=data["password"],
            role=UserRole(data["role"]),
            full_name=data["full_name"],
            email=data["email"],
            phone=data.get("phone"),
            department=data.get("department"),
            created_at=datetime.fromisoformat(data["created_at"]),
            is_active=data.get("is_active", True)
        )