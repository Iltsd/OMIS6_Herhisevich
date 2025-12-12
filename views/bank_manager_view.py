import streamlit as st
from datetime import datetime
from models.enums import CreditStatus
from controllers.report_controller import ReportController
from controllers.data_controller import DataController
from .base_view import BaseView


class BankManagerView(BaseView):

    def __init__(self, data_controller: DataController,
                 report_controller: ReportController):
        self.data_controller = data_controller
        self.report_controller = report_controller

    def render(self):

        st.title("👔 Панель руководителя подразделения")

        tab1, tab2, tab3, tab4 = st.tabs([
            "📄 Все отчеты",
            "✏️ Изменить отчет",
            "📤 Отправить отчет",
            "📈 Аналитика"
        ])

        with tab1:
            self._render_all_reports()

        with tab2:
            self._render_edit_report()

        with tab3:
            self._render_send_report()

        with tab4:
            self._render_analytics()

    def _render_all_reports(self):

        st.header("Все отчеты системы")

        all_reports = self.report_controller.get_reports_for_user(
            "",
            st.session_state.user_role
        )

        if not all_reports:
            st.info("Нет доступных отчетов")
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            status_filter = st.multiselect(
                "Статус",
                [s.value for s in CreditStatus],
                default=[s.value for s in CreditStatus]
            )

        with col2:
            attractiveness_filter = st.multiselect(
                "Привлекательность",
                ["Высокая", "Средняя", "Низкая", "Очень низкая", "Нулевая"],
                default=["Высокая", "Средняя", "Низкая", "Очень низкая", "Нулевая"]
            )

        with col3:

            date_filter = st.selectbox(
                "Период",
                ["Все", "Сегодня", "Неделя", "Месяц", "Квартал"]
            )

        filtered_reports = all_reports

        if status_filter:
            filtered_reports = [r for r in filtered_reports
                                if r.status.value in status_filter]

        if attractiveness_filter:
            filtered_reports = [r for r in filtered_reports
                                if r.credit_attractiveness in attractiveness_filter]

        if date_filter != "Все":
            now = datetime.now()
            if date_filter == "Сегодня":
                start_date = datetime(now.year, now.month, now.day)
            elif date_filter == "Неделя":
                start_date = now - datetime.timedelta(days=7)
            elif date_filter == "Месяц":
                start_date = now - datetime.timedelta(days=30)
            elif date_filter == "Квартал":
                start_date = now - datetime.timedelta(days=90)

            filtered_reports = [r for r in filtered_reports
                                if r.created_at >= start_date]

        st.write(f"**Найдено отчетов:** {len(filtered_reports)}")

        if filtered_reports:

            import pandas as pd

            report_data = []
            for report in filtered_reports:
                report_data.append({
                    "ID": report.id[:8],
                    "Заемщик": report.borrower_name,
                    "Сумма": f"{report.max_loan_amount:,.0f} ₽",
                    "Привлекательность": report.credit_attractiveness,
                    "Риск": report.risk_level,
                    "Статус": report.status.value,
                    "Балл": report.score,
                    "Создан": report.created_at.strftime("%d.%m.%Y"),
                    "Автор": report.created_by_name
                })

            df = pd.DataFrame(report_data)

            def color_status(val):
                if val == "Одобрен":
                    return 'background-color: #90EE90'
                elif val == "Отклонен":
                    return 'background-color: #FFB6C1'
                elif val == "Требует исправлений":
                    return 'background-color: #FFFACD'
                elif val == "На рассмотрении":
                    return 'background-color: #ADD8E6'
                return ''

            styled_df = df.style.applymap(color_status, subset=['Статус'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        else:
            st.info("Нет отчетов, соответствующих фильтрам")

    def _render_edit_report(self):

        st.header("Изменение отчета")

        pending_reports = self.report_controller.get_reports_by_status(CreditStatus.PENDING)
        correction_reports = self.report_controller.get_reports_by_status(CreditStatus.NEEDS_CORRECTION)
        available_reports = pending_reports + correction_reports

        if not available_reports:
            st.info("Нет отчетов, требующих редактирования")
            return

        report_options = {f"{r.id[:8]} - {r.borrower_name} - {r.created_by_name}": r
                          for r in available_reports}

        selected_report_key = st.selectbox(
            "Выберите отчет для редактирования",
            options=list(report_options.keys())
        )

        report = report_options[selected_report_key]

        with st.form("edit_report_form"):
            st.subheader(f"Редактирование отчета #{report.id[:8]}")

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Заемщик:** {report.borrower_name}")
                st.write(f"**Автор:** {report.created_by_name}")
                st.write(f"**Создан:** {report.created_at.strftime('%d.%m.%Y %H:%M')}")

            with col2:
                st.write(f"**Текущий статус:** {report.status.value}")
                st.write(f"**Текущий балл:** {report.score}/100")
                if report.modified_at:
                    st.write(f"**Изменен:** {report.modified_at.strftime('%d.%m.%Y %H:%M')}")

            st.divider()

            col3, col4, col5 = st.columns(3)

            with col3:
                new_max_loan = st.number_input(
                    "Максимальная сумма кредита (руб)",
                    value=float(report.max_loan_amount),
                    step=10000.0,
                    format="%.2f"
                )

            with col4:
                new_attractiveness = st.selectbox(
                    "Кредитная привлекательность",
                    ["Высокая", "Средняя", "Низкая", "Очень низкая", "Нулевая"],
                    index=["Высокая", "Средняя", "Низкая", "Очень низкая", "Нулевая"].index(
                        report.credit_attractiveness)
                )

            with col5:
                new_risk_level = st.selectbox(
                    "Уровень риска",
                    ["Низкий", "Средний", "Высокий", "Критический"],
                    index=["Низкий", "Средний", "Высокий", "Критический"].index(report.risk_level)
                )

            new_status = st.selectbox(
                "Новый статус",
                [s.value for s in CreditStatus],
                index=[s.value for s in CreditStatus].index(report.status.value)
            )

            notes = st.text_area(
                "Комментарии и примечания",
                value=report.notes if report.notes else ""
            )

            submitted = st.form_submit_button("Сохранить изменения", type="primary")

            if submitted:

                success = self.report_controller.modify_report(
                    report_id=report.id,
                    max_loan_amount=new_max_loan,
                    credit_attractiveness=new_attractiveness,
                    risk_level=new_risk_level,
                    modified_by=st.session_state.user.id,
                    modified_by_name=st.session_state.user.full_name,
                    notes=notes
                )

                if success:

                    if new_status != report.status.value:
                        self.report_controller.update_report_status(
                            report_id=report.id,
                            status=CreditStatus(new_status),
                            modified_by=st.session_state.user.id,
                            modified_by_name=st.session_state.user.full_name
                        )

                    st.success("✅ Отчет успешно обновлен!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Ошибка при обновлении отчета")

    def _render_send_report(self):

        st.header("Отправка отчета сотруднику")

        ready_statuses = [CreditStatus.APPROVED, CreditStatus.NEEDS_CORRECTION]
        ready_reports = []

        for status in ready_statuses:
            ready_reports.extend(self.report_controller.get_reports_by_status(status))

        if not ready_reports:
            st.info("Нет отчетов, готовых к отправке")
            return

        for report in ready_reports:
            with st.expander(f"Отчет #{report.id[:8]} - {report.borrower_name} - {report.status.value}"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Заемщик:** {report.borrower_name}")
                    st.write(f"**Сумма:** {report.max_loan_amount:,.2f} ₽")
                    st.write(f"**Привлекательность:** {report.credit_attractiveness}")
                    st.write(f"**Автор:** {report.created_by_name}")

                with col2:
                    if st.button(f"Отправить", key=f"send_{report.id}"):

                        from datetime import datetime
                        report.modified_at = datetime.now()
                        report.modified_by = st.session_state.user.id
                        report.modified_by_name = st.session_state.user.full_name

                        if report.status == CreditStatus.NEEDS_CORRECTION:
                            report.status = CreditStatus.PENDING

                        self.data_controller.update_report(report)

                        st.success(f"✅ Отчет #{report.id[:8]} отправлен сотруднику {report.created_by_name}!")

    def _render_analytics(self):

        st.header("Аналитика системы")

        stats = self.data_controller.get_statistics()
        report_stats = self.report_controller.get_reports_statistics()

        st.subheader("Ключевые показатели")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Общая одобряемость",
                      f"{(report_stats.get('by_status', {}).get('Одобрен', 0) / report_stats.get('total', 1) * 100):.1f}%")

        with col2:
            st.metric("Средний балл", f"{report_stats.get('avg_score', 0):.1f}")

        with col3:
            st.metric("Средняя сумма", f"{report_stats.get('avg_loan', 0):,.0f} ₽")

        with col4:
            high_attract = report_stats.get('high_attractiveness', 0)
            total = report_stats.get('total', 1)
            st.metric("Высокая привлекательность",
                      f"{(high_attract / total * 100):.1f}%")

        st.subheader("Распределение по статусам")

        if report_stats.get('by_status'):
            import pandas as pd

            status_data = pd.DataFrame({
                "Статус": list(report_stats['by_status'].keys()),
                "Количество": list(report_stats['by_status'].values())
            })

            st.bar_chart(status_data.set_index("Статус"))

        st.subheader("Активность сотрудников")

        user_stats = {}
        for report in self.data_controller.reports:
            user_id = report.created_by
            if user_id not in user_stats:
                user = self.data_controller.get_user_by_id(user_id)
                user_name = user.full_name if user else "Неизвестный"
                user_stats[user_id] = {
                    "name": user_name,
                    "total": 0,
                    "approved": 0,
                    "rejected": 0,
                    "avg_score": 0,
                    "total_amount": 0
                }

            user_stats[user_id]["total"] += 1
            user_stats[user_id]["total_amount"] += report.max_loan_amount

            if report.status == CreditStatus.APPROVED:
                user_stats[user_id]["approved"] += 1
            elif report.status == CreditStatus.REJECTED:
                user_stats[user_id]["rejected"] += 1

        if user_stats:
            stats_data = []
            for user_id, stats in user_stats.items():
                approval_rate = (stats["approved"] / stats["total"] * 100) if stats["total"] > 0 else 0
                avg_amount = stats["total_amount"] / stats["total"] if stats["total"] > 0 else 0

                stats_data.append({
                    "Сотрудник": stats["name"],
                    "Всего отчетов": stats["total"],
                    "Одобрено": stats["approved"],
                    "Отклонено": stats["rejected"],
                    "Процент одобрения": f"{approval_rate:.1f}%",
                    "Ср. сумма": f"{avg_amount:,.0f} ₽"
                })

            import pandas as pd
            df = pd.DataFrame(stats_data)
            st.dataframe(df.sort_values("Всего отчетов", ascending=False),
                         use_container_width=True,
                         hide_index=True)