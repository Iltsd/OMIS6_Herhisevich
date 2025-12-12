from typing import Optional, Tuple
from models.user import User, UserRole
from models.enums import UserRole as RoleEnum
from .data_controller import DataController


class AuthController:

    def __init__(self, data_controller: DataController):
        self.data_controller = data_controller

    def login(self, username: str, password: str, role: str) -> Tuple[bool, Optional[User], str]:

        user = self.data_controller.get_user_by_username(username)

        if not user:
            return False, None, "Пользователь не найден"

        if user.password != password:
            return False, None, "Неверный пароль"

        if user.role.value != role:
            return False, None, f"У пользователя роль '{user.role.value}', а вы выбрали '{role}'"

        if not user.is_active:
            return False, None, "Учетная запись заблокирована"

        return True, user, "Успешный вход"

    def register(self, username: str, password: str, confirm_password: str,
                 role: str, full_name: str, email: str,
                 phone: str = "", department: str = "") -> Tuple[bool, Optional[User], str]:

        if password != confirm_password:
            return False, None, "Пароли не совпадают"

        if len(password) < 6:
            return False, None, "Пароль должен содержать минимум 6 символов"

        if self.data_controller.get_user_by_username(username):
            return False, None, "Пользователь с таким логином уже существует"

        if not self._validate_email(email):
            return False, None, "Неверный формат email"

        try:
            user_role = UserRole(role)
        except ValueError:
            return False, None, "Неверная роль пользователя"

        new_user = User.create_new(
            username=username,
            password=password,
            role=user_role,
            full_name=full_name,
            email=email,
            phone=phone,
            department=department
        )

        if self.data_controller.add_user(new_user):
            return True, new_user, "Регистрация успешна"
        else:
            return False, None, "Ошибка при сохранении пользователя"

    def _validate_email(self, email: str) -> bool:
        return '@' in email and '.' in email

    def get_available_roles(self) -> list:
        return [role.value for role in RoleEnum]