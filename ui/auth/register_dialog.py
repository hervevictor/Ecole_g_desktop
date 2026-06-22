from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QWidget
)
from PySide6.QtCore import Qt
from database.connexion import get_session
from database.models import Utilisateur


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("G-École — Créer un compte")
        self.setFixedWidth(500)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        self.utilisateur = None
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QDialog { background-color: #f0f4f8; }
            QScrollArea { background: transparent; border: none; }
            QWidget#scroll_content { background: transparent; }
            QFrame#card {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
            QFrame#info_box {
                background-color: #fffbeb;
                border: 1px solid #f6ad55;
                border-radius: 8px;
            }
            QLineEdit {
                background-color: #f7fafc;
                border: 1.5px solid #cbd5e0;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 13px;
                color: #2d3748;
                min-height: 38px;
            }
            QLineEdit:focus { border: 2px solid #4299e1; background-color: white; }
            QLabel#lbl_field {
                color: #4a5568;
                font-size: 12px;
                font-weight: bold;
                margin-bottom: 0px;
            }
            QPushButton#btn_register {
                background-color: #2b6cb0; color: white;
                border: none; border-radius: 8px;
                padding: 11px; font-size: 13px; font-weight: bold;
            }
            QPushButton#btn_register:hover { background-color: #3182ce; }
            QPushButton#btn_register:disabled { background-color: #a0aec0; }
            QPushButton#btn_cancel {
                background-color: transparent; color: #718096;
                border: 1.5px solid #cbd5e0; border-radius: 8px;
                padding: 9px; font-size: 13px;
            }
            QPushButton#btn_cancel:hover { background-color: #edf2f7; }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Zone scrollable ────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("scroll_content")
        cl = QVBoxLayout(content)
        cl.setContentsMargins(28, 22, 28, 22)
        cl.setSpacing(12)

        # Header compact
        icon = QLabel("🎓")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 32px;")
        cl.addWidget(icon)

        title = QLabel("Créer un compte")
        title.setStyleSheet("color:#1a365d; font-size:19px; font-weight:bold;")
        title.setAlignment(Qt.AlignCenter)
        cl.addWidget(title)

        sub = QLabel("Faites une demande d'accès — l'administrateur activera votre compte")
        sub.setStyleSheet("color:#718096; font-size:11px;")
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        cl.addWidget(sub)

        # Info box
        info_box = QFrame()
        info_box.setObjectName("info_box")
        ib = QHBoxLayout(info_box)
        ib.setContentsMargins(12, 8, 12, 8)
        info_lbl = QLabel(
            "🔒  Votre rôle sera défini par l'administrateur. "
            "Votre compte sera inactif jusqu'à son activation."
        )
        info_lbl.setStyleSheet("color:#744210; font-size:11px;")
        info_lbl.setWordWrap(True)
        ib.addWidget(info_lbl)
        cl.addWidget(info_box)

        # ── Card formulaire ────────────────────────────────────────
        card = QFrame()
        card.setObjectName("card")
        fl = QVBoxLayout(card)
        fl.setContentsMargins(20, 18, 20, 18)
        fl.setSpacing(0)

        def add_field(parent_layout, label_text, placeholder, echo=False):
            """Ajoute un label + input avec espacement cohérent."""
            lbl = QLabel(label_text)
            lbl.setObjectName("lbl_field")
            parent_layout.addWidget(lbl)
            inp = QLineEdit()
            inp.setPlaceholderText(placeholder)
            if echo:
                inp.setEchoMode(QLineEdit.Password)
            parent_layout.addWidget(inp)
            parent_layout.addSpacing(10)
            return inp

        # Nom / Prénom côte à côte
        row = QHBoxLayout()
        row.setSpacing(12)

        left_col = QVBoxLayout()
        left_col.setSpacing(4)
        lbl_nom = QLabel("Nom *"); lbl_nom.setObjectName("lbl_field")
        self.nom_input = QLineEdit(); self.nom_input.setPlaceholderText("Votre nom")
        left_col.addWidget(lbl_nom); left_col.addWidget(self.nom_input)

        right_col = QVBoxLayout()
        right_col.setSpacing(4)
        lbl_prenom = QLabel("Prénom"); lbl_prenom.setObjectName("lbl_field")
        self.prenom_input = QLineEdit(); self.prenom_input.setPlaceholderText("Votre prénom")
        right_col.addWidget(lbl_prenom); right_col.addWidget(self.prenom_input)

        row.addLayout(left_col)
        row.addLayout(right_col)
        fl.addLayout(row)
        fl.addSpacing(10)

        # Champs individuels — label + input + espace
        lbl_u = QLabel("Nom d'utilisateur *"); lbl_u.setObjectName("lbl_field")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choisissez un identifiant unique")
        fl.addWidget(lbl_u); fl.addWidget(self.username_input); fl.addSpacing(10)

        lbl_e = QLabel("Email"); lbl_e.setObjectName("lbl_field")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("exemple@email.com")
        fl.addWidget(lbl_e); fl.addWidget(self.email_input); fl.addSpacing(10)

        lbl_t = QLabel("Téléphone"); lbl_t.setObjectName("lbl_field")
        self.tel_input = QLineEdit()
        self.tel_input.setPlaceholderText("+228 XX XX XX XX")
        fl.addWidget(lbl_t); fl.addWidget(self.tel_input); fl.addSpacing(10)

        lbl_p = QLabel("Mot de passe *"); lbl_p.setObjectName("lbl_field")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Minimum 6 caractères")
        self.password_input.setEchoMode(QLineEdit.Password)
        fl.addWidget(lbl_p); fl.addWidget(self.password_input); fl.addSpacing(10)

        lbl_c = QLabel("Confirmer le mot de passe *"); lbl_c.setObjectName("lbl_field")
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Répétez le mot de passe")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.returnPressed.connect(self._register)
        fl.addWidget(lbl_c); fl.addWidget(self.confirm_input); fl.addSpacing(4)

        # Messages feedback
        self.error_label = QLabel()
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        self.error_label.setStyleSheet(
            "color:#c53030; background:#fff5f5; border:1px solid #feb2b2;"
            "border-radius:6px; padding:8px 12px; font-size:12px;"
        )
        fl.addWidget(self.error_label)

        self.success_label = QLabel()
        self.success_label.setWordWrap(True)
        self.success_label.setVisible(False)
        self.success_label.setStyleSheet(
            "color:#744210; background:#fffbeb; border:1px solid #f6ad55;"
            "border-radius:6px; padding:8px 12px; font-size:12px;"
        )
        fl.addWidget(self.success_label)

        # Boutons
        fl.addSpacing(8)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setObjectName("btn_cancel")
        self.btn_cancel.setFixedHeight(40)
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_cancel)

        self.btn_register = QPushButton("Envoyer ma demande")
        self.btn_register.setObjectName("btn_register")
        self.btn_register.setFixedHeight(40)
        self.btn_register.clicked.connect(self._register)
        btn_row.addWidget(self.btn_register)

        fl.addLayout(btn_row)
        cl.addWidget(card)

        scroll.setWidget(content)
        root.addWidget(scroll)

        # Ajuster la hauteur à l'écran (max 700px)
        from PySide6.QtWidgets import QApplication
        screen_h = QApplication.primaryScreen().availableGeometry().height()
        self.setFixedHeight(min(700, screen_h - 80))

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
                role='parent',
                is_active=False,
            )
            user.set_password(password)
            session.add(user)
            session.commit()
            self.utilisateur = user

            self.success_label.setText(
                "✓  Compte créé ! Vous allez être redirigé vers la connexion…"
            )
            self.success_label.setVisible(True)
            self.error_label.setVisible(False)
            self.btn_register.setEnabled(False)
            self.btn_cancel.setEnabled(False)
            # Rediriger vers le login après 1.5s
            from PySide6.QtCore import QTimer
            QTimer.singleShot(1500, self.accept)

        except Exception as e:
            session.rollback()
            self._show_error(f"Erreur lors de la création : {str(e)}")

    def _show_error(self, msg):
        self.success_label.setVisible(False)
        self.error_label.setText(f"⚠  {msg}")
        self.error_label.setVisible(True)
