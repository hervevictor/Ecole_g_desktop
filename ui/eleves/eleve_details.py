from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QTableWidget, QTableWidgetItem, QFrame,
    QScrollArea, QHeaderView, QAbstractItemView, QMessageBox,
    QComboBox, QSpinBox, QDialog, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from database.connexion import get_session
from database.models import (
    Eleve, PaiementEcolage, Note, Bulletin, MatiereClasse,
    Periode, RecuPaiement, AnneeScolaire
)
from sqlalchemy import func
import datetime, random, string


class EleveDetailsPage(QWidget):
    retour = Signal()

    def __init__(self, eleve_id, parent=None):
        super().__init__(parent)
        self.eleve_id = eleve_id
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 20)
        layout.setSpacing(15)

        # Header
        header = QHBoxLayout()
        btn_retour = QPushButton("← Retour")
        btn_retour.setObjectName("btn_secondary")
        btn_retour.setFixedHeight(32)
        btn_retour.clicked.connect(self.retour.emit)
        header.addWidget(btn_retour)

        self.lbl_titre = QLabel()
        font = QFont(); font.setPointSize(17); font.setBold(True)
        self.lbl_titre.setFont(font)
        self.lbl_titre.setStyleSheet("color: #1a365d;")
        header.addWidget(self.lbl_titre)
        header.addStretch()

        btn_edit = QPushButton("Modifier")
        btn_edit.setObjectName("btn_primary")
        btn_edit.setFixedHeight(32)
        btn_edit.clicked.connect(self._modifier)
        header.addWidget(btn_edit)
        layout.addLayout(header)

        # Info card
        self.info_card = QFrame()
        self.info_card.setObjectName("card")
        info_layout = QHBoxLayout(self.info_card)
        info_layout.setContentsMargins(18, 14, 18, 14)
        info_layout.setSpacing(30)

        self.lbl_matricule = QLabel()
        self.lbl_classe = QLabel()
        self.lbl_parent = QLabel()
        self.lbl_tel = QLabel()
        self.lbl_statut_paiement = QLabel()

        for lbl in [self.lbl_matricule, self.lbl_classe, self.lbl_parent,
                    self.lbl_tel, self.lbl_statut_paiement]:
            lbl.setStyleSheet("color: #4a5568; font-size: 13px;")
            info_layout.addWidget(lbl)
        info_layout.addStretch()
        layout.addWidget(self.info_card)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_paiements_tab(), "Paiements")
        self.tabs.addTab(self._build_notes_tab(), "Notes")
        self.tabs.addTab(self._build_bulletins_tab(), "Bulletins")
        layout.addWidget(self.tabs, 1)

    def _build_paiements_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)

        # Summary
        self.pay_summary = QHBoxLayout()
        layout.addLayout(self.pay_summary)

        # Add payment button
        h = QHBoxLayout()
        btn_payer = QPushButton("+ Enregistrer un paiement")
        btn_payer.setObjectName("btn_success")
        btn_payer.clicked.connect(self._ajouter_paiement)
        h.addWidget(btn_payer)
        h.addStretch()
        btn_recu = QPushButton("Imprimer historique")
        btn_recu.setObjectName("btn_secondary")
        btn_recu.clicked.connect(self._imprimer_historique)
        h.addWidget(btn_recu)
        layout.addLayout(h)

        self.table_paiements = QTableWidget()
        self.table_paiements.setColumnCount(6)
        self.table_paiements.setHorizontalHeaderLabels([
            "Date", "Montant", "Mode", "Référence", "Statut", "Actions"
        ])
        self.table_paiements.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_paiements.verticalHeader().setVisible(False)
        self.table_paiements.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_paiements.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.table_paiements.setColumnWidth(5, 150)
        layout.addWidget(self.table_paiements)
        return w

    def _build_notes_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)

        h = QHBoxLayout()
        btn_add_note = QPushButton("+ Ajouter une note")
        btn_add_note.setObjectName("btn_primary")
        btn_add_note.clicked.connect(self._ajouter_note)
        h.addWidget(btn_add_note)
        h.addStretch()
        layout.addLayout(h)

        self.table_notes = QTableWidget()
        self.table_notes.setColumnCount(4)
        self.table_notes.setHorizontalHeaderLabels(["Période", "Matière", "Note (/20)", "Coefficient"])
        self.table_notes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_notes.verticalHeader().setVisible(False)
        self.table_notes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_notes)
        return w

    def _build_bulletins_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(10, 10, 10, 10)

        h = QHBoxLayout()
        btn_gen = QPushButton("Générer bulletin")
        btn_gen.setObjectName("btn_primary")
        btn_gen.clicked.connect(self._generer_bulletin)
        h.addWidget(btn_gen)
        h.addStretch()
        layout.addLayout(h)

        self.table_bulletins = QTableWidget()
        self.table_bulletins.setColumnCount(4)
        self.table_bulletins.setHorizontalHeaderLabels(["Période", "Moyenne", "Rang", "Appréciation"])
        self.table_bulletins.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_bulletins.verticalHeader().setVisible(False)
        self.table_bulletins.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table_bulletins)
        return w

    def refresh(self):
        session = get_session()
        eleve = session.get(Eleve, self.eleve_id)
        if not eleve:
            return

        self.lbl_titre.setText(f"{eleve.nom} {eleve.prenom}")
        self.lbl_matricule.setText(f"Matricule : <b>{eleve.matricule}</b>")
        classe_str = str(eleve.nos_classe) if eleve.nos_classe else "Non assigné"
        self.lbl_classe.setText(f"Classe : <b>{classe_str}</b>")
        self.lbl_parent.setText(f"Parent : {eleve.nom_du_parent or '—'}")
        self.lbl_tel.setText(f"Tél : {eleve.tel_parent or '—'}")

        # Paiement summary
        du = eleve.montant_total_du(session)
        paye = eleve.montant_total_paye(session)
        reste = eleve.reste_a_payer(session)
        color = "#276749" if reste <= 0 else "#c53030"
        self.lbl_statut_paiement.setText(
            f"Reste à payer : <b style='color:{color}'>{reste:,} FCFA</b>"
        )

        # Clear summary
        for i in reversed(range(self.pay_summary.count())):
            item = self.pay_summary.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        for label, val, color in [
            ("Total dû", f"{du:,} FCFA", "#c53030"),
            ("Payé", f"{paye:,} FCFA", "#276749"),
            ("Reste", f"{reste:,} FCFA", "#c53030" if reste > 0 else "#276749"),
        ]:
            frame = QFrame(); frame.setObjectName("card")
            fl = QVBoxLayout(frame); fl.setContentsMargins(12, 8, 12, 8)
            fl.addWidget(QLabel(label))
            v = QLabel(f"<b>{val}</b>")
            v.setStyleSheet(f"color: {color}; font-size: 15px;")
            fl.addWidget(v)
            self.pay_summary.addWidget(frame)

        self._charger_paiements(session, eleve)
        self._charger_notes(session, eleve)
        self._charger_bulletins(session, eleve)

    def _charger_paiements(self, session, eleve):
        paiements = session.query(PaiementEcolage).filter_by(eleve_id=eleve.id).order_by(
            PaiementEcolage.date_paiement.desc()).all()
        self.table_paiements.setRowCount(0)
        statut_labels = {
            'valide': ('Validé', '#276749', '#c6f6d5'),
            'en_attente': ('En attente', '#744210', '#fefcbf'),
            'rejete': ('Rejeté', '#742a2a', '#fed7d7'),
        }
        for p in paiements:
            row = self.table_paiements.rowCount()
            self.table_paiements.insertRow(row)
            date_str = p.date_paiement.strftime('%d/%m/%Y') if p.date_paiement else '—'
            for col, val in enumerate([
                date_str, f"{p.montant:,} FCFA", p.mode_paiement or '—', p.reference or '—'
            ]):
                self.table_paiements.setItem(row, col, QTableWidgetItem(val))

            txt, fg, bg = statut_labels.get(p.statut, (p.statut, '#2d3748', '#edf2f7'))
            badge = QLabel(f"  {txt}  ")
            badge.setStyleSheet(f"background:{bg}; color:{fg}; border-radius:8px; font-size:11px; font-weight:bold;")
            badge.setAlignment(Qt.AlignCenter)
            self.table_paiements.setCellWidget(row, 4, badge)

            actions = QWidget()
            ah = QHBoxLayout(actions); ah.setContentsMargins(2, 1, 2, 1); ah.setSpacing(3)
            if p.statut == 'en_attente':
                btn_v = QPushButton("Valider")
                btn_v.setObjectName("btn_success")
                btn_v.setFixedSize(60, 24)
                btn_v.clicked.connect(lambda _, pid=p.id: self._valider_paiement(pid))
                ah.addWidget(btn_v)
            btn_d = QPushButton("Suppr.")
            btn_d.setObjectName("btn_danger")
            btn_d.setFixedSize(55, 24)
            btn_d.clicked.connect(lambda _, pid=p.id: self._supprimer_paiement(pid))
            ah.addWidget(btn_d)
            self.table_paiements.setCellWidget(row, 5, actions)
            self.table_paiements.setRowHeight(row, 40)

    def _charger_notes(self, session, eleve):
        notes = session.query(Note).filter_by(eleve_id=eleve.id).all()
        self.table_notes.setRowCount(0)
        for note in notes:
            row = self.table_notes.rowCount()
            self.table_notes.insertRow(row)
            periode = str(note.periode) if note.periode else '—'
            matiere = note.matiere_classe.matiere.nom if note.matiere_classe and note.matiere_classe.matiere else '—'
            coef = str(note.matiere_classe.coefficient) if note.matiere_classe else '1'
            for col, val in enumerate([periode, matiere, str(note.valeur), coef]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_notes.setItem(row, col, item)

    def _charger_bulletins(self, session, eleve):
        bulletins = session.query(Bulletin).filter_by(eleve_id=eleve.id).all()
        self.table_bulletins.setRowCount(0)
        for b in bulletins:
            row = self.table_bulletins.rowCount()
            self.table_bulletins.insertRow(row)
            periode = str(b.periode) if b.periode else '—'
            moyenne = f"{b.moyenne}/20" if b.moyenne is not None else '—'
            rang = str(b.rang) if b.rang else '—'
            for col, val in enumerate([periode, moyenne, rang, b.appreciation or '—']):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignCenter)
                self.table_bulletins.setItem(row, col, item)

    def _ajouter_paiement(self):
        dlg = PaiementDialog(self.eleve_id, parent=self)
        if dlg.exec():
            self.refresh()

    def _valider_paiement(self, paiement_id):
        session = get_session()
        p = session.get(PaiementEcolage, paiement_id)
        if p:
            p.statut = 'valide'
            # Générer un reçu
            if not p.recu:
                num = 'REC' + ''.join(random.choices(string.digits, k=6))
                session.add(RecuPaiement(paiement_id=p.id, numero_recu=num))
            session.commit()
            self.refresh()

    def _supprimer_paiement(self, paiement_id):
        rep = QMessageBox.question(self, "Confirmation", "Supprimer ce paiement ?",
                                   QMessageBox.Yes | QMessageBox.No)
        if rep == QMessageBox.Yes:
            session = get_session()
            p = session.get(PaiementEcolage, paiement_id)
            if p:
                session.delete(p)
                session.commit()
                self.refresh()

    def _ajouter_note(self):
        dlg = NoteDialog(self.eleve_id, parent=self)
        if dlg.exec():
            self.refresh()

    def _generer_bulletin(self):
        from utils.bulletins import generer_bulletin_eleve
        session = get_session()
        generer_bulletin_eleve(self.eleve_id, session)
        self.refresh()

    def _modifier(self):
        from ui.eleves.eleve_form import EleveFormDialog
        dlg = EleveFormDialog(eleve_id=self.eleve_id, parent=self)
        if dlg.exec():
            self.refresh()

    def _imprimer_historique(self):
        from utils.export import export_historique_paiement_pdf
        session = get_session()
        eleve = session.get(Eleve, self.eleve_id)
        export_historique_paiement_pdf(eleve, session, parent=self)


