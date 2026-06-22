from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit,
    QHeaderView, QAbstractItemView, QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.connexion import get_session
from database.models import PaiementEcolage, AnneeScolaire, Eleve, RecuPaiement
from sqlalchemy import func
import random, string


class PaiementsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 20)
        layout.setSpacing(15)

        title = QLabel("Gestion des Paiements")
        font = QFont(); font.setPointSize(18); font.setBold(True)
        title.setFont(font); title.setStyleSheet("color: #1a365d;")
        layout.addWidget(title)

        # Summary cards
        self.summary_layout = QHBoxLayout()
        layout.addLayout(self.summary_layout)

        # Filters
        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setObjectName("search_input")
        self.search.setPlaceholderText("Rechercher par nom d'élève...")
        self.search.setFixedHeight(36)
        self.search.textChanged.connect(self._filtrer)
        filters.addWidget(self.search, 2)

        self.filtre_statut = QComboBox()
        self.filtre_statut.setFixedHeight(36)
        self.filtre_statut.addItems(["Tous les statuts", "En attente", "Validés", "Rejetés"])
        self.filtre_statut.currentIndexChanged.connect(self._filtrer)
        filters.addWidget(self.filtre_statut)

        btn_valider_tout = QPushButton("Valider sélection")
        btn_valider_tout.setObjectName("btn_success")
        btn_valider_tout.setFixedHeight(36)
        btn_valider_tout.clicked.connect(self._valider_selection)
        filters.addWidget(btn_valider_tout)
        layout.addLayout(filters)

        self.lbl_count = QLabel()
        self.lbl_count.setStyleSheet("color: #718096; font-size: 12px;")
        layout.addWidget(self.lbl_count)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Élève", "Classe", "Montant", "Mode", "Date", "Statut", "Actions"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Fixed)
        self.table.setColumnWidth(6, 160)
        layout.addWidget(self.table, 1)

        self._paiements_data = []

    def refresh(self):
        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        annee_id = annee.id if annee else None

        # Summary
        total_valide = session.query(func.sum(PaiementEcolage.montant)).filter(
            PaiementEcolage.annee_scolaire_id == annee_id,
            PaiementEcolage.statut == 'valide'
        ).scalar() or 0
        nb_attente = session.query(func.count(PaiementEcolage.id)).filter(
            PaiementEcolage.annee_scolaire_id == annee_id,
            PaiementEcolage.statut == 'en_attente'
        ).scalar() or 0

        for i in reversed(range(self.summary_layout.count())):
            item = self.summary_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        for label, val, color in [
            ("Total collecté", f"{total_valide:,} FCFA", "#276749"),
            ("En attente de validation", str(nb_attente), "#c53030"),
        ]:
            frame = QFrame(); frame.setObjectName("card")
            fl = QVBoxLayout(frame); fl.setContentsMargins(15, 10, 15, 10)
            fl.addWidget(QLabel(label))
            v = QLabel(f"<b>{val}</b>")
            v.setStyleSheet(f"color:{color}; font-size:16px;")
            fl.addWidget(v)
            self.summary_layout.addWidget(frame)
        self.summary_layout.addStretch()

        self._paiements_data = (
            session.query(PaiementEcolage)
            .filter_by(annee_scolaire_id=annee_id)
            .order_by(PaiementEcolage.date_paiement.desc())
            .all()
        )
        self._filtrer()

    def _filtrer(self):
        terme = self.search.text().lower()
        statut_filter = self.filtre_statut.currentText()

        paiements = self._paiements_data
        if terme:
            paiements = [p for p in paiements if p.eleve and
                         (terme in p.eleve.nom.lower() or terme in p.eleve.prenom.lower())]

        statut_map = {"En attente": "en_attente", "Validés": "valide", "Rejetés": "rejete"}
        if statut_filter in statut_map:
            paiements = [p for p in paiements if p.statut == statut_map[statut_filter]]

        self.lbl_count.setText(f"{len(paiements)} paiement(s)")
        self._afficher_paiements(paiements)

    def _afficher_paiements(self, paiements):
        self.table.setRowCount(0)
        statut_labels = {
            'valide': ('Validé', '#276749', '#c6f6d5'),
            'en_attente': ('En attente', '#744210', '#fefcbf'),
            'rejete': ('Rejeté', '#742a2a', '#fed7d7'),
        }
        for p in paiements:
            row = self.table.rowCount()
            self.table.insertRow(row)
            eleve_nom = f"{p.eleve.nom} {p.eleve.prenom}" if p.eleve else '—'
            classe_str = str(p.eleve.nos_classe) if p.eleve and p.eleve.nos_classe else '—'
            date_str = p.date_paiement.strftime('%d/%m/%Y') if p.date_paiement else '—'
            for col, val in enumerate([
                eleve_nom, classe_str, f"{p.montant:,} FCFA",
                p.mode_paiement or '—', date_str
            ]):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
                self.table.setItem(row, col, item)

            txt, fg, bg = statut_labels.get(p.statut, (p.statut, '#2d3748', '#edf2f7'))
            badge = QLabel(f"  {txt}  ")
            badge.setStyleSheet(f"background:{bg};color:{fg};border-radius:8px;font-size:11px;font-weight:bold;")
            badge.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 5, badge)

            actions = QWidget()
            ah = QHBoxLayout(actions); ah.setContentsMargins(2, 1, 2, 1); ah.setSpacing(3)
            if p.statut == 'en_attente':
                btn_v = QPushButton("Valider")
                btn_v.setObjectName("btn_success")
                btn_v.setFixedSize(60, 24)
                btn_v.clicked.connect(lambda _, pid=p.id: self._valider(pid))
                ah.addWidget(btn_v)
                btn_r = QPushButton("Rejeter")
                btn_r.setObjectName("btn_danger")
                btn_r.setFixedSize(60, 24)
                btn_r.clicked.connect(lambda _, pid=p.id: self._rejeter(pid))
                ah.addWidget(btn_r)
            self.table.setCellWidget(row, 6, actions)
            self.table.setRowHeight(row, 42)

    def _valider(self, paiement_id):
        session = get_session()
        p = session.get(PaiementEcolage, paiement_id)
        if p:
            p.statut = 'valide'
            if not p.recu:
                num = 'REC' + ''.join(random.choices(string.digits, k=6))
                session.add(RecuPaiement(paiement_id=p.id, numero_recu=num))
            session.commit()
            self.refresh()

    def _rejeter(self, paiement_id):
        session = get_session()
        p = session.get(PaiementEcolage, paiement_id)
        if p:
            p.statut = 'rejete'
            session.commit()
            self.refresh()

    def _valider_selection(self):
        rows = set(i.row() for i in self.table.selectedItems())
        if not rows:
            QMessageBox.information(self, "Info", "Sélectionnez des lignes à valider.")
            return
        session = get_session()
        count = 0
        for row in rows:
            item = self.table.item(row, 0)
            if item:
                eleve_nom = item.text()
                paiements = [p for p in self._paiements_data
                             if p.eleve and f"{p.eleve.nom} {p.eleve.prenom}" == eleve_nom
                             and p.statut == 'en_attente']
                for p in paiements:
                    p.statut = 'valide'
                    if not p.recu:
                        num = 'REC' + ''.join(random.choices(string.digits, k=6))
                        session.add(RecuPaiement(paiement_id=p.id, numero_recu=num))
                    count += 1
        session.commit()
        QMessageBox.information(self, "Succès", f"{count} paiement(s) validé(s).")
        self.refresh()
