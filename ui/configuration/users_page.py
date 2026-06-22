from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QComboBox, QCheckBox, QMessageBox,
    QHeaderView, QAbstractItemView, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.connexion import get_session
from database.models import Utilisateur, Professeur, AnneeScolaire, ROLES, ROLE_LABELS


class UsersTab(QWidget):
    def __init__(self, current_user, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(12)

        # Header
        h = QHBoxLayout()
        title = QLabel("Gestion des utilisateurs")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a365d;")
        h.addWidget(title)
        h.addStretch()
        btn_add = QPushButton("+ Ajouter un utilisateur")
        btn_add.setObjectName("btn_primary"); btn_add.setFixedHeight(34)
        btn_add.clicked.connect(self._ajouter)
        h.addWidget(btn_add)
        layout.addLayout(h)

        # Info card
        info = QFrame(); info.setObjectName("card")
        info_layout = QHBoxLayout(info); info_layout.setContentsMargins(12, 8, 12, 8)
        info_lbl = QLabel(
            "🔒  Seul l'administrateur peut créer des comptes et assigner des rôles. "
            "Les mots de passe sont stockés de façon sécurisée (hachage SHA-256 + sel)."
        )
        info_lbl.setStyleSheet("color: #2b6cb0; font-size: 12px;")
        info_lbl.setWordWrap(True)
        info_layout.addWidget(info_lbl)
        layout.addWidget(info)

        # Bannière comptes en attente (masquée par défaut)
        self.pending_banner = QFrame()
        self.pending_banner.setStyleSheet(
            "background:#fffbeb; border:1px solid #f6ad55; border-radius:8px;"
        )
        pb_layout = QHBoxLayout(self.pending_banner)
        pb_layout.setContentsMargins(14, 10, 14, 10)
        self.pending_lbl = QLabel()
        self.pending_lbl.setStyleSheet("color:#744210; font-size:12px; font-weight:bold;")
        pb_layout.addWidget(self.pending_lbl)
        self.pending_banner.setVisible(False)
        layout.addWidget(self.pending_banner)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Nom complet", "Nom d'utilisateur", "Rôle", "Email", "Actif", "Créé le", "Actions"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 190)
        layout.addWidget(self.table)

    def refresh(self):
        session = get_session()
        users = session.query(Utilisateur).order_by(Utilisateur.is_active, Utilisateur.role, Utilisateur.nom).all()
        self.table.setRowCount(0)

        # Bannière comptes en attente
        pending_count = sum(1 for u in users if not u.is_active)
        if pending_count:
            self.pending_lbl.setText(
                f"⏳  {pending_count} compte(s) en attente d'activation — "
                "Cliquez sur « Activer » pour donner accès à l'utilisateur."
            )
            self.pending_banner.setVisible(True)
        else:
            self.pending_banner.setVisible(False)

        ROLE_COLORS = {
            'admin':      ('#1a365d', '#ebf8ff'),
            'professeur': ('#276749', '#f0fff4'),
            'secretaire': ('#744210', '#fffff0'),
            'parent':     ('#553c9a', '#faf5ff'),
        }

        for user in users:
            row = self.table.rowCount()
            self.table.insertRow(row)
            nom_complet = f"{user.nom} {user.prenom}".strip() or "—"
            date_str = user.date_creation.strftime('%d/%m/%Y') if user.date_creation else '—'

            for col, val in enumerate([
                nom_complet, user.username, '', user.email or '—',
                '', date_str
            ]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row, col, item)

            # Role badge
            fg, bg = ROLE_COLORS.get(user.role, ('#2d3748', '#edf2f7'))
            role_badge = QLabel(f"  {ROLE_LABELS.get(user.role, user.role)}  ")
            role_badge.setStyleSheet(
                f"background:{bg}; color:{fg}; border-radius:8px; "
                f"font-size:11px; font-weight:bold; padding:2px 6px;"
            )
            role_badge.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 2, role_badge)

            # Active badge
            if user.is_active:
                actif_lbl = QLabel("  ✓ Actif  ")
                actif_lbl.setStyleSheet(
                    "background:#c6f6d5; color:#276749; border-radius:8px;"
                    "font-size:11px; font-weight:bold; padding:2px 6px;"
                )
            else:
                actif_lbl = QLabel("  ⏳ En attente  ")
                actif_lbl.setStyleSheet(
                    "background:#fefcbf; color:#744210; border-radius:8px;"
                    "font-size:11px; font-weight:bold; padding:2px 6px;"
                )
            actif_lbl.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 4, actif_lbl)

            # Actions
            actions = QWidget()
            ah = QHBoxLayout(actions); ah.setContentsMargins(3, 2, 3, 2); ah.setSpacing(4)

            # Bouton Activer (visible seulement pour les comptes inactifs)
            if not user.is_active:
                btn_activate = QPushButton("Activer")
                btn_activate.setFixedSize(60, 26)
                btn_activate.setStyleSheet(
                    "background:#38a169; color:white; border:none; border-radius:4px;"
                    "font-size:11px; font-weight:bold;"
                )
                btn_activate.clicked.connect(lambda _, uid=user.id: self._activer(uid))
                ah.addWidget(btn_activate)

            btn_edit = QPushButton("Modifier")
            btn_edit.setObjectName("btn_primary"); btn_edit.setFixedSize(65, 26)
            btn_edit.clicked.connect(lambda _, uid=user.id: self._modifier(uid))
            ah.addWidget(btn_edit)

            btn_pass = QPushButton("MDP")
            btn_pass.setObjectName("btn_secondary"); btn_pass.setFixedSize(45, 26)
            btn_pass.clicked.connect(lambda _, uid=user.id: self._changer_mdp(uid))
            ah.addWidget(btn_pass)

            # Ne pas supprimer son propre compte
            if user.id != self.current_user.id and user.username != 'admin':
                btn_del = QPushButton("Suppr.")
                btn_del.setObjectName("btn_danger"); btn_del.setFixedSize(55, 26)
                btn_del.clicked.connect(lambda _, uid=user.id: self._supprimer(uid))
                ah.addWidget(btn_del)

            self.table.setCellWidget(row, 6, actions)
            self.table.setRowHeight(row, 44)

    def _activer(self, user_id):
        dlg = ActiverCompteDialog(user_id=user_id, parent=self)
        if dlg.exec():
            self.refresh()

    def _ajouter(self):
        dlg = UserFormDialog(current_user=self.current_user, parent=self)
        if dlg.exec():
            self.refresh()

    def _modifier(self, user_id):
        dlg = UserFormDialog(user_id=user_id, current_user=self.current_user, parent=self)
        if dlg.exec():
            self.refresh()

    def _changer_mdp(self, user_id):
        dlg = ChangeMDPDialog(user_id=user_id, parent=self)
        if dlg.exec():
            QMessageBox.information(self, "Succès", "Mot de passe modifié.")

    def _supprimer(self, user_id):
        rep = QMessageBox.question(self, "Confirmation",
                                   "Supprimer cet utilisateur ?",
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            session = get_session()
            u = session.get(Utilisateur, user_id)
            if u:
                session.delete(u); session.commit()
                self.refresh()


class ActiverCompteDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Activer un compte")
        self.setFixedWidth(420)
        self._build_ui()

    def _build_ui(self):
        session = get_session()
        u = session.get(Utilisateur, self.user_id)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # En-tête
        header = QLabel("Activation du compte")
        header.setStyleSheet("font-size:15px; font-weight:bold; color:#1a365d;")
        layout.addWidget(header)

        info = QLabel(
            f"Vous allez activer le compte de <b>{u.nom} {u.prenom}</b> "
            f"(@{u.username}).<br>Choisissez le rôle à lui attribuer."
        )
        info.setStyleSheet(
            "color:#2d3748; font-size:12px; background:#ebf8ff; "
            "border:1px solid #bee3f8; border-radius:6px; padding:10px;"
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        # Rôle
        role_lbl = QLabel("Rôle *")
        role_lbl.setStyleSheet("font-weight:bold; color:#4a5568; font-size:12px;")
        layout.addWidget(role_lbl)

        self.role_cb = QComboBox()
        self.role_cb.setFixedHeight(38)
        for r in ROLES:
            self.role_cb.addItem(ROLE_LABELS[r], r)
        layout.addWidget(self.role_cb)

        # Boutons
        btns = QHBoxLayout(); btns.addStretch()
        btn_c = QPushButton("Annuler"); btn_c.setObjectName("btn_secondary")
        btn_c.clicked.connect(self.reject); btns.addWidget(btn_c)
        btn_ok = QPushButton("✓  Activer le compte"); btn_ok.setObjectName("btn_primary")
        btn_ok.setStyleSheet(
            "background:#38a169; color:white; border:none; border-radius:6px;"
            "padding:8px 16px; font-weight:bold;"
        )
        btn_ok.clicked.connect(self._activer); btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def _activer(self):
        session = get_session()
        u = session.get(Utilisateur, self.user_id)
        if u:
            u.role = self.role_cb.currentData()
            u.is_active = True
            session.commit()
        self.accept()


class UserFormDialog(QDialog):
    def __init__(self, user_id=None, current_user=None, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.current_user = current_user
        self.setWindowTitle("Modifier l'utilisateur" if user_id else "Créer un utilisateur")
        self.setMinimumWidth(450)
        self._build_ui()
        if user_id:
            self._charger()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        form = QFormLayout()
        form.setSpacing(10)

        self.nom = QLineEdit(); self.nom.setFixedHeight(36)
        self.prenom = QLineEdit(); self.prenom.setFixedHeight(36)
        self.username = QLineEdit(); self.username.setFixedHeight(36)
        self.email = QLineEdit(); self.email.setFixedHeight(36)
        self.is_active = QCheckBox("Compte actif"); self.is_active.setChecked(True)

        self.role_cb = QComboBox(); self.role_cb.setFixedHeight(36)
        for r in ROLES:
            self.role_cb.addItem(ROLE_LABELS[r], r)
        self.role_cb.currentIndexChanged.connect(self._on_role_changed)

        self.prof_cb = QComboBox(); self.prof_cb.setFixedHeight(36)
        self.prof_cb.addItem("— Aucun —", None)
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        if annee:
            for p in session.query(Professeur).filter_by(annee_scolaire_id=annee.id).all():
                self.prof_cb.addItem(str(p), p.id)
        self.prof_label = QLabel("Lier au professeur")
        self.prof_label.setVisible(False)
        self.prof_cb.setVisible(False)

        if not self.user_id:
            self.password = QLineEdit(); self.password.setEchoMode(QLineEdit.Password)
            self.password.setFixedHeight(36)
            self.password.setPlaceholderText("Minimum 6 caractères")
            self.password2 = QLineEdit(); self.password2.setEchoMode(QLineEdit.Password)
            self.password2.setFixedHeight(36); self.password2.setPlaceholderText("Répéter le mot de passe")
            form.addRow("Mot de passe *", self.password)
            form.addRow("Confirmer MDP *", self.password2)

        form.addRow("Nom *", self.nom)
        form.addRow("Prénom", self.prenom)
        form.addRow("Nom d'utilisateur *", self.username)
        form.addRow("Email", self.email)
        form.addRow("Rôle *", self.role_cb)
        form.addRow(self.prof_label, self.prof_cb)
        form.addRow("", self.is_active)
        layout.addLayout(form)

        btns = QHBoxLayout(); btns.addStretch()
        btn_c = QPushButton("Annuler"); btn_c.setObjectName("btn_secondary")
        btn_c.clicked.connect(self.reject); btns.addWidget(btn_c)
        btn_s = QPushButton("Enregistrer"); btn_s.setObjectName("btn_primary")
        btn_s.clicked.connect(self._sauvegarder); btns.addWidget(btn_s)
        layout.addLayout(btns)

    def _on_role_changed(self):
        role = self.role_cb.currentData()
        self.prof_label.setVisible(role == 'professeur')
        self.prof_cb.setVisible(role == 'professeur')

    def _charger(self):
        session = get_session()
        u = session.get(Utilisateur, self.user_id)
        if not u: return
        self.nom.setText(u.nom or '')
        self.prenom.setText(u.prenom or '')
        self.username.setText(u.username)
        self.email.setText(u.email or '')
        self.is_active.setChecked(u.is_active)
        idx = self.role_cb.findData(u.role)
        if idx >= 0: self.role_cb.setCurrentIndex(idx)
        if u.professeur_id:
            idx2 = self.prof_cb.findData(u.professeur_id)
            if idx2 >= 0: self.prof_cb.setCurrentIndex(idx2)
        self._on_role_changed()
        # Verrouiller username de l'admin
        if u.username == 'admin':
            self.username.setEnabled(False)
            self.role_cb.setEnabled(False)

    def _sauvegarder(self):
        nom = self.nom.text().strip()
        username = self.username.text().strip()
        role = self.role_cb.currentData()

        if not nom or not username:
            QMessageBox.warning(self, "Erreur", "Nom et nom d'utilisateur obligatoires."); return

        session = get_session()

        if not self.user_id:
            pwd = self.password.text()
            pwd2 = self.password2.text()
            if len(pwd) < 6:
                QMessageBox.warning(self, "Erreur", "Le mot de passe doit faire au moins 6 caractères."); return
            if pwd != pwd2:
                QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas."); return
            # Vérifier unicité username
            existing = session.query(Utilisateur).filter_by(username=username).first()
            if existing:
                QMessageBox.warning(self, "Erreur", f"Le nom d'utilisateur '{username}' est déjà utilisé."); return
            u = Utilisateur(username=username, role=role)
            u.set_password(pwd)
            session.add(u)
        else:
            u = session.get(Utilisateur, self.user_id)
            if u.username != 'admin':
                # Vérifier unicité si changement
                existing = session.query(Utilisateur).filter(
                    Utilisateur.username == username,
                    Utilisateur.id != self.user_id
                ).first()
                if existing:
                    QMessageBox.warning(self, "Erreur", f"Le nom d'utilisateur '{username}' est déjà utilisé."); return
                u.username = username
                u.role = role

        u.nom = nom
        u.prenom = self.prenom.text().strip()
        u.email = self.email.text().strip()
        u.is_active = self.is_active.isChecked()
        u.professeur_id = self.prof_cb.currentData() if role == 'professeur' else None
        session.commit()
        self.accept()


class ChangeMDPDialog(QDialog):
    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("Changer le mot de passe")
        self.setMinimumWidth(360)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(12)

        session = get_session()
        u = session.get(Utilisateur, self.user_id)
        lbl = QLabel(f"Utilisateur : <b>{u.username}</b>" if u else "")
        lbl.setStyleSheet("color: #2d3748; font-size: 13px;")
        layout.addWidget(lbl)

        form = QFormLayout(); form.setSpacing(10)
        self.new_pwd = QLineEdit(); self.new_pwd.setEchoMode(QLineEdit.Password)
        self.new_pwd.setFixedHeight(36); self.new_pwd.setPlaceholderText("Nouveau mot de passe")
        self.new_pwd2 = QLineEdit(); self.new_pwd2.setEchoMode(QLineEdit.Password)
        self.new_pwd2.setFixedHeight(36); self.new_pwd2.setPlaceholderText("Confirmer")
        form.addRow("Nouveau MDP *", self.new_pwd)
        form.addRow("Confirmer *", self.new_pwd2)
        layout.addLayout(form)

        btns = QHBoxLayout(); btns.addStretch()
        btn_c = QPushButton("Annuler"); btn_c.setObjectName("btn_secondary")
        btn_c.clicked.connect(self.reject); btns.addWidget(btn_c)
        btn_s = QPushButton("Changer"); btn_s.setObjectName("btn_primary")
        btn_s.clicked.connect(self._changer); btns.addWidget(btn_s)
        layout.addLayout(btns)

    def _changer(self):
        pwd = self.new_pwd.text()
        pwd2 = self.new_pwd2.text()
        if len(pwd) < 6:
            QMessageBox.warning(self, "Erreur", "Minimum 6 caractères."); return
        if pwd != pwd2:
            QMessageBox.warning(self, "Erreur", "Les mots de passe ne correspondent pas."); return
        session = get_session()
        u = session.get(Utilisateur, self.user_id)
        if u:
            u.set_password(pwd)
            session.commit()
            self.accept()
