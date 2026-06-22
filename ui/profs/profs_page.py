from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QDialog,
    QFormLayout, QComboBox, QHeaderView, QAbstractItemView,
    QMessageBox, QTabWidget, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.connexion import get_session
from database.models import Professeur, AnneeScolaire, Niveau, EmploiDuTemps


class ProfsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 20)
        layout.setSpacing(15)

        title = QLabel("Gestion des Professeurs")
        font = QFont(); font.setPointSize(18); font.setBold(True)
        title.setFont(font); title.setStyleSheet("color: #1a365d;")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_profs_tab(), "Professeurs")
        self.tabs.addTab(self._build_edt_tab(), "Emplois du temps")
        layout.addWidget(self.tabs, 1)

    def _build_profs_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        h = QHBoxLayout()
        self.search_prof = QLineEdit()
        self.search_prof.setObjectName("search_input")
        self.search_prof.setPlaceholderText("Rechercher un professeur...")
        self.search_prof.setFixedHeight(36)
        self.search_prof.textChanged.connect(self._filtrer_profs)
        h.addWidget(self.search_prof, 2)
        h.addStretch()
        btn_add = QPushButton("+ Ajouter un professeur")
        btn_add.setObjectName("btn_primary"); btn_add.setFixedHeight(36)
        btn_add.clicked.connect(self._ajouter_prof)
        h.addWidget(btn_add)
        layout.addLayout(h)

        self.table_profs = QTableWidget()
        self.table_profs.setColumnCount(6)
        self.table_profs.setHorizontalHeaderLabels(["Nom", "Prénom", "Spécialité", "Niveau", "Tél.", "Actions"])
        self.table_profs.setAlternatingRowColors(True)
        self.table_profs.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_profs.verticalHeader().setVisible(False)
        self.table_profs.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_profs.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table_profs.setColumnWidth(5, 140)
        layout.addWidget(self.table_profs)
        self._profs_data = []
        return w

    def _build_edt_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        h = QHBoxLayout()
        self.filtre_prof_edt = QComboBox()
        self.filtre_prof_edt.setFixedHeight(36)
        self.filtre_prof_edt.addItem("Tous les professeurs", None)
        self.filtre_prof_edt.currentIndexChanged.connect(self._filtrer_edt)
        h.addWidget(self.filtre_prof_edt)
        h.addStretch()
        btn_add_edt = QPushButton("+ Ajouter un créneau")
        btn_add_edt.setObjectName("btn_primary"); btn_add_edt.setFixedHeight(36)
        btn_add_edt.clicked.connect(self._ajouter_edt)
        h.addWidget(btn_add_edt)
        layout.addLayout(h)

        self.table_edt = QTableWidget()
        self.table_edt.setColumnCount(6)
        self.table_edt.setHorizontalHeaderLabels(["Professeur", "Jour", "Début", "Fin", "Matière", "Classe"])
        self.table_edt.setAlternatingRowColors(True)
        self.table_edt.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_edt.verticalHeader().setVisible(False)
        self.table_edt.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_edt)
        return w

    def refresh(self):
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        annee_id = annee.id if annee else None

        self._profs_data = session.query(Professeur).filter_by(annee_scolaire_id=annee_id).order_by(Professeur.nom).all()
        self._filtrer_profs()

        self.filtre_prof_edt.blockSignals(True)
        self.filtre_prof_edt.clear()
        self.filtre_prof_edt.addItem("Tous les professeurs", None)
        for p in self._profs_data:
            self.filtre_prof_edt.addItem(str(p), p.id)
        self.filtre_prof_edt.blockSignals(False)
        self._filtrer_edt()

    def _filtrer_profs(self):
        terme = self.search_prof.text().lower()
        profs = self._profs_data
        if terme:
            profs = [p for p in profs if terme in p.nom.lower() or terme in p.prenom.lower()
                     or terme in (p.specialite or '').lower()]
        self.table_profs.setRowCount(0)
        for prof in profs:
            row = self.table_profs.rowCount()
            self.table_profs.insertRow(row)
            niveau_str = str(prof.niveau) if prof.niveau else '—'
            for col, val in enumerate([prof.nom, prof.prenom, prof.specialite or '—',
                                        niveau_str, prof.telephone or '—']):
                self.table_profs.setItem(row, col, QTableWidgetItem(val))
            actions = QWidget()
            ah = QHBoxLayout(actions); ah.setContentsMargins(2, 1, 2, 1); ah.setSpacing(3)
            btn_e = QPushButton("Modifier"); btn_e.setObjectName("btn_primary"); btn_e.setFixedSize(65, 24)
            btn_e.clicked.connect(lambda _, pid=prof.id: self._modifier_prof(pid))
            ah.addWidget(btn_e)
            btn_d = QPushButton("Suppr."); btn_d.setObjectName("btn_danger"); btn_d.setFixedSize(55, 24)
            btn_d.clicked.connect(lambda _, pid=prof.id: self._supprimer_prof(pid))
            ah.addWidget(btn_d)
            self.table_profs.setCellWidget(row, 5, actions)
            self.table_profs.setRowHeight(row, 42)

    def _filtrer_edt(self):
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        annee_id = annee.id if annee else None
        prof_id = self.filtre_prof_edt.currentData()
        q = session.query(EmploiDuTemps).join(Professeur).filter(
            Professeur.annee_scolaire_id == annee_id
        )
        if prof_id:
            q = q.filter(EmploiDuTemps.professeur_id == prof_id)
        edts = q.all()
        self.table_edt.setRowCount(0)
        for edt in edts:
            row = self.table_edt.rowCount()
            self.table_edt.insertRow(row)
            prof_str = str(edt.professeur) if edt.professeur else '—'
            classe_str = str(edt.nos_classe) if edt.nos_classe else '—'
            for col, val in enumerate([prof_str, edt.jour, edt.heure_debut, edt.heure_fin,
                                        edt.matiere or '—', classe_str]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_edt.setItem(row, col, item)

    def _ajouter_prof(self):
        dlg = ProfFormDialog(parent=self)
        if dlg.exec():
            self.refresh()

    def _modifier_prof(self, prof_id):
        dlg = ProfFormDialog(prof_id=prof_id, parent=self)
        if dlg.exec():
            self.refresh()

    def _supprimer_prof(self, prof_id):
        rep = QMessageBox.question(self, "Confirmation", "Supprimer ce professeur ?",
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            session = get_session()
            p = session.get(Professeur, prof_id)
            if p:
                session.delete(p)
                session.commit()
                self.refresh()

    def _ajouter_edt(self):
        dlg = EdtFormDialog(parent=self)
        if dlg.exec():
            self.refresh()


class ProfFormDialog(QDialog):
    def __init__(self, prof_id=None, parent=None):
        super().__init__(parent)
        self.prof_id = prof_id
        self.setWindowTitle("Modifier le professeur" if prof_id else "Ajouter un professeur")
        self.setMinimumWidth(420)
        self._build_ui()
        if prof_id:
            self._charger()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        form = QFormLayout()

        self.nom = QLineEdit(); self.nom.setFixedHeight(36)
        self.prenom = QLineEdit(); self.prenom.setFixedHeight(36)
        self.telephone = QLineEdit(); self.telephone.setFixedHeight(36)
        self.email = QLineEdit(); self.email.setFixedHeight(36)
        self.specialite = QLineEdit(); self.specialite.setFixedHeight(36)
        self.matricule = QLineEdit(); self.matricule.setFixedHeight(36)

        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        self.niveau = QComboBox(); self.niveau.setFixedHeight(36)
        self.niveau.addItem("— Aucun niveau —", None)
        if annee:
            for n in session.query(Niveau).filter_by(annee_scolaire_id=annee.id).all():
                self.niveau.addItem(str(n), n.id)

        form.addRow("Nom *", self.nom)
        form.addRow("Prénom *", self.prenom)
        form.addRow("Téléphone", self.telephone)
        form.addRow("Email", self.email)
        form.addRow("Spécialité", self.specialite)
        form.addRow("Matricule", self.matricule)
        form.addRow("Niveau", self.niveau)
        layout.addLayout(form)

        btns = QHBoxLayout(); btns.addStretch()
        btn_c = QPushButton("Annuler"); btn_c.setObjectName("btn_secondary")
        btn_c.clicked.connect(self.reject)
        btns.addWidget(btn_c)
        btn_s = QPushButton("Enregistrer"); btn_s.setObjectName("btn_primary")
        btn_s.clicked.connect(self._sauvegarder)
        btns.addWidget(btn_s)
        layout.addLayout(btns)

    def _charger(self):
        session = get_session()
        p = session.get(Professeur, self.prof_id)
        if not p: return
        self.nom.setText(p.nom); self.prenom.setText(p.prenom)
        self.telephone.setText(p.telephone or ''); self.email.setText(p.email or '')
        self.specialite.setText(p.specialite or ''); self.matricule.setText(p.matricule or '')
        if p.niveau_id:
            idx = self.niveau.findData(p.niveau_id)
            if idx >= 0: self.niveau.setCurrentIndex(idx)

    def _sauvegarder(self):
        if not self.nom.text().strip() or not self.prenom.text().strip():
            QMessageBox.warning(self, "Erreur", "Nom et prénom obligatoires."); return
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        if self.prof_id:
            p = session.get(Professeur, self.prof_id)
        else:
            p = Professeur(annee_scolaire_id=annee.id if annee else None)
        p.nom = self.nom.text().strip().upper()
        p.prenom = self.prenom.text().strip()
        p.telephone = self.telephone.text().strip()
        p.email = self.email.text().strip()
        p.specialite = self.specialite.text().strip()
        p.matricule = self.matricule.text().strip()
        p.niveau_id = self.niveau.currentData()
        if not self.prof_id: session.add(p)
        session.commit()
        self.accept()


class EdtFormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter un créneau")
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        form = QFormLayout()

        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()

        self.prof_cb = QComboBox(); self.prof_cb.setFixedHeight(36)
        if annee:
            for p in session.query(Professeur).filter_by(annee_scolaire_id=annee.id).all():
                self.prof_cb.addItem(str(p), p.id)

        self.jour_cb = QComboBox(); self.jour_cb.setFixedHeight(36)
        self.jour_cb.addItems(["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"])

        self.h_debut = QComboBox(); self.h_debut.setFixedHeight(36)
        self.h_fin = QComboBox(); self.h_fin.setFixedHeight(36)
        heures = [f"{h:02d}:{m:02d}" for h in range(7, 19) for m in (0, 30)]
        self.h_debut.addItems(heures); self.h_fin.addItems(heures)
        self.h_fin.setCurrentIndex(2)

        self.matiere_input = QLineEdit(); self.matiere_input.setFixedHeight(36)

        form.addRow("Professeur *", self.prof_cb)
        form.addRow("Jour *", self.jour_cb)
        form.addRow("Heure début *", self.h_debut)
        form.addRow("Heure fin *", self.h_fin)
        form.addRow("Matière", self.matiere_input)
        layout.addLayout(form)

        btns = QHBoxLayout(); btns.addStretch()
        btn_c = QPushButton("Annuler"); btn_c.setObjectName("btn_secondary")
        btn_c.clicked.connect(self.reject)
        btns.addWidget(btn_c)
        btn_s = QPushButton("Enregistrer"); btn_s.setObjectName("btn_primary")
        btn_s.clicked.connect(self._sauvegarder)
        btns.addWidget(btn_s)
        layout.addLayout(btns)

    def _sauvegarder(self):
        prof_id = self.prof_cb.currentData()
        if not prof_id:
            QMessageBox.warning(self, "Erreur", "Sélectionnez un professeur."); return
        session = get_session()
        session.add(EmploiDuTemps(
            professeur_id=prof_id,
            jour=self.jour_cb.currentText(),
            heure_debut=self.h_debut.currentText(),
            heure_fin=self.h_fin.currentText(),
            matiere=self.matiere_input.text().strip()
        ))
        session.commit()
        self.accept()
