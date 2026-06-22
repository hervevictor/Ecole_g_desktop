from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QComboBox,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from database.connexion import get_session
from database.models import Eleve, NosClasse, AnneeScolaire, Niveau


class ElevesPage(QWidget):
    ouvrir_details = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 20)
        layout.setSpacing(15)

        # Header
        header = QHBoxLayout()
        title = QLabel("Gestion des Élèves")
        font = QFont(); font.setPointSize(18); font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #1a365d;")
        header.addWidget(title)
        header.addStretch()

        self.btn_ajouter = QPushButton("+ Ajouter un élève")
        self.btn_ajouter.setObjectName("btn_primary")
        self.btn_ajouter.setFixedHeight(36)
        self.btn_ajouter.clicked.connect(self._ajouter)
        header.addWidget(self.btn_ajouter)

        self.btn_export_pdf = QPushButton("Export PDF")
        self.btn_export_pdf.setObjectName("btn_secondary")
        self.btn_export_pdf.setFixedHeight(36)
        self.btn_export_pdf.clicked.connect(self._export_pdf)
        header.addWidget(self.btn_export_pdf)

        self.btn_export_excel = QPushButton("Export Excel")
        self.btn_export_excel.setObjectName("btn_secondary")
        self.btn_export_excel.setFixedHeight(36)
        self.btn_export_excel.clicked.connect(self._export_excel)
        header.addWidget(self.btn_export_excel)
        layout.addLayout(header)

        # Filters
        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setObjectName("search_input")
        self.search.setPlaceholderText("Rechercher par nom, prénom ou matricule...")
        self.search.setFixedHeight(36)
        self.search.textChanged.connect(self._filtrer)
        filters.addWidget(self.search, 2)

        self.filtre_niveau = QComboBox()
        self.filtre_niveau.setFixedHeight(36)
        self.filtre_niveau.addItem("Tous les niveaux", None)
        self.filtre_niveau.currentIndexChanged.connect(self._filtrer)
        filters.addWidget(self.filtre_niveau)

        self.filtre_classe = QComboBox()
        self.filtre_classe.setFixedHeight(36)
        self.filtre_classe.addItem("Toutes les classes", None)
        self.filtre_classe.currentIndexChanged.connect(self._filtrer)
        filters.addWidget(self.filtre_classe)

        self.filtre_statut = QComboBox()
        self.filtre_statut.setFixedHeight(36)
        self.filtre_statut.addItems(["Tous", "Nouveaux", "Anciens"])
        self.filtre_statut.currentIndexChanged.connect(self._filtrer)
        filters.addWidget(self.filtre_statut)
        layout.addLayout(filters)

        # Count label
        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet("color: #718096; font-size: 12px;")
        layout.addWidget(self.lbl_count)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Matricule", "Nom", "Prénom", "Classe", "Sexe", "Parent", "Téléphone", "Actions"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 180)
        self.table.setMinimumHeight(400)
        layout.addWidget(self.table, 1)

        self._eleves_data = []

    def refresh(self):
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        annee_id = annee.id if annee else None

        # Reload niveaux filter
        self.filtre_niveau.blockSignals(True)
        self.filtre_niveau.clear()
        self.filtre_niveau.addItem("Tous les niveaux", None)
        niveaux = session.query(Niveau).filter_by(annee_scolaire_id=annee_id).all()
        for n in niveaux:
            self.filtre_niveau.addItem(n.nom, n.id)
        self.filtre_niveau.blockSignals(False)

        # Reload classes filter
        self.filtre_classe.blockSignals(True)
        self.filtre_classe.clear()
        self.filtre_classe.addItem("Toutes les classes", None)
        classes = session.query(NosClasse).filter_by(annee_scolaire_id=annee_id).all()
        for c in classes:
            self.filtre_classe.addItem(str(c), c.id)
        self.filtre_classe.blockSignals(False)

        self._eleves_data = (
            session.query(Eleve)
            .filter_by(annee_scolaire_id=annee_id)
            .order_by(Eleve.nom)
            .all()
        )
        self._filtrer()

    def _filtrer(self):
        terme = self.search.text().lower()
        niveau_id = self.filtre_niveau.currentData()
        classe_id = self.filtre_classe.currentData()
        statut = self.filtre_statut.currentText()

        eleves = self._eleves_data
        if terme:
            eleves = [e for e in eleves if terme in e.nom.lower()
                      or terme in e.prenom.lower()
                      or terme in (e.matricule or '').lower()]
        if niveau_id:
            eleves = [e for e in eleves
                      if e.nos_classe and e.nos_classe.classe and
                      e.nos_classe.classe.niveau_id == niveau_id]
        if classe_id:
            eleves = [e for e in eleves if e.nos_classe_id == classe_id]
        if statut == "Nouveaux":
            eleves = [e for e in eleves if e.est_nouveau]
        elif statut == "Anciens":
            eleves = [e for e in eleves if not e.est_nouveau]

        self.lbl_count.setText(f"{len(eleves)} élève(s) trouvé(s)")
        self._afficher_eleves(eleves)

    def _afficher_eleves(self, eleves):
        self.table.setRowCount(0)
        for eleve in eleves:
            row = self.table.rowCount()
            self.table.insertRow(row)
            classe_str = str(eleve.nos_classe) if eleve.nos_classe else "—"
            data = [
                eleve.matricule or '', eleve.nom, eleve.prenom,
                classe_str, eleve.sexe or '', eleve.nom_du_parent or '',
                str(eleve.tel_parent or ''),
            ]
            for col, val in enumerate(data):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row, col, item)

            # Action buttons
            actions = QWidget()
            h = QHBoxLayout(actions)
            h.setContentsMargins(4, 2, 4, 2)
            h.setSpacing(4)

            btn_voir = QPushButton("Voir")
            btn_voir.setObjectName("btn_primary")
            btn_voir.setFixedSize(55, 26)
            btn_voir.clicked.connect(lambda _, eid=eleve.id: self.ouvrir_details.emit(eid))
            h.addWidget(btn_voir)

            btn_del = QPushButton("Suppr.")
            btn_del.setObjectName("btn_danger")
            btn_del.setFixedSize(55, 26)
            btn_del.clicked.connect(lambda _, eid=eleve.id: self._supprimer(eid))
            h.addWidget(btn_del)

            self.table.setCellWidget(row, 7, actions)
            self.table.setRowHeight(row, 42)

    def _ajouter(self):
        from ui.eleves.eleve_form import EleveFormDialog
        dlg = EleveFormDialog(parent=self)
        if dlg.exec():
            self.refresh()

    def _supprimer(self, eleve_id):
        rep = QMessageBox.question(self, "Confirmation",
                                   "Supprimer cet élève ? Cette action est irréversible.",
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            session = get_session()
            eleve = session.get(Eleve, eleve_id)
            if eleve:
                session.delete(eleve)
                session.commit()
                self.refresh()

    def _export_pdf(self):
        from utils.export import export_eleves_pdf
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        eleves = session.query(Eleve).filter_by(annee_scolaire_id=annee.id if annee else None).order_by(Eleve.nom).all()
        export_eleves_pdf(eleves, parent=self)

    def _export_excel(self):
        from utils.export import export_eleves_excel
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        eleves = session.query(Eleve).filter_by(annee_scolaire_id=annee.id if annee else None).order_by(Eleve.nom).all()
        export_eleves_excel(eleves, parent=self)
