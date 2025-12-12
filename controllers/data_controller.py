import json
import os
from typing import List, Optional, Dict, Any
from models.user import User
from models.borrower import Borrower
from models.report import CreditReport


class DataController:

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.borrowers_file = os.path.join(data_dir, "borrowers.json")
        self.reports_file = os.path.join(data_dir, "reports.json")

        os.makedirs(data_dir, exist_ok=True)

        self.users = self._load_users()
        self.borrowers = self._load_borrowers()
        self.reports = self._load_reports()

        self.blacklist = [
            "Иванов Иван Иванович",
            "Петров Петр Петрович",
            "Сидоров Сидор Сидорович"
        ]

    def _load_users(self) -> List[User]:

        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [User.from_dict(user_data) for user_data in data]
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return []

    def _load_borrowers(self) -> List[Borrower]:

        if os.path.exists(self.borrowers_file):
            try:
                with open(self.borrowers_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [Borrower.from_dict(borrower_data) for borrower_data in data]
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return []

    def _load_reports(self) -> List[CreditReport]:

        if os.path.exists(self.reports_file):
            try:
                with open(self.reports_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [CreditReport.from_dict(report_data) for report_data in data]
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return []

    def _save_users(self):

        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump([user.to_dict() for user in self.users], f, ensure_ascii=False, indent=2)

    def _save_borrowers(self):

        with open(self.borrowers_file, 'w', encoding='utf-8') as f:
            json.dump([borrower.to_dict() for borrower in self.borrowers], f, ensure_ascii=False, indent=2)

    def _save_reports(self):

        with open(self.reports_file, 'w', encoding='utf-8') as f:
            json.dump([report.to_dict() for report in self.reports], f, ensure_ascii=False, indent=2)


    def get_user_by_username(self, username: str) -> Optional[User]:

        for user in self.users:
            if user.username == username and user.is_active:
                return user
        return None

    def get_user_by_id(self, user_id: str) -> Optional[User]:

        for user in self.users:
            if user.id == user_id and user.is_active:
                return user
        return None

    def add_user(self, user: User) -> bool:

        if self.get_user_by_username(user.username):
            return False

        self.users.append(user)
        self._save_users()
        return True

    def update_user(self, user: User) -> bool:

        for i, existing_user in enumerate(self.users):
            if existing_user.id == user.id:
                self.users[i] = user
                self._save_users()
                return True
        return False

    def add_borrower(self, borrower: Borrower) -> str:

        self.borrowers.append(borrower)
        self._save_borrowers()
        return borrower.id

    def get_borrower_by_id(self, borrower_id: str) -> Optional[Borrower]:

        for borrower in self.borrowers:
            if borrower.id == borrower_id:
                return borrower
        return None

    def get_borrowers_by_creator(self, user_id: str) -> List[Borrower]:

        return [b for b in self.borrowers if b.created_by == user_id]

    def add_report(self, report: CreditReport) -> str:

        self.reports.append(report)
        self._save_reports()
        return report.id

    def get_report_by_id(self, report_id: str) -> Optional[CreditReport]:

        for report in self.reports:
            if report.id == report_id:
                return report
        return None

    def get_reports_by_creator(self, user_id: str) -> List[CreditReport]:

        return [r for r in self.reports if r.created_by == user_id]

    def get_all_reports(self) -> List[CreditReport]:

        return self.reports

    def update_report(self, report: CreditReport) -> bool:

        for i, existing_report in enumerate(self.reports):
            if existing_report.id == report.id:
                self.reports[i] = report
                self._save_reports()
                return True
        return False

    def check_blacklist(self, full_name: str) -> bool:

        return full_name in self.blacklist

    def get_statistics(self) -> Dict[str, Any]:

        from models.enums import CreditStatus

        total_reports = len(self.reports)
        status_counts = {
            status.value: len([r for r in self.reports if r.status == status])
            for status in CreditStatus
        }

        return {
            "total_users": len(self.users),
            "total_borrowers": len(self.borrowers),
            "total_reports": total_reports,
            "status_counts": status_counts,
            "avg_credit_score": sum(r.score for r in self.reports) / total_reports if total_reports > 0 else 0,
            "avg_loan_amount": sum(r.max_loan_amount for r in self.reports) / total_reports if total_reports > 0 else 0
        }