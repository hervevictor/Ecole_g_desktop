from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QDateEdit, QCheckBox, QFormLayout,
    QGroupBox, QScrollArea, QWidget, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QDate
from database.connexion import get_session
from database.models import Eleve, NosClasse, AnneeScolaire, generer_matricule
import os


class EleveFormDialog(QDialog):
    def __init__(self, eleve_id=None, parent=None):
        super().__init__(parent)
        self.eleve_id = eleve_id
        self.setWindowTitle("Modifier l'élève" if eleve_id else "Ajouter un élève")
        self.setMinimumWidth(500)
        self.setMinimumHeight(550)
        self._build_ui()
        if eleve_id:
            self._charger(eleve_id)

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(15)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        content = QWidget()
        form_layout = QFormLayout(content)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.nom = QLineEdit(); self.nom.setPlaceholderText("Nom de famille")
        self.prenom = QLineEdit(); self.prenom.setPlaceholderText("Prénom")
        self.sexe = QComboBox()
        self.sexe.addItems(["Masculin", "Féminin"])
        self.date_naissance = QDateEdit()
        self.date_naissance.setCalendarPopup(True)
        self.date_naissance.setDate(QDate(2010, 1, 1))
        self.lieu_naissance = QLineEdit(); self.lieu_naissance.setPlaceholderText("Ville de naissance")
        self.nom_parent = QLineEdit(); self.nom_parent.setPlaceholderText("Nom complet du parent/tuteur")
        self.tel_parent = QLineEdit(); self.tel_parent.setPlaceholderText("Ex: 07XXXXXXXX")
        self.adresse = QLineEdit(); self.adresse.setPlaceholderText("Adresse de résidence")
        self.est_nouveau = QCheckBox("Nouvel élève (première inscription)")

        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        self.classe = QComboBox()
        self.classe.addItem("— Sélectionner une classe —", None)
        if annee:
            classes = session.query(NosClasse).filter_by(annee_scolaire_id=annee.id).all()
            for c in classes:
                self.classe.addItem(str(c), c.id)

        form_layout.addRow("Nom *", self.nom)
        form_layout.addRow("Prénom *", self.prenom)
        form_layout.addRow("Sexe *", self.sexe)
        form_layout.addRow("Date de naissance *", self.date_naissance)
        form_layout.addRow("Lieu de naissance", self.lieu_naissance)
        form_layout.addRow("Classe", self.classe)
        form_layout.addRow("Nom du parent *", self.nom_parent)
        form_layout.addRow("Tél. parent *", self.tel_parent)
        form_layout.addRow("Adresse", self.adresse)
        form_layout.addRow("", self.est_nouveau)

        scroll.setWidget(content)
        main.addWidget(scroll, 1)

        # Buttons
        btns = QHBoxLayout()
        btns.addStretch()
        btn_annuler = QPushButton("Annuler")
        btn_annuler.setObjectName("btn_secondary")
        btn_annuler.clicked.connect(self.reject)
        btns.addWidget(btn_annuler)

        btn_save = QPushButton("Enregistrer")
        btn_save.setObjectName("btn_primary")
        btn_save.clicked.connect(self._sauvegarder)
        btns.addWidget(btn_save)
        main.addLayout(btns)

    def _charger(self, eleve_id):
        session = get_session()
        eleve = session.get(Eleve, eleve_id)
        if not eleve:
            return
        self.nom.setText(eleve.nom)
        self.prenom.setText(eleve.prenom)
        idx = self.sexe.findText(eleve.sexe or "Masculin")
        if idx >= 0: self.sexe.setCurrentIndex(idx)
        if eleve.date_de_naissance:
            d = eleve.date_de_naissance
            self.date_naissance.setDate(QDate(d.year, d.month, d.day))
        self.lieu_naissance.setText(eleve.lieu_de_naissance or '')
        self.nom_parent.setText(eleve.nom_du_parent or '')
        self.tel_parent.setText(str(eleve.tel_parent or ''))
        self.adresse.setText(eleve.adresse or '')
        self.est_nouveau.setChecked(eleve.est_nouveau)
        if eleve.nos_classe_id:
            idx = self.classe.findData(eleve.nos_classe_id)
            if idx >= 0: self.classe.setCurrentIndex(idx)

    def _sauvegarder(self):
        if not self.nom.text().strip() or not self.prenom.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom et le prénom sont obligatoires.")
            return
        if not self.nom_parent.text().strip():
            QMessageBox.warning(self, "Erreur", "Le nom du parent est obligatoire.")
            return

        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        if not annee:
            QMessageBox.critical(self, "Erreur", "Aucune année scolaire active. Configurez d'abord l'année scolaire.")
            return

        if self.eleve_id:
            eleve = session.get(Eleve, self.eleve_id)
        else:
            eleve = Eleve(matricule=generer_matricule(), annee_scolaire_id=annee.id)

        eleve.nom = self.nom.text().strip().upper()
        eleve.prenom = self.prenom.text().strip().capitalize()
        eleve.sexe = self.sexe.currentText()
        d = self.date_naissance.date()
        from datetime import date
        eleve.date_de_naissance = date(d.year(), d.month(), d.day())
        eleve.lieu_de_naissance = self.lieu_naissance.text().strip()
        eleve.nom_du_parent = self.nom_parent.text().strip()
        eleve.tel_parent = self.tel_parent.text().strip()
        eleve.adresse = self.adresse.text().strip()
        eleve.est_nouveau = self.est_nouveau.isChecked()
        eleve.nos_classe_id = self.classe.currentData()

        if not self.eleve_id:
            session.add(eleve)
        session.commit()
        self.accept()
