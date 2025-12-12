from typing import Tuple
from models.borrower import Borrower
from models.report import AnalysisResult, CreditReport
from models.enums import CreditStatus
from .data_controller import DataController


class CreditController:

    def __init__(self, data_controller: DataController):
        self.data_controller = data_controller

    def analyze_borrower(self, borrower: Borrower) -> Tuple[AnalysisResult, bool, str]:

        in_blacklist = self.data_controller.check_blacklist(borrower.full_name)
        blacklist_reason = ""

        if in_blacklist:
            borrower.blacklisted = True
            borrower.blacklist_reason = "Нахождение в черном списке банка"
            blacklist_reason = "Заемщик находится в черном списке банка"

            return AnalysisResult(
                max_loan_amount=0,
                credit_attractiveness="Нулевая",
                risk_level="Критический",
                recommendations=["Заемщик находится в черном списке банка"],
                score=0
            ), True, blacklist_reason

        disposable_income = borrower.income - borrower.expenses

        if borrower.income > 0:
            debt_ratio = (borrower.existing_loans / borrower.income) * 100
            if debt_ratio > 50:
                debt_score = 20
            elif debt_ratio > 30:
                debt_score = 40
            elif debt_ratio > 15:
                debt_score = 70
            else:
                debt_score = 100
        else:
            debt_score = 0

        history_score = borrower.credit_history_score

        if borrower.employment_years >= 5:
            employment_score = 100
        elif borrower.employment_years >= 3:
            employment_score = 80
        elif borrower.employment_years >= 1:
            employment_score = 60
        else:
            employment_score = 30

        if disposable_income > 50000:
            income_score = 100
        elif disposable_income > 30000:
            income_score = 80
        elif disposable_income > 15000:
            income_score = 60
        elif disposable_income > 0:
            income_score = 40
        else:
            income_score = 0

        savings_ratio = disposable_income / borrower.income if borrower.income > 0 else 0
        if savings_ratio > 0.3:
            savings_score = 100
        elif savings_ratio > 0.2:
            savings_score = 80
        elif savings_ratio > 0.1:
            savings_score = 60
        else:
            savings_score = 30

        total_score = int(
            debt_score * 0.3 +
            history_score * 0.25 +
            employment_score * 0.2 +
            income_score * 0.15 +
            savings_score * 0.1
        )

        base_amount = disposable_income * 12 * 0.3  # 30% годового располагаемого дохода
        score_factor = total_score / 100

        history_factor = borrower.credit_history_score / 100

        employment_factor = min(1, borrower.employment_years / 5)

        final_max_loan = base_amount * score_factor * history_factor * employment_factor

        if total_score >= 80:
            attractiveness = "Высокая"
            risk = "Низкий"
        elif total_score >= 60:
            attractiveness = "Средняя"
            risk = "Средний"
        elif total_score >= 40:
            attractiveness = "Низкая"
            risk = "Высокий"
        else:
            attractiveness = "Очень низкая"
            risk = "Критический"

        recommendations = []

        if total_score < 80:
            if debt_score < 60:
                recommendations.append("Уменьшите текущую задолженность")
            if history_score < 70:
                recommendations.append("Улучшите кредитную историю (своевременно оплачивайте счета)")
            if employment_score < 80:
                recommendations.append("Увеличьте стаж работы на текущем месте")
            if income_score < 70:
                recommendations.append("Увеличьте располагаемый доход")
            if savings_score < 60:
                recommendations.append("Создайте финансовую подушку безопасности")

        if borrower.credit_history_score < 50:
            recommendations.append(
                "Рассмотрите возможность получения небольшого кредита и его своевременного погашения")

        if borrower.employment_years < 1:
            recommendations.append("Стабильная занятость более 1 года повысит шансы на одобрение")

        if len(recommendations) == 0:
            recommendations.append("Ваши финансовые показатели находятся на хорошем уровне")

        result = AnalysisResult(
            max_loan_amount=round(final_max_loan, 2),
            credit_attractiveness=attractiveness,
            risk_level=risk,
            recommendations=recommendations,
            score=total_score
        )

        return result, False, ""

    def create_credit_report(self, borrower: Borrower, analysis_result: AnalysisResult,
                             user_id: str, user_name: str) -> CreditReport:

        if analysis_result.score >= 60:
            status = CreditStatus.PENDING
        else:
            status = CreditStatus.REJECTED

        report = CreditReport.create_new(
            borrower_id=borrower.id,
            borrower_name=borrower.full_name,
            analysis_result=analysis_result,
            created_by=user_id,
            created_by_name=user_name
        )

        report.status = status

        return report