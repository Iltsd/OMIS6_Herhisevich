import streamlit as st
from controllers.data_controller import DataController
from controllers.auth_controller import AuthController
from controllers.credit_controller import CreditController
from controllers.report_controller import ReportController
from views.auth_view import AuthView
from views.dashboard_view import DashboardView
from views.credit_officer_view import CreditOfficerView
from views.bank_manager_view import BankManagerView


def initialize_session_state():

    if 'data_controller' not in st.session_state:
        st.session_state.data_controller = DataController()

    if 'auth_controller' not in st.session_state:
        st.session_state.auth_controller = AuthController(st.session_state.data_controller)

    if 'credit_controller' not in st.session_state:
        st.session_state.credit_controller = CreditController(st.session_state.data_controller)

    if 'report_controller' not in st.session_state:
        st.session_state.report_controller = ReportController(st.session_state.data_controller)

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"


class CreditAnalysisSystem:

    def __init__(self):
        initialize_session_state()

    def run(self):

        st.set_page_config(
            page_title="Система анализа кредитоспособности",
            page_icon="🏦",
            layout="wide",
            initial_sidebar_state="expanded"
        )


        self._apply_custom_styles()

        if not st.session_state.logged_in:
            auth_view = AuthView(st.session_state.data_controller)
            auth_view.render()
            return

        self._render_main_interface()

    def _apply_custom_styles(self):

        st.markdown("""
        <style>
        /* Основные стили */
        .main {
            padding: 0rem 1rem;
        }

        /* Стили для метрик */
        div[data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }

        /* Стили для кнопок в сайдбаре */
        .stButton button {
            width: 100%;
        }

        /* Улучшение читаемости таблиц */
        .dataframe {
            font-size: 14px;
        }

        /* Стили для заголовков */
        h1, h2, h3 {
            color: #1E3A8A;
        }

        /* Анимации */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        </style>
        """, unsafe_allow_html=True)

    def _render_main_interface(self):

        user = st.session_state.user

        with st.sidebar:
            st.title("🏦 Банковская система")
            st.divider()

            st.markdown(f"### 👤 {user.full_name}")
            st.caption(f"**Роль:** {user.role.value}")
            st.caption(f"**Отдел:** {user.department if user.department else 'Не указан'}")
            st.divider()

            st.markdown("### 📍 Навигация")

            if user.role.value == "Сотрудник кредитного отдела":
                menu_options = {
                    "📊 Дашборд": "dashboard",
                    "👤 Ввод данных заемщика": "enter_data",
                    "📋 Мои отчеты": "my_reports",
                    "❌ Отказы": "rejections",
                    "🔍 Поиск заемщиков": "search"
                }
            else:
                menu_options = {
                    "📊 Дашборд": "dashboard",
                    "📄 Все отчеты": "all_reports",
                    "✏️ Изменить отчет": "edit_report",
                    "📤 Отправить отчет": "send_report",
                    "📈 Аналитика": "analytics"
                }

            for option_name, option_value in menu_options.items():
                if st.button(option_name,
                             key=f"menu_{option_value}",
                             use_container_width=True,
                             type="primary" if st.session_state.current_page == option_value else "secondary"):
                    st.session_state.current_page = option_value
                    st.rerun()

            st.divider()

            auth_view = AuthView(st.session_state.data_controller)
            auth_view.show_logout_button()

        self._render_content()

    def _render_content(self):

        user = st.session_state.user

        dashboard_view = DashboardView(
            st.session_state.data_controller,
            st.session_state.report_controller
        )

        if user.role.value == "Сотрудник кредитного отдела":
            credit_officer_view = CreditOfficerView(
                st.session_state.data_controller,
                st.session_state.credit_controller,
                st.session_state.report_controller
            )

            if st.session_state.current_page == "dashboard":
                dashboard_view.render()
            elif st.session_state.current_page == "enter_data":
                credit_officer_view._render_borrower_input()
            elif st.session_state.current_page == "my_reports":
                credit_officer_view._render_my_reports()
            elif st.session_state.current_page == "rejections":
                credit_officer_view._render_rejections()
            elif st.session_state.current_page == "search":
                credit_officer_view._render_search_borrowers()

        else:
            bank_manager_view = BankManagerView(
                st.session_state.data_controller,
                st.session_state.report_controller
            )

            if st.session_state.current_page == "dashboard":
                dashboard_view.render()
            elif st.session_state.current_page == "all_reports":
                bank_manager_view._render_all_reports()
            elif st.session_state.current_page == "edit_report":
                bank_manager_view._render_edit_report()
            elif st.session_state.current_page == "send_report":
                bank_manager_view._render_send_report()
            elif st.session_state.current_page == "analytics":
                bank_manager_view._render_analytics()

    def _show_footer(self):

        st.divider()
        st.markdown("""
        <div style='text-align: center; color: gray; padding: 20px;'>
            <p>Интеллектуальная система анализа кредитоспособности заемщиков © 2024</p>
            <p>Версия 1.0 | Разработано в соответствии с UML диаграммами</p>
        </div>
        """, unsafe_allow_html=True)


def main():
    try:
        system = CreditAnalysisSystem()
        system.run()
    except Exception as e:
        st.error(f"Произошла ошибка в приложении: {str(e)}")
        st.write("Пожалуйста, обновите страницу или свяжитесь с администратором.")


if __name__ == "__main__":
    main()