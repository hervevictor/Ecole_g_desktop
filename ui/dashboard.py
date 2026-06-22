from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGridLayout, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database.connexion import get_session
from database.models import (
    Eleve, PaiementEcolage, Professeur, NosClasse,
    AnneeScolaire, Bulletin, Note, Niveau
)
from sqlalchemy import func


def make_stat_card(title, value, subtitle, color):
    card = QFrame()
    card.setObjectName("stat_card")
    card.setMinimumHeight(110)
    layout = QVBoxLayout(card)
    layout.setContentsMargins(18, 14, 18, 14)
    layout.setSpacing(4)

    accent = QFrame()
    accent.setFixedHeight(4)
    accent.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
    layout.addWidget(accent)

    lbl_title = QLabel(title)
    lbl_title.setStyleSheet("color: #718096; font-size: 12px; font-weight: bold;")
    layout.addWidget(lbl_title)

    lbl_value = QLabel(str(value))
    font = QFont()
    font.setPointSize(28)
    font.setBold(True)
    lbl_value.setFont(font)
    lbl_value.setStyleSheet(f"color: {color};")
    layout.addWidget(lbl_value)

    lbl_sub = QLabel(subtitle)
    lbl_sub.setStyleSheet("color: #a0aec0; font-size: 11px;")
    layout.addWidget(lbl_sub)

    return card


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 15, 25, 20)
        main_layout.setSpacing(20)

        title = QLabel("Tableau de bord")
        title.setObjectName("page_title")
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        title.setFont(font)
        title.setStyleSheet("color: #1a365d; margin-bottom: 5px;")
        main_layout.addWidget(title)

        # Stats grid
        self.stats_grid = QGridLayout()
        self.stats_grid.setSpacing(15)
        main_layout.addLayout(self.stats_grid)

        # Scroll area for lower content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(20)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll.setWidget(self.scroll_content)
        main_layout.addWidget(scroll, 1)

    def refresh(self):
        # Clear stats grid
        for i in reversed(range(self.stats_grid.count())):
            self.stats_grid.itemAt(i).widget().setParent(None)

        session = get_session()
        annee = session.query(AnneeScolaire).filter_by(actif=True).first()
        annee_id = annee.id if annee else None

        nb_eleves = session.query(func.count(Eleve.id)).filter_by(annee_scolaire_id=annee_id).scalar() or 0
        nb_profs = session.query(func.count(Professeur.id)).filter_by(annee_scolaire_id=annee_id).scalar() or 0
        nb_classes = session.query(func.count(NosClasse.id)).filter_by(annee_scolaire_id=annee_id).scalar() or 0

        total_du = session.query(func.sum(PaiementEcolage.montant)).filter(
            PaiementEcolage.annee_scolaire_id == annee_id,
            PaiementEcolage.statut == 'valide'
        ).scalar() or 0

        paiements_attente = session.query(func.count(PaiementEcolage.id)).filter(
            PaiementEcolage.annee_scolaire_id == annee_id,
            PaiementEcolage.statut == 'en_attente'
        ).scalar() or 0

        cards = [
            ("Élèves", nb_eleves, "cette année scolaire", "#3182ce"),
            ("Professeurs", nb_profs, "inscrits", "#38a169"),
            ("Classes", nb_classes, "actives", "#805ad5"),
            ("Paiements validés", f"{total_du:,} F", "FCFA collectés", "#d69e2e"),
            ("En attente", paiements_attente, "paiements à valider", "#e53e3e"),
        ]

        for i, (title, value, sub, color) in enumerate(cards):
            card = make_stat_card(title, value, sub, color)
            self.stats_grid.addWidget(card, i // 3, i % 3)

        # Clear scroll content
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        # Année scolaire info
        if annee:
            self._add_annee_section(annee)

        # Répartition par niveau
        self._add_repartition_section(session, annee_id)

        self.scroll_layout.addStretch()

    def _add_annee_section(self, annee):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)

        h = QHBoxLayout()
        title = QLabel("Année scolaire active")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a365d;")
        h.addWidget(title)
        h.addStretch()
        badge = QLabel(f"  {annee}  ")
        badge.setStyleSheet("""
            background-color: #ebf8ff; color: #2b6cb0;
            border-radius: 12px; padding: 4px 12px;
            font-weight: bold; font-size: 13px;
        """)
        h.addWidget(badge)
        layout.addLayout(h)
        self.scroll_layout.addWidget(card)

    def _add_repartition_section(self, session, annee_id):
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(10)

        title = QLabel("Répartition par niveau")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1a365d; margin-bottom: 5px;")
        layout.addWidget(title)

        niveaux = session.query(Niveau).filter_by(annee_scolaire_id=annee_id).all()
        if not niveaux:
            layout.addWidget(QLabel("Aucun niveau configuré pour cette année."))
        else:
            for niveau in niveaux:
                nb = session.query(func.count(Eleve.id)).join(
                    NosClasse, Eleve.nos_classe_id == NosClasse.id
                ).join(
                    NosClasse.classe
                ).filter(
                    NosClasse.annee_scolaire_id == annee_id,
                    NosClasse.classe.has(niveau_id=niveau.id)
                ).scalar() or 0

                row = QHBoxLayout()
                lbl = QLabel(f"  {niveau.nom} ({niveau.type_niveau})")
                lbl.setStyleSheet("color: #4a5568;")
                row.addWidget(lbl)
                row.addStretch()
                val = QLabel(f"<b>{nb}</b> élèves")
                val.setStyleSheet("color: #2b6cb0;")
                row.addWidget(val)
                layout.addLayout(row)

                sep = QFrame()
                sep.setFrameShape(QFrame.HLine)
                sep.setStyleSheet("color: #e2e8f0;")
                layout.addWidget(sep)

        self.scroll_layout.addWidget(card)
