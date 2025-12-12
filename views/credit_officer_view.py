import streamlit as st
from datetime import datetime
from controllers.credit_controller import CreditController
from controllers.report_controller import ReportController
from controllers.data_controller import DataController
from models.borrower import Borrower
from models.enums import CreditStatus
from .base_view import BaseView


class CreditOfficerView(BaseView):

    def __init__(self, data_controller: DataController,
                 credit_controller: CreditController,
                 report_controller: ReportController):
        self.data_controller = data_controller
        self.credit_controller = credit_controller
        self.report_controller = report_controller

    def render(self):

        st.title("👤 Панель сотрудника кредитного отдела")

        tab1, tab2, tab3, tab4 = st.tabs([
            "📝 Ввод данных заемщика",
            "📋 Мои отчеты",
            "❌ Отказы",
            "🔍 Поиск заемщиков"
        ])

        with tab1:
            self._render_borrower_input()

        with tab2:
            self._render_my_reports()

        with tab3:
            self._render_rejections()

        with tab4:
            self._render_search_borrowers()

    def _render_borrower_input(self):

        st.header("Ввод данных заемщика")

        with st.form("borrower_input_form", clear_on_submit=True):
            st.subheader("Персональные данные")

            col1, col2 = st.columns(2)

            with col1:
                full_name = st.text_input("ФИО*")
                passport_series = st.text_input("Серия паспорта*", max_chars=4)
                birth_date = st.date_input("Дата рождения*",
                                           min_value=datetime(1900, 1, 1),
                                           max_value=datetime.now())

            with col2:
                passport_number = st.text_input("Номер паспорта*", max_chars=6)
                phone = st.text_input("Телефон*")
                email = st.text_input("Email")

            st.subheader("Финансовые данные")

            col3, col4 = st.columns(2)

            with col3:
                income = st.number_input("Ежемесячный доход (руб)*",
                                         min_value=0.0,
                                         step=1000.0,
                                         format="%.2f")
                expenses = st.number_input("Ежемесячные расходы (руб)*",
                                           min_value=0.0,
                                           step=1000.0,
                                           format="%.2f")
                existing_loans = st.number_input("Существующие кредиты (руб)",
                                                 min_value=0.0,
                                                 step=1000.0,
                                                 format="%.2f")

            with col4:
                credit_history_score = st.slider("Оценка кредитной истории (0-100)*",
                                                 0, 100, 70)
                employment_years = st.number_input("Стаж работы (лет)*",
                                                   min_value=0,
                                                   max_value=50,
                                                   step=1)

            st.subheader("Данные о работе")

            employer_name = st.text_input("Название работодателя*")
            position = st.text_input("Должность*")
            address = st.text_area("Адрес проживания*")

            st.caption("* Обязательные поля")

            submitted = st.form_submit_button("Провести анализ кредитоспособности",
                                              type="primary")

            if submitted:

                required_fields = {
                    "ФИО": full_name,
                    "Серия паспорта": passport_series,
                    "Номер паспорта": passport_number,
                    "Телефон": phone,
                    "Ежемесячный доход": income,
                    "Ежемесячные расходы": expenses,
                    "ФИО работодателя": employer_name,
                    "Должность": position,
                    "Адрес": address
                }

                missing_fields = [field for field, value in required_fields.items() if not value]

                if missing_fields:
                    st.error(f"Заполните обязательные поля: {', '.join(missing_fields)}")
                    return

                try:
                    borrower = Borrower.create_new(
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
                        created_by=st.session_state.user.id
                    )

                    with st.spinner("Проводим анализ кредитоспособности..."):
                        analysis_result, is_blacklisted, blacklist_reason = \
                            self.credit_controller.analyze_borrower(borrower)

                        if is_blacklisted:
                            st.error(f"❌ {blacklist_reason}")
                            borrower.blacklisted = True
                            borrower.blacklist_reason = blacklist_reason

                            report = self.credit_controller.create_credit_report(
                                borrower, analysis_result,
                                st.session_state.user.id,
                                st.session_state.user.full_name
                            )
                            report.status = CreditStatus.REJECTED
                            report.blacklist_check = True
                            report.blacklist_found = True

                            self.data_controller.add_borrower(borrower)
                            self.data_controller.add_report(report)

                            self._display_analysis_result(analysis_result, is_blacklisted)
                            return

                        report = self.credit_controller.create_credit_report(
                            borrower, analysis_result,
                            st.session_state.user.id,
                            st.session_state.user.full_name
                        )

                        borrower_id = self.data_controller.add_borrower(borrower)
                        report_id = self.data_controller.add_report(report)

                        st.success(f"✅ Анализ завершен! ID заемщика: {borrower_id[:8]}")

                        self._display_analysis_result(analysis_result, is_blacklisted)

                except Exception as e:
                    st.error(f"Ошибка при создании заемщика: {str(e)}")

    def _display_analysis_result(self, result, is_blacklisted: bool):

        st.subheader("Результат анализа кредитоспособности")

        if is_blacklisted:
            st.error("Заемщик находится в черном списке банка")
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Максимальная сумма кредита", f"{result.max_loan_amount:,.2f} ₽")

        with col2:

            if result.credit_attractiveness == "Высокая":
                st.success(f"Привлекательность: {result.credit_attractiveness}")
            elif result.credit_attractiveness == "Средняя":
                st.warning(f"Привлекательность: {result.credit_attractiveness}")
            else:
                st.error(f"Привлекательность: {result.credit_attractiveness}")

        with col3:
            st.metric("Уровень риска", result.risk_level)

        if result.recommendations:
            st.subheader("Рекомендации для улучшения кредитоспособности")
            for i, rec in enumerate(result.recommendations, 1):
                st.write(f"{i}. {rec}")

    def _render_my_reports(self):

        st.header("Мои отчеты")

        user_id = st.session_state.user.id
        my_reports = self.report_controller.get_reports_for_user(
            user_id,
            st.session_state.user_role
        )

        if not my_reports:
            st.info("У вас нет созданных отчетов")
            return

        col1, col2 = st.columns([3, 1])

        with col2:
            status_filter = st.multiselect(
                "Фильтр по статусу",
                [s.value for s in CreditStatus],
                default=[s.value for s in CreditStatus]
            )

        filtered_reports = [
            r for r in my_reports
            if r.status.value in status_filter
        ]

        for report in filtered_reports:
            with st.expander(f"Отчет #{report.id[:8]} - {report.borrower_name} - {report.status.value}"):
                self._display_report_details(report)

                if report.status == CreditStatus.NEEDS_CORRECTION:
                    st.warning("Требует исправлений руководителем")
                elif report.status == CreditStatus.PENDING:
                    st.info("На рассмотрении у руководителя")
                elif report.status == CreditStatus.APPROVED:
                    st.success("✅ Одобрен")
                elif report.status == CreditStatus.REJECTED:
                    st.error("❌ Отклонен")

    def _display_report_details(self, report):

        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Заемщик:** {report.borrower_name}")
            st.write(f"**Макс. сумма:** {report.max_loan_amount:,.2f} ₽")
            st.write(f"**Привлекательность:** {report.credit_attractiveness}")

        with col2:
            st.write(f"**Уровень риска:** {report.risk_level}")
            st.write(f"**Скоринг-балл:** {report.score}/100")
            st.write(f"**Создан:** {report.created_at.strftime('%d.%m.%Y %H:%M')}")

        if report.recommendations:
            st.write("**Рекомендации:**")
            for rec in report.recommendations:
                st.write(f"• {rec}")

        if report.notes:
            st.write(f"**Примечания руководителя:** {report.notes}")

    def _render_rejections(self):

        st.header("Отказы в кредитовании")

        rejected_reports = self.report_controller.get_reports_by_status(CreditStatus.REJECTED)
        my_rejected = [r for r in rejected_reports if r.created_by == st.session_state.user.id]

        if not my_rejected:
            st.info("У вас нет отказов в кредитовании")
            return

        for report in my_rejected:
            with st.expander(f"Отказ #{report.id[:8]} - {report.borrower_name}"):
                self._display_report_details(report)
                if report.blacklist_found:
                    st.error("Причина отказа: Заемщик находится в черном списке банка")

    def _render_search_borrowers(self):

        st.header("Поиск заемщиков")

        search_type = st.radio("Тип поиска:", ["По ФИО", "По паспорту"])

        if search_type == "По ФИО":
            search_query = st.text_input("Введите ФИО заемщика")
        else:
            col1, col2 = st.columns(2)
            with col1:
                passport_series = st.text_input("Серия паспорта", max_chars=4)
            with col2:
                passport_number = st.text_input("Номер паспорта", max_chars=6)
            search_query = f"{passport_series} {passport_number}"

        if st.button("Найти", type="primary"):
            if not search_query:
                st.warning("Введите данные для поиска")
                return

            found_borrowers = []
            for borrower in self.data_controller.borrowers:
                if search_type == "По ФИО":
                    if search_query.lower() in borrower.full_name.lower():
                        found_borrowers.append(borrower)
                else:
                    if (passport_series and passport_number and
                            borrower.passport_series == passport_series and
                            borrower.passport_number == passport_number):
                        found_borrowers.append(borrower)

            if found_borrowers:
                st.success(f"Найдено заемщиков: {len(found_borrowers)}")

                for borrower in found_borrowers:
                    with st.expander(f"{borrower.full_name}"):
                        st.write(f"**Паспорт:** {borrower.passport_series} {borrower.passport_number}")
                        st.write(f"**Телефон:** {borrower.phone}")
                        st.write(f"**Доход:** {borrower.income:,.2f} ₽/мес")
                        st.write(f"**Кредитная история:** {borrower.credit_history_score}/100")

                        # Поиск отчетов по этому заемщику
                        borrower_reports = [r for r in self.data_controller.reports
                                            if r.borrower_id == borrower.id]

                        if borrower_reports:
                            st.write("**История отчетов:**")
                            for report in borrower_reports:
                                status_color = {
                                    "На рассмотрении": "🟡",
                                    "Одобрен": "🟢",
                                    "Отклонен": "🔴",
                                    "Требует исправлений": "🟠",
                                    "В процессе анализа": "⚪"
                                }
                                st.write(f"{status_color.get(report.status.value, '⚪')} "
                                         f"{report.created_at.strftime('%d.%m.%Y')} - "
                                         f"{report.status.value} - "
                                         f"{report.max_loan_amount:,.2f} ₽")
            else:
                st.info("Заемщики не найдены")