class PaiementDialog(QDialog):
    def __init__(self, eleve_id, parent=None):
        super().__init__(parent)
        self.eleve_id = eleve_id
        self.setWindowTitle("Enregistrer un paiement")
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        form = QFormLayout()
        self.montant = QSpinBox()
        self.montant.setRange(0, 10_000_000)
        self.montant.setSingleStep(1000)
        self.montant.setSuffix(" FCFA")
        self.montant.setFixedHeight(36)
        form.addRow("Montant *", self.montant)

        self.mode = QComboBox()
        self.mode.addItems(["Espèces", "Mobile Money", "Virement", "Chèque"])
        self.mode.setFixedHeight(36)
        form.addRow("Mode de paiement", self.mode)

        self.reference = QLineEdit()
        self.reference.setPlaceholderText("Numéro de transaction (optionnel)")
        self.reference.setFixedHeight(36)
        form.addRow("Référence", self.reference)

        self.statut = QComboBox()
        self.statut.addItems(["en_attente", "valide"])
        self.statut.setFixedHeight(36)
        form.addRow("Statut initial", self.statut)

        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Annuler"); btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        btn_ok = QPushButton("Enregistrer"); btn_ok.setObjectName("btn_success")
        btn_ok.clicked.connect(self._sauvegarder)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def _sauvegarder(self):
        if self.montant.value() <= 0:
            QMessageBox.warning(self, "Erreur", "Le montant doit être supérieur à 0.")
            return
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        p = PaiementEcolage(
            eleve_id=self.eleve_id,
            montant=self.montant.value(),
            mode_paiement=self.mode.currentText(),
            reference=self.reference.text().strip(),
            statut=self.statut.currentText(),
            annee_scolaire_id=annee.id if annee else None,
        )
        if p.statut == 'valide':
            num = 'REC' + ''.join(random.choices(string.digits, k=6))
            session.add(p)
            session.flush()
            session.add(RecuPaiement(paiement_id=p.id, numero_recu=num))
        else:
            session.add(p)
        session.commit()
        self.accept()


