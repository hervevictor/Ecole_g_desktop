from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, Signal
from database.connexion import get_session
from database.models import Utilisateur, ROLE_LABELS


class WaitingPage(QWidget):
    demander_verification = Signal()
    demander_deconnexion  = Signal()

    def __init__(self, utilisateur):
        super().__init__()
        self._user = utilisateur
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #f0f4f8; }
            QFrame#card {
                background-color: white;
                border-radius: 16px;
                border: 1px solid #e2e8f0;
            }
            QPushButton#btn_check {
                background-color: #2b6cb0; color: white;
                border: none; border-radius: 8px;
                padding: 12px 32px; font-size: 14px; font-weight: bold;
            }
            QPushButton#btn_check:hover { background-color: #3182ce; }
            QPushButton#btn_logout {
                background: transparent; color: #718096;
                border: 1.5px solid #cbd5e0; border-radius: 8px;
                padding: 10px 24px; font-size: 13px;
            }
            QPushButton#btn_logout:hover { background: #edf2f7; }
        """)

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(520)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(50, 48, 50, 48)
        cl.setSpacing(16)
        cl.setAlignment(Qt.AlignCenter)

        # Icône
        icon = QLabel("⏳")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 56px;")
        cl.addWidget(icon)

        # Titre
        title = QLabel("Compte en attente d'activation")
        title.setStyleSheet("color:#1a365d; font-size:20px; font-weight:bold;")
        title.setAlignment(Qt.AlignCenter)
        cl.addWidget(title)

        # Nom de l'utilisateur
        nom = f"{self._user.nom} {self._user.prenom}".strip() or self._user.username
        name_lbl = QLabel(nom)
        name_lbl.setStyleSheet("color:#4a5568; font-size:15px;")
        name_lbl.setAlignment(Qt.AlignCenter)
        cl.addWidget(name_lbl)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:#e2e8f0; margin: 4px 0;")
        sep.setFixedHeight(1)
        cl.addWidget(sep)

        # Message d'explication
        msg = QLabel(
            "Votre compte a bien été créé mais aucun rôle ne vous a encore été attribué.\n\n"
            "Un administrateur doit activer votre compte et vous assigner un rôle\n"
            "(Professeur, Secrétaire, Parent…) avant que vous puissiez accéder\n"
            "aux fonctionnalités de G-École.\n\n"
            "Contactez votre administrateur pour accélérer le processus."
        )
        msg.setStyleSheet("color:#4a5568; font-size:13px; line-height:1.6;")
        msg.setAlignment(Qt.AlignCenter)
        msg.setWordWrap(True)
        cl.addWidget(msg)

        # Statut
        self.status_lbl = QLabel()
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setVisible(False)
        cl.addWidget(self.status_lbl)

        cl.addSpacing(8)

        # Boutons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.setAlignment(Qt.AlignCenter)

        btn_logout = QPushButton("Se déconnecter")
        btn_logout.setObjectName("btn_logout")
        btn_logout.setFixedHeight(44)
        btn_logout.clicked.connect(self.demander_deconnexion.emit)
        btn_row.addWidget(btn_logout)

        btn_check = QPushButton("🔄  Vérifier l'activation")
        btn_check.setObjectName("btn_check")
        btn_check.setFixedHeight(44)
        btn_check.clicked.connect(self._verifier)
        btn_row.addWidget(btn_check)

        cl.addLayout(btn_row)

        # Compte rendu
        info = QLabel(f"Connecté en tant que : @{self._user.username}")
        info.setStyleSheet("color:#a0aec0; font-size:11px;")
        info.setAlignment(Qt.AlignCenter)
        cl.addWidget(info)

        root.addWidget(card)

    def _verifier(self):
        session = get_session()
        session.refresh(self._user)
        if self._user.is_active and self._user.role != 'parent':
            # Compte activé avec un vrai rôle → signal pour recharger l'app
            self.demander_verification.emit()
        elif self._user.is_active:
            self._show_status(
                "⚠  Votre compte est actif mais aucun rôle spécifique ne vous a été assigné. "
                "Contactez l'administrateur.", "warn"
            )
        else:
            self._show_status("⏳  Votre compte est toujours en attente. Réessayez plus tard.", "wait")

    def _show_status(self, text, kind):
        colors = {
            "ok":   ("color:#276749; background:#f0fff4; border:1px solid #9ae6b4;"),
            "warn": ("color:#744210; background:#fffbeb; border:1px solid #f6ad55;"),
            "wait": ("color:#2c5282; background:#ebf8ff; border:1px solid #90cdf4;"),
        }
        self.status_lbl.setStyleSheet(
            colors.get(kind, colors["wait"]) +
            "border-radius:6px; padding:8px 12px; font-size:12px;"
        )
        self.status_lbl.setText(text)
        self.status_lbl.setVisible(True)
