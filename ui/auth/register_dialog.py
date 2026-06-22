from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame
)
from PySide6.QtCore import Qt
from database.connexion import get_session
from database.models import Utilisateur


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("G-École — Créer un compte")
        self.setFixedSize(460, 600)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        self.utilisateur = None
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #f0f4f8; }
            QFrame#card {
                background-color: white;
                border-radius: 14px;
                border: 1px solid #e2e8f0;
            }
            QFrame#info_box {
                background-color: #fffbeb;
                border: 1px solid #f6e05e;
                border-radius: 8px;
            }
            QLineEdit {
                background-color: #f7fafc;
                border: 1.5px solid #cbd5e0;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: #2d3748;
            }
            QLineEdit:focus { border: 2px solid #4299e1; background-color: white; }
            QLabel#field_label { color: #4a5568; font-size: 12px; font-weight: bold; }
            QPushButton#btn_register {
                background-color: #2b6cb0; color: white;
                border: none; border-radius: 8px;
                padding: 12px; font-size: 14px; font-weight: bold;
            }
            QPushButton#btn_register:hover { background-color: #3182ce; }
            QPushButton#btn_register:disabled { background-color: #a0aec0; }
            QPushButton#btn_cancel {
                background-color: transparent; color: #718096;
                border: 1.5px solid #cbd5e0; border-radius: 8px;
                padding: 10px; font-size: 13px;
            }
            QPushButton#btn_cancel:hover { background-color: #edf2f7; }
            QLabel#msg_err {
                color: #c53030; font-size: 12px;
                background-color: #fff5f5;
                border: 1px solid #feb2b2;
                border-radius: 6px; padding: 8px 12px;
            }
            QLabel#msg_ok {
                color: #744210; font-size: 12px;
                background-color: #fffbeb;
                border: 1px solid #f6e05e;
                border-radius: 6px; padding: 8px 12px;
            }
        """)

        main = QVBoxLayout(self)
        main.setContentsMargins(30, 24, 30, 24)
        main.setSpacing(0)

        # Header
        icon = QLabel("🎓")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 36px;")
        main.addWidget(icon)

        title = QLabel("Créer un compte")
        title.setStyleSheet("color: #1a365d; font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        main.addWidget(title)

        sub = QLabel("Remplissez vos informations pour faire une demande d'accès")
        sub.setStyleSheet("color: #718096; font-size: 12px;")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        main.addWidget(sub)
        main.addSpacing(14)

        # Info box — rôle attribué par l'admin
        info_box = QFrame()
        info_box.setObjectName("info_box")
        ib = QHBoxLayout(info_box)
        ib.setContentsMargins(12, 10, 12, 10)
        info_lbl = QLabel(
            "🔒  Votre rôle sera défini par l'administrateur. "
            "Votre compte sera inactif jusqu'à son activation."
        )
        info_lbl.setStyleSheet("color: #744210; font-size: 12px;")
        info_lbl.setWordWrap(True)
        ib.addWidget(info_lbl)
        main.addWidget(info_box)
        main.addSpacing(12)

        # Card
        card = QFrame()
        card.setObjectName("card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(24, 20, 24, 20)
        cl.setSpacing(10)

        # Nom / Prénom
        row_name = QHBoxLayout()
        row_name.setSpacing(12)

        nom_col = QVBoxLayout()
        lbl_nom = QLabel("Nom *"); lbl_nom.setObjectName("field_label")
        self.nom_input = QLineEdit()
        self.nom_input.setPlaceholderText("Votre nom")
        self.nom_input.setFixedHeight(42)
        nom_col.addWidget(lbl_nom); nom_col.addWidget(self.nom_input)

        prenom_col = QVBoxLayout()
        lbl_prenom = QLabel("Prénom"); lbl_prenom.setObjectName("field_label")
        self.prenom_input = QLineEdit()
        self.prenom_input.setPlaceholderText("Votre prénom")
        self.prenom_input.setFixedHeight(42)
        prenom_col.addWidget(lbl_prenom); prenom_col.addWidget(self.prenom_input)

        row_name.addLayout(nom_col); row_name.addLayout(prenom_col)
        cl.addLayout(row_name)

        # Username
        lbl_user = QLabel("Nom d'utilisateur *"); lbl_user.setObjectName("field_label")
        cl.addWidget(lbl_user)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choisissez un identifiant unique")
        self.username_input.setFixedHeight(42)
        cl.addWidget(self.username_input)

        # Email
        lbl_email = QLabel("Email"); lbl_email.setObjectName("field_label")
        cl.addWidget(lbl_email)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("votre@email.com")
        self.email_input.setFixedHeight(42)
        cl.addWidget(self.email_input)

        # Téléphone
        lbl_tel = QLabel("Téléphone"); lbl_tel.setObjectName("field_label")
        cl.addWidget(lbl_tel)
        self.tel_input = QLineEdit()
        self.tel_input.setPlaceholderText("+225 XX XX XX XX XX")
        self.tel_input.setFixedHeight(42)
        cl.addWidget(self.tel_input)

        # Mot de passe
        lbl_pass = QLabel("Mot de passe *"); lbl_pass.setObjectName("field_label")
        cl.addWidget(lbl_pass)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Minimum 6 caractères")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(42)
        cl.addWidget(self.password_input)

        # Confirmer
        lbl_confirm = QLabel("Confirmer le mot de passe *"); lbl_confirm.setObjectName("field_label")
        cl.addWidget(lbl_confirm)
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Répétez le mot de passe")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setFixedHeight(42)
        self.confirm_input.returnPressed.connect(self._register)
        cl.addWidget(self.confirm_input)

        # Messages
        self.error_label = QLabel()
        self.error_label.setObjectName("msg_err")
        self.error_label.setVisible(False)
        self.error_label.setWordWrap(True)
        cl.addWidget(self.error_label)

        self.success_label = QLabel()
        self.success_label.setObjectName("msg_ok")
        self.success_label.setVisible(False)
        self.success_label.setWordWrap(True)
        cl.addWidget(self.success_label)

        # Boutons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_cancel.setFixedHeight(42)
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_cancel)

        self.btn_register = QPushButton("Envoyer ma demande")
        self.btn_register.setObjectName("btn_register")
        self.btn_register.setFixedHeight(42)
        self.btn_register.clicked.connect(self._register)
        btn_row.addWidget(self.btn_register)

        cl.addLayout(btn_row)
        main.addWidget(card)

    def _register(self):
        nom = self.nom_input.text().strip()
        prenom = self.prenom_input.text().strip()
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        telephone = self.tel_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not nom or not username or not password:
            self._show_error("Nom, nom d'utilisateur et mot de passe sont obligatoires.")
            return
        if len(password) < 6:
            self._show_error("Le mot de passe doit contenir au moins 6 caractères.")
            return
        if password != confirm:
            self._show_error("Les mots de passe ne correspondent pas.")
            return

        session = get_session()
        if session.query(Utilisateur).filter_by(username=username).first():
            self._show_error("Ce nom d'utilisateur est déjà pris. Choisissez-en un autre.")
            return

        try:
            user = Utilisateur(
                username=username,
                nom=nom,
                prenom=prenom,
                email=email,
                telephone=telephone,
                role='parent',      # rôle minimal par défaut
                is_active=False,    # inactif jusqu'à validation admin
            )
            user.set_password(password)
            session.add(user)
            session.commit()
            self.utilisateur = user

            self.success_label.setText(
                "⏳  Demande envoyée ! Un administrateur doit activer votre compte "
                "et vous attribuer un rôle avant que vous puissiez vous connecter."
            )
            self.success_label.setVisible(True)
            self.error_label.setVisible(False)
            self.btn_register.setEnabled(False)
            self.btn_cancel.setText("Fermer")

        except Exception as e:
            session.rollback()
            self._show_error(f"Erreur lors de la création : {str(e)}")

    def _show_error(self, msg):
        self.success_label.setVisible(False)
        self.error_label.setText(f"⚠  {msg}")
        self.error_label.setVisible(True)