class NoteDialog(QDialog):
    def __init__(self, eleve_id, parent=None):
        super().__init__(parent)
        self.eleve_id = eleve_id
        self.setWindowTitle("Ajouter une note")
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        form = QFormLayout()
        session = get_session()
        eleve = session.get(Eleve, self.eleve_id)

        self.periode_cb = QComboBox()
        self.periode_cb.setFixedHeight(36)
        if eleve and eleve.nos_classe:
            periodes = session.query(Periode).filter_by(
                niveau_id=eleve.nos_classe.classe.niveau_id if eleve.nos_classe.classe else None
            ).all()
            for p in periodes:
                self.periode_cb.addItem(str(p), p.id)
        form.addRow("Période *", self.periode_cb)

        self.matiere_cb = QComboBox()
        self.matiere_cb.setFixedHeight(36)
        if eleve and eleve.nos_classe and eleve.nos_classe.classe:
            mcs = session.query(MatiereClasse).filter_by(classe_id=eleve.nos_classe.classe_id).all()
            for mc in mcs:
                self.matiere_cb.addItem(f"{mc.matiere.nom} (coef {mc.coefficient})", mc.id)
        form.addRow("Matière *", self.matiere_cb)

        self.valeur = QSpinBox()
        self.valeur.setRange(0, 20)
        self.valeur.setFixedHeight(36)
        form.addRow("Note (/20) *", self.valeur)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Annuler"); btn_cancel.setObjectName("btn_secondary")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)
        btn_ok = QPushButton("Enregistrer"); btn_ok.setObjectName("btn_primary")
        btn_ok.clicked.connect(self._sauvegarder)
        btns.addWidget(btn_ok)
        layout.addLayout(btns)

    def _sauvegarder(self):
        periode_id = self.periode_cb.currentData()
        matiere_classe_id = self.matiere_cb.currentData()
        if not periode_id or not matiere_classe_id:
            QMessageBox.warning(self, "Erreur", "Sélectionnez la période et la matière.")
            return
        session = get_session()
        existing = session.query(Note).filter_by(
            eleve_id=self.eleve_id,
            matiere_classe_id=matiere_classe_id,
            periode_id=periode_id
        ).first()
        if existing:
            existing.valeur = self.valeur.value()
        else:
            session.add(Note(
                eleve_id=self.eleve_id,
                matiere_classe_id=matiere_classe_id,
                periode_id=periode_id,
                valeur=self.valeur.value()
            ))
        session.commit()
        self.accept()
