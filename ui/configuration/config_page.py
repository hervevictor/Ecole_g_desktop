from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QGroupBox, QTabWidget, QScrollArea,
    QComboBox, QDateEdit, QMessageBox, QCheckBox, QSpinBox,
    QDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QFrame
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont
from database.connexion import get_session
from database.models import (
    ConfigurationEtablissement, AnneeScolaire, Niveau, Classe,
    NosClasse, TypeMatiere, Matiere, MatiereClasse, Periode, FraisScolarite
)
import datetime


class ConfigPage(QWidget):
    demander_refresh_sidebar = Signal()

    def __init__(self, current_user=None, parent=None):
        super().__init__(parent)
        self.current_user = current_user
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 20)
        layout.setSpacing(15)

        title = QLabel("Configuration")
        font = QFont(); font.setPointSize(18); font.setBold(True)
        title.setFont(font); title.setStyleSheet("color: #1a365d;")
        layout.addWidget(title)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_etablissement_tab(), "Établissement")
        self.tabs.addTab(self._build_annee_tab(), "Années scolaires")
        # Onglet utilisateurs (admin seulement)
        if self.current_user and self.current_user.role == 'admin':
            from ui.configuration.users_page import UsersTab
            self.users_tab = UsersTab(current_user=self.current_user)
            self.tabs.addTab(self.users_tab, "👥 Utilisateurs")
        self.tabs.addTab(self._build_classes_tab(), "Classes & Niveaux")
        self.tabs.addTab(self._build_matieres_tab(), "Matières")
        self.tabs.addTab(self._build_periodes_tab(), "Périodes")
        self.tabs.addTab(self._build_frais_tab(), "Frais de scolarité")
        layout.addWidget(self.tabs, 1)

    # ── Établissement ──────────────────────────────────────────────
    def _build_etablissement_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        form = QFormLayout()
        form.setSpacing(10)
        self.etab_nom = QLineEdit(); self.etab_nom.setFixedHeight(36)
        self.etab_adresse = QLineEdit(); self.etab_adresse.setFixedHeight(36)
        self.etab_tel = QLineEdit(); self.etab_tel.setFixedHeight(36)
        self.etab_email = QLineEdit(); self.etab_email.setFixedHeight(36)
        self.etab_directeur = QLineEdit(); self.etab_directeur.setFixedHeight(36)
        self.etab_devise = QLineEdit(); self.etab_devise.setFixedHeight(36)
        self.etab_num_paiement1 = QLineEdit(); self.etab_num_paiement1.setFixedHeight(36)
        self.etab_num_paiement2 = QLineEdit(); self.etab_num_paiement2.setFixedHeight(36)

        form.addRow("Nom de l'établissement", self.etab_nom)
        form.addRow("Adresse", self.etab_adresse)
        form.addRow("Téléphone", self.etab_tel)
        form.addRow("Email", self.etab_email)
        form.addRow("Directeur", self.etab_directeur)
        form.addRow("Devise / Slogan", self.etab_devise)
        form.addRow("N° paiement 1 (Mobile Money)", self.etab_num_paiement1)
        form.addRow("N° paiement 2", self.etab_num_paiement2)
        layout.addLayout(form)

        btn_save = QPushButton("Enregistrer la configuration")
        btn_save.setObjectName("btn_primary"); btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self._sauver_etablissement)
        layout.addWidget(btn_save)
        layout.addStretch()
        scroll.setWidget(w)
        return scroll

    def _sauver_etablissement(self):
        session = get_session()
        config = session.query(ConfigurationEtablissement).first()
        if not config:
            config = ConfigurationEtablissement()
            session.add(config)
        config.nom_etablissement = self.etab_nom.text().strip()
        config.adresse = self.etab_adresse.text().strip()
        config.telephone = self.etab_tel.text().strip()
        config.email = self.etab_email.text().strip()
        config.directeur = self.etab_directeur.text().strip()
        config.devise = self.etab_devise.text().strip()
        config.numero_paiement_1 = self.etab_num_paiement1.text().strip()
        config.numero_paiement_2 = self.etab_num_paiement2.text().strip()
        session.commit()
        self.demander_refresh_sidebar.emit()
        QMessageBox.information(self, "Succès", "Configuration enregistrée.")

    # ── Années scolaires ───────────────────────────────────────────
    def _build_annee_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        h = QHBoxLayout()
        self.annee_debut = QSpinBox(); self.annee_debut.setRange(2000, 2100)
        self.annee_debut.setValue(datetime.date.today().year)
        self.annee_debut.setFixedHeight(36)
        self.annee_fin = QSpinBox(); self.annee_fin.setRange(2000, 2100)
        self.annee_fin.setValue(datetime.date.today().year + 1)
        self.annee_fin.setFixedHeight(36)
        h.addWidget(QLabel("Début :"))
        h.addWidget(self.annee_debut)
        h.addWidget(QLabel("Fin :"))
        h.addWidget(self.annee_fin)
        btn_add = QPushButton("Créer l'année")
        btn_add.setObjectName("btn_primary"); btn_add.setFixedHeight(36)
        btn_add.clicked.connect(self._creer_annee)
        h.addWidget(btn_add)
        h.addStretch()
        layout.addLayout(h)

        self.table_annees = QTableWidget()
        self.table_annees.setColumnCount(3)
        self.table_annees.setHorizontalHeaderLabels(["Année", "Active", "Actions"])
        self.table_annees.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_annees.verticalHeader().setVisible(False)
        self.table_annees.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_annees.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table_annees.setColumnWidth(2, 160)
        layout.addWidget(self.table_annees)
        return w

    def _creer_annee(self):
        debut = self.annee_debut.value()
        fin = self.annee_fin.value()
        if fin <= debut:
            QMessageBox.warning(self, "Erreur", "L'année de fin doit être supérieure au début."); return
        session = get_session()
        existing = session.query(AnneeScolaire).filter_by(debut=debut, fin=fin).first()
        if existing:
            QMessageBox.warning(self, "Erreur", "Cette année scolaire existe déjà."); return
        session.add(AnneeScolaire(debut=debut, fin=fin, actif=False))
        session.commit()
        self._charger_annees()

    def _charger_annees(self):
        session = get_session()
        annees = session.query(AnneeScolaire).order_by(AnneeScolaire.debut.desc()).all()
        self.table_annees.setRowCount(0)
        for a in annees:
            row = self.table_annees.rowCount()
            self.table_annees.insertRow(row)
            self.table_annees.setItem(row, 0, QTableWidgetItem(str(a)))
            badge = QLabel("  Active  " if a.actif else "  Inactive  ")
            badge.setStyleSheet(
                "background:#c6f6d5;color:#276749;" if a.actif else "background:#e2e8f0;color:#718096;"
                + "border-radius:8px;font-size:11px;font-weight:bold;"
            )
            badge.setAlignment(Qt.AlignCenter)
            self.table_annees.setCellWidget(row, 1, badge)

            actions = QWidget()
            ah = QHBoxLayout(actions); ah.setContentsMargins(2, 1, 2, 1); ah.setSpacing(3)
            if not a.actif:
                btn_act = QPushButton("Activer")
                btn_act.setObjectName("btn_success"); btn_act.setFixedSize(65, 24)
                btn_act.clicked.connect(lambda _, aid=a.id: self._activer_annee(aid))
                ah.addWidget(btn_act)
            btn_del = QPushButton("Suppr.")
            btn_del.setObjectName("btn_danger"); btn_del.setFixedSize(55, 24)
            btn_del.clicked.connect(lambda _, aid=a.id: self._supprimer_annee(aid))
            ah.addWidget(btn_del)
            self.table_annees.setCellWidget(row, 2, actions)
            self.table_annees.setRowHeight(row, 40)

    def _activer_annee(self, annee_id):
        session = get_session()
        session.query(AnneeScolaire).update({'actif': False})
        annee = session.get(AnneeScolaire, annee_id)
        if annee:
            annee.actif = True
            session.commit()
            self._charger_annees()
            QMessageBox.information(self, "Succès", f"Année {annee} activée.")

    def _supprimer_annee(self, annee_id):
        rep = QMessageBox.question(self, "Confirmation",
                                   "Supprimer cette année ? Toutes les données associées seront perdues.",
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            session = get_session()
            a = session.get(AnneeScolaire, annee_id)
            if a:
                session.delete(a)
                session.commit()
                self._charger_annees()

    # ── Classes & Niveaux ──────────────────────────────────────────
    def _build_classes_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        h = QHBoxLayout()
        btn_add_niv = QPushButton("+ Niveau")
        btn_add_niv.setObjectName("btn_secondary"); btn_add_niv.setFixedHeight(34)
        btn_add_niv.clicked.connect(self._ajouter_niveau)
        h.addWidget(btn_add_niv)
        btn_add_cls = QPushButton("+ Classe")
        btn_add_cls.setObjectName("btn_secondary"); btn_add_cls.setFixedHeight(34)
        btn_add_cls.clicked.connect(self._ajouter_classe)
        h.addWidget(btn_add_cls)
        btn_add_nos = QPushButton("+ Sous-classe (A, B...)")
        btn_add_nos.setObjectName("btn_primary"); btn_add_nos.setFixedHeight(34)
        btn_add_nos.clicked.connect(self._ajouter_nos_classe)
        h.addWidget(btn_add_nos)
        h.addStretch()
        layout.addLayout(h)

        self.table_classes = QTableWidget()
        self.table_classes.setColumnCount(4)
        self.table_classes.setHorizontalHeaderLabels(["Type", "Nom", "Titulaire", "Actions"])
        self.table_classes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_classes.verticalHeader().setVisible(False)
        self.table_classes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_classes.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table_classes.setColumnWidth(3, 120)
        layout.addWidget(self.table_classes)
        return w

    def _charger_classes(self):
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        annee_id = annee.id if annee else None
        self.table_classes.setRowCount(0)

        for niveau in session.query(Niveau).filter_by(annee_scolaire_id=annee_id).all():
            row = self.table_classes.rowCount()
            self.table_classes.insertRow(row)
            niv_label = QLabel(f"  NIVEAU : {niveau.nom} ({niveau.type_niveau})  ")
            niv_label.setStyleSheet("background:#ebf8ff;color:#2b6cb0;font-weight:bold;padding:4px;")
            self.table_classes.setCellWidget(row, 0, niv_label)
            self.table_classes.setSpan(row, 0, 1, 4)
            self.table_classes.setRowHeight(row, 34)

            for classe in niveau.classes:
                for nos in classe.nos_classes:
                    row2 = self.table_classes.rowCount()
                    self.table_classes.insertRow(row2)
                    for col, val in enumerate([classe.nom, str(nos), nos.titulaire or '—']):
                        self.table_classes.setItem(row2, col, QTableWidgetItem(val))
                    actions = QWidget()
                    ah = QHBoxLayout(actions); ah.setContentsMargins(2, 1, 2, 1)
                    btn_d = QPushButton("Suppr."); btn_d.setObjectName("btn_danger"); btn_d.setFixedSize(55, 24)
                    btn_d.clicked.connect(lambda _, nid=nos.id: self._supprimer_nos_classe(nid))
                    ah.addWidget(btn_d)
                    self.table_classes.setCellWidget(row2, 3, actions)
                    self.table_classes.setRowHeight(row2, 38)

    def _ajouter_niveau(self):
        dlg = SimpleInputDialog("Ajouter un niveau", [
            ("Nom du niveau", "Ex: Sixième"),
            ("Type", "COLLEGE ou LYCEE"),
        ], parent=self)
        if dlg.exec():
            vals = dlg.get_values()
            session = get_session()
            annee = session.query(AnneeScolaire).filter_by(actif=True).first()
            if not annee:
                QMessageBox.warning(self, "Erreur", "Aucune année active."); return
            type_niv = vals[1].upper() if vals[1].upper() in ('COLLEGE', 'LYCEE') else 'COLLEGE'
            session.add(Niveau(nom=vals[0], type_niveau=type_niv, annee_scolaire_id=annee.id))
            session.commit()
            self._charger_classes()

    def _ajouter_classe(self):
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        if not annee:
            QMessageBox.warning(self, "Erreur", "Aucune année active."); return
        niveaux = session.query(Niveau).filter_by(annee_scolaire_id=annee.id).all()
        if not niveaux:
            QMessageBox.warning(self, "Erreur", "Créez d'abord un niveau."); return
        options = {str(n): n.id for n in niveaux}
        dlg = SelectInputDialog("Ajouter une classe",
                                "Nom de la classe", "Ex: 6ème",
                                "Niveau", list(options.keys()), parent=self)
        if dlg.exec():
            nom, choix = dlg.get_values()
            niveau_id = options[choix]
            session.add(Classe(nom=nom, niveau_id=niveau_id, annee_scolaire_id=annee.id))
            session.commit()
            self._charger_classes()

    def _ajouter_nos_classe(self):
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        if not annee:
            QMessageBox.warning(self, "Erreur", "Aucune année active."); return
        classes = session.query(Classe).filter_by(annee_scolaire_id=annee.id).all()
        if not classes:
            QMessageBox.warning(self, "Erreur", "Créez d'abord des classes."); return
        options = {c.nom: c.id for c in classes}
        dlg = SelectInputDialog("Ajouter une sous-classe",
                                "Indice (A, B, C...)", "Ex: A",
                                "Classe", list(options.keys()), parent=self)
        if dlg.exec():
            indice, choix = dlg.get_values()
            classe_id = options[choix]
            session.add(NosClasse(classe_id=classe_id, indice=indice, annee_scolaire_id=annee.id))
            session.commit()
            self._charger_classes()

    def _supprimer_nos_classe(self, nos_id):
        rep = QMessageBox.question(self, "Confirmation", "Supprimer cette sous-classe ?",
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            session = get_session()
            nos = session.get(NosClasse, nos_id)
            if nos:
                session.delete(nos); session.commit()
                self._charger_classes()

    # ── Matières ───────────────────────────────────────────────────
    def _build_matieres_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        h = QHBoxLayout()
        btn_add = QPushButton("+ Ajouter une matière")
        btn_add.setObjectName("btn_primary"); btn_add.setFixedHeight(34)
        btn_add.clicked.connect(self._ajouter_matiere)
        h.addWidget(btn_add)
        h.addStretch()
        layout.addLayout(h)

        self.table_matieres = QTableWidget()
        self.table_matieres.setColumnCount(3)
        self.table_matieres.setHorizontalHeaderLabels(["Matière", "Type", "Actions"])
        self.table_matieres.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_matieres.verticalHeader().setVisible(False)
        self.table_matieres.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_matieres.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table_matieres.setColumnWidth(2, 100)
        layout.addWidget(self.table_matieres)
        return w

    def _charger_matieres(self):
        session = get_session()
        matieres = session.query(Matiere).order_by(Matiere.nom).all()
        self.table_matieres.setRowCount(0)
        for m in matieres:
            row = self.table_matieres.rowCount()
            self.table_matieres.insertRow(row)
            type_str = str(m.type_matiere) if m.type_matiere else '—'
            for col, val in enumerate([m.nom, type_str]):
                self.table_matieres.setItem(row, col, QTableWidgetItem(val))
            actions = QWidget()
            ah = QHBoxLayout(actions); ah.setContentsMargins(2, 1, 2, 1)
            btn_d = QPushButton("Suppr."); btn_d.setObjectName("btn_danger"); btn_d.setFixedSize(55, 24)
            btn_d.clicked.connect(lambda _, mid=m.id: self._supprimer_matiere(mid))
            ah.addWidget(btn_d)
            self.table_matieres.setCellWidget(row, 2, actions)
            self.table_matieres.setRowHeight(row, 38)

    def _ajouter_matiere(self):
        session = get_session()
        types = session.query(TypeMatiere).all()
        type_options = {str(t): t.id for t in types}
        if not types:
            session.add(TypeMatiere(nom="Général"))
            session.commit()
            types = session.query(TypeMatiere).all()
            type_options = {str(t): t.id for t in types}
        dlg = SelectInputDialog("Ajouter une matière",
                                "Nom de la matière", "Ex: Mathématiques",
                                "Type", list(type_options.keys()), parent=self)
        if dlg.exec():
            nom, choix = dlg.get_values()
            session.add(Matiere(nom=nom.strip(), type_matiere_id=type_options[choix]))
            session.commit()
            self._charger_matieres()

    def _supprimer_matiere(self, mat_id):
        rep = QMessageBox.question(self, "Confirmation", "Supprimer cette matière ?",
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            session = get_session()
            m = session.get(Matiere, mat_id)
            if m:
                session.delete(m); session.commit()
                self._charger_matieres()

    # ── Périodes ───────────────────────────────────────────────────
    def _build_periodes_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        h = QHBoxLayout()
        btn_add = QPushButton("+ Ajouter une période")
        btn_add.setObjectName("btn_primary"); btn_add.setFixedHeight(34)
        btn_add.clicked.connect(self._ajouter_periode)
        h.addWidget(btn_add)
        h.addStretch()
        layout.addLayout(h)

        self.table_periodes = QTableWidget()
        self.table_periodes.setColumnCount(5)
        self.table_periodes.setHorizontalHeaderLabels(["Nom", "Niveau", "Début", "Fin", "Actions"])
        self.table_periodes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_periodes.verticalHeader().setVisible(False)
        self.table_periodes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_periodes.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table_periodes.setColumnWidth(4, 100)
        layout.addWidget(self.table_periodes)
        return w

    def _charger_periodes(self):
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        periodes = session.query(Periode).filter_by(annee_scolaire_id=annee.id if annee else None).all()
        self.table_periodes.setRowCount(0)
        for p in periodes:
            row = self.table_periodes.rowCount()
            self.table_periodes.insertRow(row)
            for col, val in enumerate([
                p.nom, str(p.niveau) if p.niveau else '—',
                str(p.date_debut), str(p.date_fin)
            ]):
                self.table_periodes.setItem(row, col, QTableWidgetItem(val))
            actions = QWidget()
            ah = QHBoxLayout(actions); ah.setContentsMargins(2, 1, 2, 1)
            btn_d = QPushButton("Suppr."); btn_d.setObjectName("btn_danger"); btn_d.setFixedSize(55, 24)
            btn_d.clicked.connect(lambda _, pid=p.id: self._supprimer_periode(pid))
            ah.addWidget(btn_d)
            self.table_periodes.setCellWidget(row, 4, actions)
            self.table_periodes.setRowHeight(row, 38)

    def _ajouter_periode(self):
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        if not annee:
            QMessageBox.warning(self, "Erreur", "Aucune année active."); return
        dlg = PeriodeDialog(annee.id, parent=self)
        if dlg.exec():
            self._charger_periodes()

    def _supprimer_periode(self, pid):
        rep = QMessageBox.question(self, "Confirmation", "Supprimer cette période ?",
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            session = get_session()
            p = session.get(Periode, pid)
            if p:
                session.delete(p); session.commit()
                self._charger_periodes()

    # ── Frais scolarité ────────────────────────────────────────────
    def _build_frais_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(10)

        h = QHBoxLayout()
        btn_add = QPushButton("+ Configurer les frais")
        btn_add.setObjectName("btn_primary"); btn_add.setFixedHeight(34)
        btn_add.clicked.connect(self._ajouter_frais)
        h.addWidget(btn_add)
        h.addStretch()
        layout.addLayout(h)

        self.table_frais = QTableWidget()
        self.table_frais.setColumnCount(4)
        self.table_frais.setHorizontalHeaderLabels(["Classe", "Inscription (FCFA)", "Écolage (FCFA)", "Actions"])
        self.table_frais.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_frais.verticalHeader().setVisible(False)
        self.table_frais.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_frais.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table_frais.setColumnWidth(3, 100)
        layout.addWidget(self.table_frais)
        return w

    def _charger_frais(self):
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        frais_list = session.query(FraisScolarite).filter_by(annee_scolaire_id=annee.id if annee else None).all()
        self.table_frais.setRowCount(0)
        for f in frais_list:
            row = self.table_frais.rowCount()
            self.table_frais.insertRow(row)
            for col, val in enumerate([
                str(f.classe) if f.classe else '—',
                f"{f.frais_d_inscription:,}", f"{f.montant_d_ecolage:,}"
            ]):
                self.table_frais.setItem(row, col, QTableWidgetItem(val))
            actions = QWidget()
            ah = QHBoxLayout(actions); ah.setContentsMargins(2, 1, 2, 1)
            btn_d = QPushButton("Suppr."); btn_d.setObjectName("btn_danger"); btn_d.setFixedSize(55, 24)
            btn_d.clicked.connect(lambda _, fid=f.id: self._supprimer_frais(fid))
            ah.addWidget(btn_d)
            self.table_frais.setCellWidget(row, 3, actions)
            self.table_frais.setRowHeight(row, 38)

    def _ajouter_frais(self):
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        if not annee:
            QMessageBox.warning(self, "Erreur", "Aucune année active."); return
        dlg = FraisDialog(annee.id, parent=self)
        if dlg.exec():
            self._charger_frais()

    def _supprimer_frais(self, fid):
        rep = QMessageBox.question(self, "Confirmation", "Supprimer ces frais ?",
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            session = get_session()
            f = session.get(FraisScolarite, fid)
            if f:
                session.delete(f); session.commit()
                self._charger_frais()

    def refresh(self):
        session = get_session()
        config = session.query(ConfigurationEtablissement).first()
        if config:
            self.etab_nom.setText(config.nom_etablissement or '')
            self.etab_adresse.setText(config.adresse or '')
            self.etab_tel.setText(config.telephone or '')
            self.etab_email.setText(config.email or '')
            self.etab_directeur.setText(config.directeur or '')
            self.etab_devise.setText(config.devise or '')
            self.etab_num_paiement1.setText(config.numero_paiement_1 or '')
            self.etab_num_paiement2.setText(config.numero_paiement_2 or '')
        self._charger_annees()
        self._charger_classes()
        self._charger_matieres()
        self._charger_periodes()
        self._charger_frais()


# ── Dialogs utilitaires ───────────────────────────────────────────

class SimpleInputDialog(QDialog):
    def __init__(self, title, fields, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        self._inputs = []
        form = QFormLayout()
        for label, placeholder in fields:
            inp = QLineEdit(); inp.setPlaceholderText(placeholder); inp.setFixedHeight(36)
            form.addRow(label, inp)
            self._inputs.append(inp)
        layout.addLayout(form)
        btns = QHBoxLayout(); btns.addStretch()
        btn_c = QPushButton("Annuler"); btn_c.setObjectName("btn_secondary")
        btn_c.clicked.connect(self.reject); btns.addWidget(btn_c)
        btn_s = QPushButton("OK"); btn_s.setObjectName("btn_primary")
        btn_s.clicked.connect(self.accept); btns.addWidget(btn_s)
        layout.addLayout(btns)

    def get_values(self):
        return [i.text().strip() for i in self._inputs]


class SelectInputDialog(QDialog):
    def __init__(self, title, label1, placeholder1, label2, options, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(380)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        form = QFormLayout()
        self.inp1 = QLineEdit(); self.inp1.setPlaceholderText(placeholder1); self.inp1.setFixedHeight(36)
        self.cb = QComboBox(); self.cb.setFixedHeight(36); self.cb.addItems(options)
        form.addRow(label1, self.inp1)
        form.addRow(label2, self.cb)
        layout.addLayout(form)
        btns = QHBoxLayout(); btns.addStretch()
        btn_c = QPushButton("Annuler"); btn_c.setObjectName("btn_secondary")
        btn_c.clicked.connect(self.reject); btns.addWidget(btn_c)
        btn_s = QPushButton("OK"); btn_s.setObjectName("btn_primary")
        btn_s.clicked.connect(self.accept); btns.addWidget(btn_s)
        layout.addLayout(btns)

    def get_values(self):
        return self.inp1.text().strip(), self.cb.currentText()


class PeriodeDialog(QDialog):
    def __init__(self, annee_id, parent=None):
        super().__init__(parent)
        self.annee_id = annee_id
        self.setWindowTitle("Ajouter une période")
        self.setMinimumWidth(380)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        form = QFormLayout()
        self.nom = QLineEdit(); self.nom.setPlaceholderText("Ex: 1er Trimestre"); self.nom.setFixedHeight(36)
        self.debut = QDateEdit(QDate.currentDate()); self.debut.setCalendarPopup(True); self.debut.setFixedHeight(36)
        self.fin = QDateEdit(QDate.currentDate().addMonths(3)); self.fin.setCalendarPopup(True); self.fin.setFixedHeight(36)
        session = get_session()
        self.niveau_cb = QComboBox(); self.niveau_cb.setFixedHeight(36)
        for n in session.query(Niveau).filter_by(annee_scolaire_id=self.annee_id).all():
            self.niveau_cb.addItem(str(n), n.id)
        form.addRow("Nom *", self.nom)
        form.addRow("Niveau *", self.niveau_cb)
        form.addRow("Date début *", self.debut)
        form.addRow("Date fin *", self.fin)
        layout.addLayout(form)
        btns = QHBoxLayout(); btns.addStretch()
        btn_c = QPushButton("Annuler"); btn_c.setObjectName("btn_secondary"); btn_c.clicked.connect(self.reject)
        btns.addWidget(btn_c)
        btn_s = QPushButton("Enregistrer"); btn_s.setObjectName("btn_primary"); btn_s.clicked.connect(self._save)
        btns.addWidget(btn_s)
        layout.addLayout(btns)

    def _save(self):
        if not self.nom.text().strip() or not self.niveau_cb.currentData():
            QMessageBox.warning(self, "Erreur", "Nom et niveau obligatoires."); return
        d1 = self.debut.date(); d2 = self.fin.date()
        session = get_session()
        session.add(Periode(
            nom=self.nom.text().strip(),
            niveau_id=self.niveau_cb.currentData(),
            date_debut=datetime.date(d1.year(), d1.month(), d1.day()),
            date_fin=datetime.date(d2.year(), d2.month(), d2.day()),
            annee_scolaire_id=self.annee_id
        ))
        session.commit()
        self.accept()


class FraisDialog(QDialog):
    def __init__(self, annee_id, parent=None):
        super().__init__(parent)
        self.annee_id = annee_id
        self.setWindowTitle("Configurer les frais de scolarité")
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        form = QFormLayout()
        session = get_session()
        self.classe_cb = QComboBox(); self.classe_cb.setFixedHeight(36)
        for c in session.query(Classe).filter_by(annee_scolaire_id=self.annee_id).all():
            self.classe_cb.addItem(c.nom, c.id)
        self.inscription = QSpinBox(); self.inscription.setRange(0, 10_000_000)
        self.inscription.setSingleStep(1000); self.inscription.setSuffix(" FCFA"); self.inscription.setFixedHeight(36)
        self.ecolage = QSpinBox(); self.ecolage.setRange(0, 10_000_000)
        self.ecolage.setSingleStep(1000); self.ecolage.setSuffix(" FCFA"); self.ecolage.setFixedHeight(36)
        form.addRow("Classe *", self.classe_cb)
        form.addRow("Frais d'inscription", self.inscription)
        form.addRow("Montant d'écolage", self.ecolage)
        layout.addLayout(form)
        btns = QHBoxLayout(); btns.addStretch()
        btn_c = QPushButton("Annuler"); btn_c.setObjectName("btn_secondary"); btn_c.clicked.connect(self.reject)
        btns.addWidget(btn_c)
        btn_s = QPushButton("Enregistrer"); btn_s.setObjectName("btn_primary"); btn_s.clicked.connect(self._save)
        btns.addWidget(btn_s)
        layout.addLayout(btns)

    def _save(self):
        session = get_session()
        classe_id = self.classe_cb.currentData()
        existing = session.query(FraisScolarite).filter_by(classe_id=classe_id).first()
        if existing:
            existing.frais_d_inscription = self.inscription.value()
            existing.montant_d_ecolage = self.ecolage.value()
        else:
            session.add(FraisScolarite(
                classe_id=classe_id,
                frais_d_inscription=self.inscription.value(),
                montant_d_ecolage=self.ecolage.value(),
                annee_scolaire_id=self.annee_id
            ))
        session.commit()
        self.accept()
