from typing import List, Optional
from models.report import CreditReport
from models.enums import CreditStatus
from .data_controller import DataController


class ReportController:

    def __init__(self, data_controller: DataController):
        self.data_controller = data_controller

    def get_reports_for_user(self, user_id: str, user_role: str) -> List[CreditReport]:

        if user_role == "Сотрудник кредитного отдела":

            return self.data_controller.get_reports_by_creator(user_id)
        else:

            return self.data_controller.get_all_reports()

    def get_report_by_id(self, report_id: str) -> Optional[CreditReport]:

        return self.data_controller.get_report_by_id(report_id)

    def update_report_status(self, report_id: str, status: CreditStatus,
                             modified_by: str, modified_by_name: str,
                             notes: str = None) -> bool:

        report = self.get_report_by_id(report_id)
        if not report:
            return False

        from datetime import datetime
        report.status = status
        report.modified_at = datetime.now()
        report.modified_by = modified_by
        report.modified_by_name = modified_by_name

        if notes:
            report.notes = notes

        return self.data_controller.update_report(report)

    def modify_report(self, report_id: str, max_loan_amount: float,
                      credit_attractiveness: str, risk_level: str,
                      modified_by: str, modified_by_name: str,
                      notes: str = None) -> bool:

        report = self.get_report_by_id(report_id)
        if not report:
            return False

        from datetime import datetime
        report.max_loan_amount = max_loan_amount
        report.credit_attractiveness = credit_attractiveness
        report.risk_level = risk_level
        report.modified_at = datetime.now()
        report.modified_by = modified_by
        report.modified_by_name = modified_by_name

        if notes:
            report.notes = notes

        if report.status != CreditStatus.NEEDS_CORRECTION:
            report.status = CreditStatus.NEEDS_CORRECTION

        return self.data_controller.update_report(report)

    def get_reports_by_status(self, status: CreditStatus) -> List[CreditReport]:

        all_reports = self.data_controller.get_all_reports()
        return [r for r in all_reports if r.status == status]

    def get_reports_statistics(self) -> dict:

        all_reports = self.data_controller.get_all_reports()

        if not all_reports:
            return {}

        status_stats = {}
        for status in CreditStatus:
            count = len([r for r in all_reports if r.status == status])
            status_stats[status.value] = count

        avg_score = sum(r.score for r in all_reports) / len(all_reports)
        avg_loan = sum(r.max_loan_amount for r in all_reports) / len(all_reports)

        return {
            "total": len(all_reports),
            "by_status": status_stats,
            "avg_score": round(avg_score, 1),
            "avg_loan": round(avg_loan, 2),
            "high_attractiveness": len([r for r in all_reports if r.credit_attractiveness == "Высокая"]),
            "medium_attractiveness": len([r for r in all_reports if r.credit_attractiveness == "Средняя"]),
            "low_attractiveness": len([r for r in all_reports if r.credit_attractiveness == "Низкая"]),
        }