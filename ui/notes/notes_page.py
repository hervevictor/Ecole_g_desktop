from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView,
    QAbstractItemView, QMessageBox, QSpinBox, QDialog, QFormLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.connexion import get_session
from database.models import Note, Eleve, MatiereClasse, Periode, NosClasse, AnneeScolaire


class NotesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 20)
        layout.setSpacing(15)

        title = QLabel("Saisie des Notes")
        font = QFont(); font.setPointSize(18); font.setBold(True)
        title.setFont(font); title.setStyleSheet("color: #1a365d;")
        layout.addWidget(title)

        # Filters
        filters = QHBoxLayout()
        self.filtre_classe = QComboBox(); self.filtre_classe.setFixedHeight(36)
        self.filtre_classe.addItem("— Sélectionner une classe —", None)
        self.filtre_classe.currentIndexChanged.connect(self._on_classe_changed)
        filters.addWidget(QLabel("Classe :"))
        filters.addWidget(self.filtre_classe)

        self.filtre_periode = QComboBox(); self.filtre_periode.setFixedHeight(36)
        self.filtre_periode.addItem("— Sélectionner une période —", None)
        self.filtre_periode.currentIndexChanged.connect(self._charger_notes)
        filters.addWidget(QLabel("Période :"))
        filters.addWidget(self.filtre_periode)

        self.filtre_matiere = QComboBox(); self.filtre_matiere.setFixedHeight(36)
        self.filtre_matiere.addItem("Toutes les matières", None)
        self.filtre_matiere.currentIndexChanged.connect(self._charger_notes)
        filters.addWidget(QLabel("Matière :"))
        filters.addWidget(self.filtre_matiere)
        filters.addStretch()

        btn_gen_bulletins = QPushButton("Générer bulletins de la classe")
        btn_gen_bulletins.setObjectName("btn_success"); btn_gen_bulletins.setFixedHeight(36)
        btn_gen_bulletins.clicked.connect(self._generer_bulletins_classe)
        filters.addWidget(btn_gen_bulletins)
        layout.addLayout(filters)

        self.lbl_info = QLabel()
        self.lbl_info.setStyleSheet("color: #718096; font-size: 12px;")
        layout.addWidget(self.lbl_info)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Élève", "Matricule", "Matière", "Coef", "Note /20"])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 120)
        self.table.doubleClicked.connect(self._modifier_note)
        layout.addWidget(self.table, 1)

        layout.addWidget(QLabel("Double-cliquez sur une note pour la modifier."))

    def refresh(self):
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        annee_id = annee.id if annee else None

        self.filtre_classe.blockSignals(True)
        self.filtre_classe.clear()
        self.filtre_classe.addItem("— Sélectionner une classe —", None)
        for c in session.query(NosClasse).filter_by(annee_scolaire_id=annee_id).all():
            self.filtre_classe.addItem(str(c), c.id)
        self.filtre_classe.blockSignals(False)

    def _on_classe_changed(self):
        session = get_session()
        nos_classe_id = self.filtre_classe.currentData()

        self.filtre_periode.blockSignals(True)
        self.filtre_periode.clear()
        self.filtre_periode.addItem("— Sélectionner une période —", None)

        self.filtre_matiere.blockSignals(True)
        self.filtre_matiere.clear()
        self.filtre_matiere.addItem("Toutes les matières", None)

        if nos_classe_id:
            nos = session.get(NosClasse, nos_classe_id)
            if nos and nos.classe:
                niveau_id = nos.classe.niveau_id
                annee_id = nos.annee_scolaire_id
                periodes = session.query(Periode).filter_by(niveau_id=niveau_id, annee_scolaire_id=annee_id).all()
                for p in periodes:
                    self.filtre_periode.addItem(str(p), p.id)
                mcs = session.query(MatiereClasse).filter_by(classe_id=nos.classe_id).all()
                for mc in mcs:
                    self.filtre_matiere.addItem(mc.matiere.nom if mc.matiere else '?', mc.id)

        self.filtre_periode.blockSignals(False)
        self.filtre_matiere.blockSignals(False)
        self._charger_notes()

    def _charger_notes(self):
        nos_classe_id = self.filtre_classe.currentData()
        periode_id = self.filtre_periode.currentData()
        matiere_id = self.filtre_matiere.currentData()

        if not nos_classe_id or not periode_id:
            self.table.setRowCount(0)
            self.lbl_info.setText("Sélectionnez une classe et une période.")
            return

        session = get_session()
        eleves = session.query(Eleve).filter_by(nos_classe_id=nos_classe_id).order_by(Eleve.nom).all()

        nos = session.get(NosClasse, nos_classe_id)
        if not nos or not nos.classe:
            return
        mcs = session.query(MatiereClasse).filter_by(classe_id=nos.classe_id)
        if matiere_id:
            mcs = mcs.filter_by(id=matiere_id)
        mcs = mcs.all()

        self.table.setRowCount(0)
        for eleve in eleves:
            for mc in mcs:
                note = session.query(Note).filter_by(
                    eleve_id=eleve.id,
                    matiere_classe_id=mc.id,
                    periode_id=periode_id
                ).first()
                row = self.table.rowCount()
                self.table.insertRow(row)
                nom_str = f"{eleve.nom} {eleve.prenom}"
                mat_str = mc.matiere.nom if mc.matiere else '?'
                note_str = str(note.valeur) if note else "—"
                for col, val in enumerate([nom_str, eleve.matricule or '', mat_str, str(mc.coefficient), note_str]):
                    item = QTableWidgetItem(val)
                    item.setTextAlignment(Qt.AlignCenter if col >= 3 else Qt.AlignVCenter | Qt.AlignLeft)
                    item.setData(Qt.UserRole, (eleve.id, mc.id, periode_id, note.id if note else None))
                    self.table.setItem(row, col, item)
                self.table.setRowHeight(row, 38)

        self.lbl_info.setText(f"{len(eleves)} élève(s) — double-cliquez pour modifier une note.")

    def _modifier_note(self, index):
        item = self.table.item(index.row(), 0)
        if not item:
            return
        data = item.data(Qt.UserRole)
        if not data:
            return
        eleve_id, mc_id, periode_id, note_id = data
        dlg = ModifierNoteDialog(eleve_id, mc_id, periode_id, note_id, parent=self)
        if dlg.exec():
            self._charger_notes()

    def _generer_bulletins_classe(self):
        nos_classe_id = self.filtre_classe.currentData()
        if not nos_classe_id:
            QMessageBox.warning(self, "Erreur", "Sélectionnez d'abord une classe."); return
        from utils.bulletins import generer_bulletins_classe
        session = get_session()
        generer_bulletins_classe(nos_classe_id, session)
        QMessageBox.information(self, "Succès", "Bulletins générés pour toute la classe.")


