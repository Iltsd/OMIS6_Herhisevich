import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from models.enums import CreditStatus
from controllers.data_controller import DataController
from controllers.report_controller import ReportController
from .base_view import BaseView


class DashboardView(BaseView):

    def __init__(self, data_controller: DataController, report_controller: ReportController):
        self.data_controller = data_controller
        self.report_controller = report_controller

    def render(self):

        st.title("📊 Дашборд системы анализа кредитоспособности")

        stats = self.data_controller.get_statistics()
        report_stats = self.report_controller.get_reports_statistics()

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Всего пользователей", stats["total_users"])

        with col2:
            st.metric("Всего заемщиков", stats["total_borrowers"])

        with col3:
            st.metric("Всего отчетов", stats["total_reports"])

        with col4:
            if stats["total_reports"] > 0:
                st.metric("Средний балл", f"{stats['avg_credit_score']:.1f}")
            else:
                st.metric("Средний балл", "0")

        col_left, col_right = st.columns([2, 1])

        with col_left:
            self._render_reports_chart(report_stats)

        with col_right:
            self._render_attractiveness_pie(report_stats)

        st.subheader("📋 Последние отчеты")
        self._render_recent_reports()

    def _render_reports_chart(self, report_stats: dict):

        st.subheader("Статусы отчетов")

        if "by_status" in report_stats and report_stats["by_status"]:
            status_data = pd.DataFrame({
                "Статус": list(report_stats["by_status"].keys()),
                "Количество": list(report_stats["by_status"].values())
            })

            st.bar_chart(status_data.set_index("Статус"))
        else:
            st.info("Нет данных для отображения")

    def _render_attractiveness_pie(self, report_stats: dict):

        st.subheader("Кредитная привлекательность")

        if report_stats.get("total", 0) > 0:
            attractiveness_data = {
                "Высокая": report_stats.get("high_attractiveness", 0),
                "Средняя": report_stats.get("medium_attractiveness", 0),
                "Низкая": report_stats.get("low_attractiveness", 0)
            }

            df = pd.DataFrame({
                "Привлекательность": list(attractiveness_data.keys()),
                "Количество": list(attractiveness_data.values())
            })

            st.bar_chart(df.set_index("Привлекательность"))
        else:
            st.info("Нет данных")

    def _render_recent_reports(self):

        all_reports = self.data_controller.get_all_reports()

        if not all_reports:
            st.info("Нет доступных отчетов")
            return

        recent_reports = sorted(all_reports, key=lambda x: x.created_at, reverse=True)[:10]

        report_data = []
        for report in recent_reports:
            report_data.append({
                "ID": report.id[:8],
                "Заемщик": report.borrower_name[:20] + "..." if len(
                    report.borrower_name) > 20 else report.borrower_name,
                "Сумма": f"{report.max_loan_amount:,.0f} ₽",
                "Привлекательность": report.credit_attractiveness,
                "Статус": report.status.value,
                "Создан": report.created_at.strftime("%d.%m.%Y"),
                "Автор": report.created_by_name
            })

        if report_data:
            df = pd.DataFrame(report_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Нет данных об отчетах")

    def _render_quick_stats(self):

        st.subheader("📈 Быстрая статистика")

        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_reports = [r for r in self.data_controller.reports
                          if r.created_at > thirty_days_ago]

        if recent_reports:
            approved = len([r for r in recent_reports if r.status == CreditStatus.APPROVED])
            rejected = len([r for r in recent_reports if r.status == CreditStatus.REJECTED])
            pending = len([r for r in recent_reports if r.status == CreditStatus.PENDING])

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Одобрено (30 дн.)", approved)

            with col2:
                st.metric("Отклонено (30 дн.)", rejected)

            with col3:
                st.metric("На рассмотрении", pending)
        else:
            st.info("Нет данных за последние 30 дней")