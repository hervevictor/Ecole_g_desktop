from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QSizePolicy,
    QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.connexion import get_session
from database.models import ConfigurationEtablissement, AnneeScolaire, ROLE_NAV_ACCESS, ROLE_LABELS
from ui.styles import MAIN_STYLE


# Pages disponibles dans la sidebar
NAV_ITEMS = [
    ('dashboard',  '🏠', 'Tableau de bord'),
    ('eleves',     '👥', 'Élèves'),
    ('notes',      '📝', 'Notes'),
    ('paiements',  '💰', 'Paiements'),
    ('profs',      '👨‍🏫', 'Professeurs'),
    ('config',     '⚙️',  'Configuration'),
    ('profile',    '👤', 'Mon Profil'),
]


class MainWindow(QMainWindow):
    def __init__(self, utilisateur):
        super().__init__()
        self.utilisateur = utilisateur
        self.setWindowTitle("G-École — Gestion Scolaire")
        self.setMinimumSize(1200, 750)
        self.resize(1300, 820)
        self.setStyleSheet(MAIN_STYLE)
        self._pages = {}
        self._nav_buttons = {}

        if not utilisateur.is_active:
            self._build_waiting_ui()
        else:
            self._build_ui()
            access = ROLE_NAV_ACCESS.get(utilisateur.role, ['dashboard'])
            first = access[0] if access else 'dashboard'
            self._switch_page(first)

    def _build_waiting_ui(self):
        from ui.waiting_page import WaitingPage
        self.setMinimumSize(700, 500)
        self.resize(800, 560)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        page = WaitingPage(self.utilisateur)
        page.demander_verification.connect(self._recharger_apres_activation)
        page.demander_deconnexion.connect(self._deconnecter_simple)
        layout.addWidget(page)

    def _recharger_apres_activation(self):
        self.close()
        new_window = MainWindow(self.utilisateur)
        new_window.show()
        self._new_window = new_window

    def _deconnecter_simple(self):
        self.close()
        from ui.auth.login_dialog import LoginDialog
        login = LoginDialog()
        if login.exec() and login.utilisateur:
            new_window = MainWindow(login.utilisateur)
            new_window.show()
            self._new_window = new_window

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ────────────────────────────────────────────────
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        logo_label = QLabel("🎓 G-École")
        logo_label.setObjectName("logo_label")
        logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        font = QFont(); font.setPointSize(16); font.setBold(True)
        logo_label.setFont(font)
        sidebar_layout.addWidget(logo_label)

        self._school_name = QLabel()
        self._school_name.setObjectName("school_name")
        self._school_name.setWordWrap(True)
        sidebar_layout.addWidget(self._school_name)

        self._annee_label = QLabel()
        self._annee_label.setStyleSheet("color:#63b3ed;font-size:11px;padding:0 20px 4px 20px;")
        sidebar_layout.addWidget(self._annee_label)

        # Utilisateur connecté
        role_lbl = ROLE_LABELS.get(self.utilisateur.role, self.utilisateur.role)
        nom_complet = f"{self.utilisateur.nom} {self.utilisateur.prenom}".strip() or self.utilisateur.username
        self._user_info_label = QLabel(f"👤 {nom_complet}\n    {role_lbl}")
        self._user_info_label.setStyleSheet(
            "color:#90cdf4; font-size:11px; padding:4px 20px 10px 20px; line-height:1.5;"
        )
        sidebar_layout.addWidget(self._user_info_label)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("background:#2a4a7f; margin: 0 15px;")
        sep.setFixedHeight(1)
        sidebar_layout.addWidget(sep)
        sidebar_layout.addSpacing(8)

        # Navigation — filtrer selon le rôle
        access = ROLE_NAV_ACCESS.get(self.utilisateur.role, ['dashboard'])
        for key, icon, label in NAV_ITEMS:
            if key not in access:
                continue
            btn = QPushButton(f"  {icon}  {label}")
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            btn.setFixedHeight(46)
            font2 = QFont(); font2.setPointSize(12)
            btn.setFont(font2)
            btn.clicked.connect(lambda _, k=key: self._switch_page(k))
            sidebar_layout.addWidget(btn)
            self._nav_buttons[key] = btn

        sidebar_layout.addStretch()

        # Bouton déconnexion
        btn_deconnect = QPushButton("  🚪  Déconnexion")
        btn_deconnect.setFixedHeight(40)
        btn_deconnect.setStyleSheet(
            "color:#fc8181; background:transparent; border:none; "
            "text-align:left; padding-left:20px; font-size:12px;"
        )
        btn_deconnect.clicked.connect(self._deconnecter)
        sidebar_layout.addWidget(btn_deconnect)
        sidebar_layout.addSpacing(10)

        root.addWidget(sidebar)

        # ── Content ────────────────────────────────────────────────
        self._stack = QStackedWidget()
        self._stack.setObjectName("content")
        root.addWidget(self._stack, 1)

        self._refresh_school_name()
        self._refresh_annee_label()

    def _get_or_create_page(self, key):
        if key in self._pages:
            return self._pages[key]

        if key == 'dashboard':
            from ui.dashboard import DashboardPage
            page = DashboardPage()
        elif key == 'eleves':
            from ui.eleves.eleves_page import ElevesPage
            page = ElevesPage()
            page.ouvrir_details.connect(self._ouvrir_eleve)
        elif key == 'notes':
            from ui.notes.notes_page import NotesPage
            page = NotesPage()
        elif key == 'paiements':
            from ui.paiements.paiements_page import PaiementsPage
            page = PaiementsPage()
        elif key == 'profs':
            from ui.profs.profs_page import ProfsPage
            page = ProfsPage()
        elif key == 'config':
            from ui.configuration.config_page import ConfigPage
            page = ConfigPage(current_user=self.utilisateur)
            page.demander_refresh_sidebar.connect(self._refresh_school_name)
        elif key == 'profile':
            from ui.profile.profile_page import ProfilePage
            page = ProfilePage(self.utilisateur)
            page.profil_modifie.connect(self._refresh_user_info)
        else:
            return None

        self._pages[key] = page
        self._stack.addWidget(page)
        return page

    def _switch_page(self, key):
        page = self._get_or_create_page(key)
        if not page:
            return
        self._stack.setCurrentWidget(page)
        if hasattr(page, 'refresh'):
            page.refresh()
        if key in self._nav_buttons:
            self._nav_buttons[key].setChecked(True)
        self._refresh_school_name()
        self._refresh_annee_label()

    def _ouvrir_eleve(self, eleve_id):
        from ui.eleves.eleve_details import EleveDetailsPage
        # Retirer l'ancienne page détails si elle existe
        old = self._pages.pop('eleve_details', None)
        if old:
            self._stack.removeWidget(old)
            old.deleteLater()
        details = EleveDetailsPage(eleve_id)
        details.retour.connect(lambda: self._switch_page('eleves'))
        self._pages['eleve_details'] = details
        self._stack.addWidget(details)
        self._stack.setCurrentWidget(details)

    def _deconnecter(self):
        rep = QMessageBox.question(self, "Déconnexion",
                                   "Voulez-vous vous déconnecter ?",
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            self.close()
            # Relancer la fenêtre de login
            from ui.auth.login_dialog import LoginDialog
            login = LoginDialog()
            if login.exec() and login.utilisateur:
                new_window = MainWindow(login.utilisateur)
                new_window.show()
                # Garder une référence pour éviter le garbage collection
                self._new_window = new_window

    def _refresh_user_info(self):
        session = get_session()
        session.refresh(self.utilisateur)
        role_lbl = ROLE_LABELS.get(self.utilisateur.role, self.utilisateur.role)
        nom_complet = f"{self.utilisateur.nom} {self.utilisateur.prenom}".strip() or self.utilisateur.username
        self._user_info_label.setText(f"👤 {nom_complet}\n    {role_lbl}")

    def _refresh_school_name(self):
        session = get_session()
        config = session.query(ConfigurationEtablissement).first()
        name = config.nom_etablissement if config and config.nom_etablissement else "Mon École"
        self._school_name.setText(name)
        self.setWindowTitle(f"G-École — {name}")

    def _refresh_annee_label(self):
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        self._annee_label.setText(f"Année : {annee}" if annee else "Aucune année active")
