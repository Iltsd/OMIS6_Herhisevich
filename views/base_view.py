import streamlit as st
from abc import ABC, abstractmethod


class BaseView(ABC):

    def display_data(self, data):
        st.write(data)

    def update_data(self, data):
        st.write("Данные обновлены:", data)

    @abstractmethod
    def render(self):
        pass