import os
import shutil
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTabWidget, QFileDialog, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QColor, QFont
from database.connexion import get_session
from database.models import Utilisateur, ROLE_LABELS


class _AvatarLabel(QLabel):
    def __init__(self, size=90):
        super().__init__()
        self._size = size
        self.setFixedSize(size, size)

    def set_initials(self, text):
        px = QPixmap(self._size, self._size)
        px.fill(Qt.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QColor("#2b6cb0"))
        p.setPen(Qt.NoPen)
        p.drawEllipse(0, 0, self._size, self._size)
        p.setPen(QColor("white"))
        f = QFont()
        f.setPointSize(int(self._size * 0.3))
        f.setBold(True)
        p.setFont(f)
        p.drawText(px.rect(), Qt.AlignCenter, (text[:2] if text else "?").upper())
        p.end()
        self.setPixmap(px)

    def set_photo(self, path):
        if not path or not os.path.exists(path):
            return
        src = QPixmap(path).scaled(
            self._size, self._size,
            Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
        )
        px = QPixmap(self._size, self._size)
        px.fill(Qt.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)
        clip = QPainterPath()
        clip.addEllipse(0, 0, self._size, self._size)
        p.setClipPath(clip)
        p.drawPixmap((self._size - src.width()) // 2, (self._size - src.height()) // 2, src)
        p.end()
        self.setPixmap(px)


class ProfilePage(QWidget):
    profil_modifie = Signal()

    def __init__(self, utilisateur):
        super().__init__()
        self._user = utilisateur
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("""
            QFrame#card {
                background-color: white;
                border-radius: 14px;
                border: 1px solid #e2e8f0;
            }
            QWidget#tab_content { background: white; }
            QLineEdit {
                background-color: #f7fafc;
                border: 1.5px solid #cbd5e0;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 14px;
                color: #2d3748;
            }
            QLineEdit:focus { border: 2px solid #4299e1; background-color: white; }
            QLineEdit[readOnly="true"] { background-color: #edf2f7; color: #718096; }
            QLabel#field_label { color: #4a5568; font-size: 12px; font-weight: bold; }
            QPushButton#btn_save {
                background-color: #1a365d; color: white;
                border: none; border-radius: 8px;
                padding: 10px 24px; font-size: 13px; font-weight: bold;
            }
            QPushButton#btn_save:hover { background-color: #2a4a7f; }
            QPushButton#btn_photo {
                background-color: transparent; color: #4299e1;
                border: 1.5px solid #4299e1; border-radius: 6px;
                padding: 6px 14px; font-size: 12px;
            }
            QPushButton#btn_photo:hover { background-color: #ebf8ff; }
            QTabWidget::pane { border: none; background: white; border-radius: 10px; }
            QTabBar::tab {
                padding: 10px 28px; font-size: 13px;
                color: #718096; background: transparent;
                border-bottom: 2px solid transparent;
            }
            QTabBar::tab:selected {
                color: #1a365d; font-weight: bold;
                border-bottom: 2px solid #1a365d;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(20)

        title = QLabel("Mon Profil")
        title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1a365d;")
        root.addWidget(title)

        content = QHBoxLayout()
        content.setSpacing(20)
        content.setAlignment(Qt.AlignTop)

        # ── Carte avatar ───────────────────────────────────────────
        avatar_card = QFrame()
        avatar_card.setObjectName("card")
        avatar_card.setFixedWidth(220)
        avatar_card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        ac = QVBoxLayout(avatar_card)
        ac.setContentsMargins(20, 28, 20, 28)
        ac.setSpacing(10)
        ac.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self._avatar = _AvatarLabel(size=90)
        ac.addWidget(self._avatar, alignment=Qt.AlignHCenter)

        self._name_label = QLabel()
        self._name_label.setStyleSheet("font-size: 15px; font-weight: bold; color: #2d3748;")
        self._name_label.setAlignment(Qt.AlignCenter)
        self._name_label.setWordWrap(True)
        ac.addWidget(self._name_label)

        self._role_label = QLabel()
        self._role_label.setStyleSheet("font-size: 11px; color: #718096;")
        self._role_label.setAlignment(Qt.AlignCenter)
        ac.addWidget(self._role_label)

        btn_photo = QPushButton("Changer la photo")
        btn_photo.setObjectName("btn_photo")
        btn_photo.setFixedHeight(34)
        btn_photo.clicked.connect(self._change_photo)
        ac.addWidget(btn_photo)

        ac.addSpacing(16)

        self._date_label = QLabel()
        self._date_label.setStyleSheet("font-size: 10px; color: #a0aec0;")
        self._date_label.setAlignment(Qt.AlignCenter)
        ac.addWidget(self._date_label)

        content.addWidget(avatar_card)

        # ── Onglets ────────────────────────────────────────────────
        tabs = QTabWidget()

        # Onglet 1 — Informations
        info_tab = QWidget()
        info_tab.setObjectName("tab_content")
        il = QVBoxLayout(info_tab)
        il.setContentsMargins(24, 20, 24, 20)
        il.setSpacing(12)

        row_name = QHBoxLayout()
        row_name.setSpacing(12)

        nom_col = QVBoxLayout()
        l = QLabel("Nom"); l.setObjectName("field_label")
        self._nom_input = QLineEdit(); self._nom_input.setPlaceholderText("Votre nom"); self._nom_input.setFixedHeight(42)
        nom_col.addWidget(l); nom_col.addWidget(self._nom_input)

        prenom_col = QVBoxLayout()
        l2 = QLabel("Prénom"); l2.setObjectName("field_label")
        self._prenom_input = QLineEdit(); self._prenom_input.setPlaceholderText("Votre prénom"); self._prenom_input.setFixedHeight(42)
        prenom_col.addWidget(l2); prenom_col.addWidget(self._prenom_input)

        row_name.addLayout(nom_col); row_name.addLayout(prenom_col)
        il.addLayout(row_name)

        lbl_u = QLabel("Nom d'utilisateur"); lbl_u.setObjectName("field_label")
        il.addWidget(lbl_u)
        self._username_display = QLineEdit()
        self._username_display.setFixedHeight(42)
        self._username_display.setReadOnly(True)
        il.addWidget(self._username_display)

        lbl_e = QLabel("Email"); lbl_e.setObjectName("field_label")
        il.addWidget(lbl_e)
        self._email_input = QLineEdit()
        self._email_input.setPlaceholderText("votre@email.com")
        self._email_input.setFixedHeight(42)
        il.addWidget(self._email_input)

        lbl_t = QLabel("Téléphone"); lbl_t.setObjectName("field_label")
        il.addWidget(lbl_t)
        self._tel_input = QLineEdit()
        self._tel_input.setPlaceholderText("+225 XX XX XX XX XX")
        self._tel_input.setFixedHeight(42)
        il.addWidget(self._tel_input)

        self._info_msg = QLabel()
        self._info_msg.setVisible(False)
        self._info_msg.setWordWrap(True)
        il.addWidget(self._info_msg)

        btn_save_info = QPushButton("Enregistrer les modifications")
        btn_save_info.setObjectName("btn_save")
        btn_save_info.setFixedHeight(42)
        btn_save_info.clicked.connect(self._save_info)
        il.addWidget(btn_save_info)
        il.addStretch()

        tabs.addTab(info_tab, "Informations")

        # Onglet 2 — Sécurité
        sec_tab = QWidget()
        sec_tab.setObjectName("tab_content")
        sl = QVBoxLayout(sec_tab)
        sl.setContentsMargins(24, 20, 24, 20)
        sl.setSpacing(12)

        lbl_old = QLabel("Mot de passe actuel"); lbl_old.setObjectName("field_label")
        sl.addWidget(lbl_old)
        self._old_pass = QLineEdit()
        self._old_pass.setEchoMode(QLineEdit.Password)
        self._old_pass.setFixedHeight(42)
        self._old_pass.setPlaceholderText("••••••••")
        sl.addWidget(self._old_pass)

        lbl_new = QLabel("Nouveau mot de passe"); lbl_new.setObjectName("field_label")
        sl.addWidget(lbl_new)
        self._new_pass = QLineEdit()
        self._new_pass.setEchoMode(QLineEdit.Password)
        self._new_pass.setFixedHeight(42)
        self._new_pass.setPlaceholderText("Minimum 6 caractères")
        sl.addWidget(self._new_pass)

        lbl_conf = QLabel("Confirmer le nouveau mot de passe"); lbl_conf.setObjectName("field_label")
        sl.addWidget(lbl_conf)
        self._confirm_pass = QLineEdit()
        self._confirm_pass.setEchoMode(QLineEdit.Password)
        self._confirm_pass.setFixedHeight(42)
        self._confirm_pass.setPlaceholderText("Répétez le nouveau mot de passe")
        sl.addWidget(self._confirm_pass)

        self._sec_msg = QLabel()
        self._sec_msg.setVisible(False)
        self._sec_msg.setWordWrap(True)
        sl.addWidget(self._sec_msg)

        btn_save_pass = QPushButton("Changer le mot de passe")
        btn_save_pass.setObjectName("btn_save")
        btn_save_pass.setFixedHeight(42)
        btn_save_pass.clicked.connect(self._change_password)
        sl.addWidget(btn_save_pass)
        sl.addStretch()

        tabs.addTab(sec_tab, "Sécurité")

        content.addWidget(tabs, 1)
        root.addLayout(content)
        root.addStretch()

    def refresh(self):
        session = get_session()
        session.refresh(self._user)
        u = self._user

        nom_display = f"{u.nom} {u.prenom}".strip() or u.username
        initials = "".join(p[0] for p in nom_display.split() if p)[:2]

        if getattr(u, 'photo_path', '') and os.path.exists(u.photo_path):
            self._avatar.set_photo(u.photo_path)
        else:
            self._avatar.set_initials(initials)

        self._name_label.setText(nom_display)
        self._role_label.setText(f"@{u.username}  ·  {ROLE_LABELS.get(u.role, u.role)}")
        if u.date_creation:
            self._date_label.setText(f"Membre depuis\n{u.date_creation.strftime('%d/%m/%Y')}")

        self._nom_input.setText(u.nom or '')
        self._prenom_input.setText(u.prenom or '')
        self._username_display.setText(u.username)
        self._email_input.setText(u.email or '')
        self._tel_input.setText(getattr(u, 'telephone', '') or '')

        self._info_msg.setVisible(False)
        self._sec_msg.setVisible(False)
        self._old_pass.clear()
        self._new_pass.clear()
        self._confirm_pass.clear()

    def _save_info(self):
        session = get_session()
        try:
            self._user.nom = self._nom_input.text().strip()
            self._user.prenom = self._prenom_input.text().strip()
            self._user.email = self._email_input.text().strip()
            if hasattr(self._user, 'telephone'):
                self._user.telephone = self._tel_input.text().strip()
            session.commit()

            nom_display = f"{self._user.nom} {self._user.prenom}".strip() or self._user.username
            self._name_label.setText(nom_display)
            initials = "".join(p[0] for p in nom_display.split() if p)[:2]
            if not (getattr(self._user, 'photo_path', '') and os.path.exists(self._user.photo_path or '')):
                self._avatar.set_initials(initials)

            self._show_msg(self._info_msg, "ok", "✓  Informations mises à jour avec succès.")
            self.profil_modifie.emit()
        except Exception as e:
            session.rollback()
            self._show_msg(self._info_msg, "err", f"⚠  Erreur : {str(e)}")

    def _change_password(self):
        old = self._old_pass.text()
        new = self._new_pass.text()
        confirm = self._confirm_pass.text()

        if not old or not new or not confirm:
            self._show_msg(self._sec_msg, "err", "⚠  Tous les champs sont obligatoires.")
            return
        if not self._user.check_password(old):
            self._show_msg(self._sec_msg, "err", "⚠  Le mot de passe actuel est incorrect.")
            return
        if len(new) < 6:
            self._show_msg(self._sec_msg, "err", "⚠  Le nouveau mot de passe doit contenir au moins 6 caractères.")
            return
        if new != confirm:
            self._show_msg(self._sec_msg, "err", "⚠  Les mots de passe ne correspondent pas.")
            return

        session = get_session()
        try:
            self._user.set_password(new)
            session.commit()
            self._show_msg(self._sec_msg, "ok", "✓  Mot de passe modifié avec succès.")
            self._old_pass.clear()
            self._new_pass.clear()
            self._confirm_pass.clear()
        except Exception as e:
            session.rollback()
            self._show_msg(self._sec_msg, "err", f"⚠  Erreur : {str(e)}")

    def _change_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir une photo de profil", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.webp)"
        )
        if not path:
            return

        from utils.paths import get_app_dir
        avatars_dir = os.path.join(get_app_dir(), 'assets', 'avatars')
        os.makedirs(avatars_dir, exist_ok=True)
        ext = os.path.splitext(path)[1]
        dest = os.path.join(avatars_dir, f"user_{self._user.id}{ext}")
        shutil.copy2(path, dest)

        session = get_session()
        try:
            self._user.photo_path = dest
            session.commit()
            self._avatar.set_photo(dest)
        except Exception as e:
            session.rollback()

    def _show_msg(self, label, kind, text):
        label.setText(text)
        if kind == "ok":
            label.setStyleSheet(
                "color:#276749; background-color:#f0fff4; border:1px solid #9ae6b4;"
                "border-radius:6px; padding:8px 12px; font-size:12px;"
            )
        else:
            label.setStyleSheet(
                "color:#c53030; background-color:#fff5f5; border:1px solid #feb2b2;"
                "border-radius:6px; padding:8px 12px; font-size:12px;"
            )
        label.setVisible(True)
