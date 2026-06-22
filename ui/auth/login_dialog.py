from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QCheckBox, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.connexion import get_session
from database.models import Utilisateur


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("G-École — Connexion")
        self.setFixedSize(820, 580)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        self.utilisateur = None
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QDialog { background: white; }
            QLineEdit {
                background-color: #f7fafc;
                border: 1.5px solid #cbd5e0;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: #2d3748;
            }
            QLineEdit:focus {
                border: 2px solid #4299e1;
                background-color: white;
            }
            QLabel#field_label {
                color: #4a5568;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton#btn_login {
                background-color: #1a365d;
                color: white; border: none;
                border-radius: 8px; padding: 12px;
                font-size: 14px; font-weight: bold;
            }
            QPushButton#btn_login:hover { background-color: #2a4a7f; }
            QPushButton#btn_login:pressed { background-color: #1a2d4f; }
            QPushButton#btn_login:disabled { background-color: #a0aec0; }
            QLabel#error_label {
                color: #c53030; font-size: 12px;
                background-color: #fff5f5;
                border: 1px solid #feb2b2;
                border-radius: 6px; padding: 8px 12px;
            }
        """)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Panneau gauche : Connexion ─────────────────────────────
        left = QWidget()
        left.setStyleSheet("background: white;")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(50, 30, 50, 24)
        ll.setSpacing(0)

        icon_lbl = QLabel("🎓")
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 38px;")
        ll.addWidget(icon_lbl)
        ll.addSpacing(4)

        title = QLabel("G-École")
        title.setStyleSheet("color: #1a365d; font-size: 22px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        ll.addWidget(title)

        sub = QLabel("Connexion à votre espace")
        sub.setStyleSheet("color: #718096; font-size: 12px;")
        sub.setAlignment(Qt.AlignCenter)
        ll.addWidget(sub)
        ll.addSpacing(20)

        # Username
        lbl_user = QLabel("Nom d'utilisateur")
        lbl_user.setObjectName("field_label")
        ll.addWidget(lbl_user)
        ll.addSpacing(4)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        self.username_input.setFixedHeight(42)
        ll.addWidget(self.username_input)
        ll.addSpacing(12)

        # Password
        lbl_pass = QLabel("Mot de passe")
        lbl_pass.setObjectName("field_label")
        ll.addWidget(lbl_pass)
        ll.addSpacing(4)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Entrez votre mot de passe")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(42)
        self.password_input.returnPressed.connect(self._login)
        ll.addWidget(self.password_input)
        ll.addSpacing(6)

        self.show_pass = QCheckBox("Afficher le mot de passe")
        self.show_pass.setStyleSheet("color: #718096; font-size: 12px;")
        self.show_pass.toggled.connect(
            lambda c: self.password_input.setEchoMode(
                QLineEdit.Normal if c else QLineEdit.Password
            )
        )
        ll.addWidget(self.show_pass)
        ll.addSpacing(10)

        self.error_label = QLabel()
        self.error_label.setObjectName("error_label")
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        ll.addWidget(self.error_label)
        ll.addSpacing(6)

        self.btn_login = QPushButton("Se connecter")
        self.btn_login.setObjectName("btn_login")
        self.btn_login.setFixedHeight(44)
        self.btn_login.clicked.connect(self._login)
        ll.addWidget(self.btn_login)

        ll.addStretch()

        hint = QLabel("Compte admin par défaut : admin / admin123")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet("color: #a0aec0; font-size: 10px;")
        ll.addWidget(hint)

        root.addWidget(left, 1)

        # ── Séparateur vertical ────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setStyleSheet("background: #e2e8f0;")
        sep.setFixedWidth(1)
        root.addWidget(sep)

        # ── Panneau droit : Inscription ────────────────────────────
        right = QWidget()
        right.setStyleSheet("background: #1a365d;")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(52, 0, 52, 0)
        rl.setSpacing(14)
        rl.setAlignment(Qt.AlignCenter)

        icon2 = QLabel("✨")
        icon2.setAlignment(Qt.AlignCenter)
        icon2.setStyleSheet("font-size: 46px;")
        rl.addWidget(icon2)

        title2 = QLabel("Nouveau ici ?")
        title2.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        title2.setAlignment(Qt.AlignCenter)
        rl.addWidget(title2)

        desc = QLabel(
            "Créez votre compte pour accéder\n"
            "à toutes les fonctionnalités de G-École\n"
            "et gérer votre espace personnel."
        )
        desc.setStyleSheet("color: #90cdf4; font-size: 13px;")
        desc.setAlignment(Qt.AlignCenter)
        rl.addWidget(desc)

        rl.addSpacing(10)

        btn_reg = QPushButton("  Créer un compte")
        btn_reg.setFixedHeight(46)
        btn_reg.setCursor(Qt.PointingHandCursor)
        btn_reg.setStyleSheet("""
            QPushButton {
                background: white; color: #1a365d;
                border: none; border-radius: 8px;
                font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: #ebf8ff; }
            QPushButton:pressed { background: #bee3f8; }
        """)
        btn_reg.clicked.connect(self._open_register)
        rl.addWidget(btn_reg)

        already = QLabel("Vous avez déjà un compte ? Connectez-vous à gauche.")
        already.setStyleSheet("color: #4a7fa8; font-size: 11px;")
        already.setAlignment(Qt.AlignCenter)
        already.setWordWrap(True)
        rl.addWidget(already)

        root.addWidget(right, 1)

        self.username_input.setFocus()

    def _login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self._show_error("Veuillez remplir tous les champs.")
            return

        self.btn_login.setText("Connexion en cours...")
        self.btn_login.setEnabled(False)

        session = get_session()
        user = session.query(Utilisateur).filter_by(username=username).first()

        if user and user.check_password(password):
            # Accepter même les comptes inactifs — MainWindow gère l'affichage
            self.utilisateur = user
            self.accept()
        else:
            self._show_error("Nom d'utilisateur ou mot de passe incorrect.")
            self.password_input.clear()
            self.password_input.setFocus()
            self.btn_login.setText("Se connecter")
            self.btn_login.setEnabled(True)

    def _open_register(self):
        from ui.auth.register_dialog import RegisterDialog
        dlg = RegisterDialog(self)
        if dlg.exec() and dlg.utilisateur:
            self.username_input.setText(dlg.utilisateur.username)
            self.password_input.setFocus()

    def _show_error(self, msg):
        self.error_label.setText(f"⚠  {msg}")
        self.error_label.setVisible(True)