class ModifierNoteDialog(QDialog):
    def __init__(self, eleve_id, mc_id, periode_id, note_id=None, parent=None):
        super().__init__(parent)
        self.eleve_id = eleve_id
        self.mc_id = mc_id
        self.periode_id = periode_id
        self.note_id = note_id
        self.setWindowTitle("Saisir / Modifier la note")
        self.setMinimumWidth(320)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        form = QFormLayout()

        session = get_session()
        eleve = session.get(Eleve, self.eleve_id)
        mc = session.get(MatiereClasse, self.mc_id)

        self.lbl_eleve = QLabel(str(eleve) if eleve else '?')
        self.lbl_matiere = QLabel(mc.matiere.nom if mc and mc.matiere else '?')
        self.valeur = QSpinBox(); self.valeur.setRange(0, 20); self.valeur.setFixedHeight(36)

        if self.note_id:
            note = session.get(Note, self.note_id)
            if note:
                self.valeur.setValue(note.valeur)

        form.addRow("Élève :", self.lbl_eleve)
        form.addRow("Matière :", self.lbl_matiere)
        form.addRow("Note (/20) :", self.valeur)
        layout.addLayout(form)

        btns = QHBoxLayout(); btns.addStretch()
        btn_c = QPushButton("Annuler"); btn_c.setObjectName("btn_secondary")
        btn_c.clicked.connect(self.reject); btns.addWidget(btn_c)
        btn_s = QPushButton("Enregistrer"); btn_s.setObjectName("btn_primary")
        btn_s.clicked.connect(self._sauvegarder); btns.addWidget(btn_s)
        layout.addLayout(btns)

    def _sauvegarder(self):
        session = get_session()
        if self.note_id:
            note = session.get(Note, self.note_id)
            if note:
                note.valeur = self.valeur.value()
        else:
            session.add(Note(
                eleve_id=self.eleve_id,
                matiere_classe_id=self.mc_id,
                periode_id=self.periode_id,
                valeur=self.valeur.value()
            ))
        session.commit()
        self.accept()
