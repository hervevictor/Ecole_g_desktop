import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from database.connexion import init_db


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("G-École")
    app.setOrganizationName("GEcole")

    init_db()

    from ui.auth.login_dialog import LoginDialog
    login = LoginDialog()
    if login.exec() != LoginDialog.Accepted or not login.utilisateur:
        sys.exit(0)

    from ui.main_window import MainWindow
    window = MainWindow(login.utilisateur)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
