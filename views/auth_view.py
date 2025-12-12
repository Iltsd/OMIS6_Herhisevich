import streamlit as st
from controllers.auth_controller import AuthController
from controllers.data_controller import DataController
from models.user import User
from .base_view import BaseView


class AuthView(BaseView):

    def __init__(self, data_controller: DataController):
        self.auth_controller = AuthController(data_controller)
        self.mode = "login"  # или "register"

    def render(self):

        tab1, tab2 = st.tabs(["🔐 Вход в систему", "📝 Регистрация"])

        with tab1:
            self._render_login()

        with tab2:
            self._render_register()

    def _render_login(self):

        st.header("Вход в систему")

        with st.form("login_form"):
            col1, col2 = st.columns(2)

            with col1:
                username = st.text_input("Логин", key="login_username")

            with col2:
                password = st.text_input("Пароль", type="password", key="login_password")

            role = st.selectbox(
                "Роль пользователя",
                self.auth_controller.get_available_roles(),
                key="login_role"
            )

            submitted = st.form_submit_button("Войти", type="primary")

            if submitted:
                if not username or not password:
                    st.error("Заполните все поля")
                    return

                success, user, message = self.auth_controller.login(username, password, role)

                if success and user:

                    st.session_state.user = user
                    st.session_state.logged_in = True
                    st.session_state.user_role = user.role.value
                    st.success(f"Добро пожаловать, {user.full_name}!")
                    st.rerun()
                else:
                    st.error(f"Ошибка входа: {message}")

    def _render_register(self):

        st.header("Регистрация нового пользователя")

        with st.form("register_form"):
            col1, col2 = st.columns(2)

            with col1:
                username = st.text_input("Логин*", key="register_username")
                full_name = st.text_input("ФИО*", key="register_full_name")
                email = st.text_input("Email*", key="register_email")
                phone = st.text_input("Телефон", key="register_phone")

            with col2:
                password = st.text_input("Пароль*", type="password", key="register_password")
                confirm_password = st.text_input("Подтвердите пароль*",
                                                 type="password",
                                                 key="register_confirm_password")
                role = st.selectbox(
                    "Роль пользователя*",
                    self.auth_controller.get_available_roles(),
                    key="register_role"
                )
                department = st.text_input("Отдел/Подразделение", key="register_department")

            st.caption("* Обязательные поля")

            submitted = st.form_submit_button("Зарегистрироваться", type="primary")

            if submitted:

                required_fields = {
                    "Логин": username,
                    "Пароль": password,
                    "ФИО": full_name,
                    "Email": email
                }

                missing_fields = [field for field, value in required_fields.items() if not value]

                if missing_fields:
                    st.error(f"Заполните обязательные поля: {', '.join(missing_fields)}")
                    return


                success, user, message = self.auth_controller.register(
                    username=username,
                    password=password,
                    confirm_password=confirm_password,
                    role=role,
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    department=department
                )

                if success and user:
                    st.success(f"{message}! Теперь вы можете войти в систему.")
                    st.rerun()
                else:
                    st.error(f"Ошибка регистрации: {message}")

    def show_logout_button(self):

        if st.sidebar.button("🚪 Выйти", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()