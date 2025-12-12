from enum import Enum

class UserRole(Enum):
    CREDIT_OFFICER = "Сотрудник кредитного отдела"
    BANK_MANAGER = "Руководитель подразделения банка"

class CreditStatus(Enum):
    PENDING = "На рассмотрении"
    APPROVED = "Одобрен"
    REJECTED = "Отклонен"
    NEEDS_CORRECTION = "Требует исправлений"
    IN_PROGRESS = "В процессе анализа"