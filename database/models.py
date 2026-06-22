from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, Text,
    ForeignKey, UniqueConstraint, create_engine
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import random, string, hashlib, os

Base = declarative_base()

ROLES = ['admin', 'professeur', 'secretaire', 'parent']

ROLE_LABELS = {
    'admin': 'Administrateur',
    'professeur': 'Professeur',
    'secretaire': 'Secrétaire',
    'parent': 'Parent',
}

ROLE_NAV_ACCESS = {
    'admin':      ['dashboard', 'eleves', 'notes', 'paiements', 'profs', 'config', 'profile'],
    'professeur': ['dashboard', 'notes', 'profs', 'profile'],
    'secretaire': ['dashboard', 'eleves', 'paiements', 'profile'],
    'parent':     ['dashboard', 'profile'],
}


def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{h}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, h = stored.split(':')
        return hashlib.sha256((salt + password).encode()).hexdigest() == h
    except Exception:
        return False


class Utilisateur(Base):
    __tablename__ = 'utilisateur'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False, default='secretaire')
    nom = Column(String(100), default='')
    prenom = Column(String(100), default='')
    email = Column(String(100), default='')
    telephone = Column(String(20), default='')
    photo_path = Column(String(500), default='')
    is_active = Column(Boolean, default=True)
    date_creation = Column(DateTime, default=datetime.now)
    professeur_id = Column(Integer, ForeignKey('professeur.id'), nullable=True)

    professeur = relationship('Professeur', foreign_keys=[professeur_id])

    def set_password(self, password: str):
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)

    def role_label(self) -> str:
        return ROLE_LABELS.get(self.role, self.role)

    def __repr__(self):
        return f"{self.username} ({self.role})"


def generer_matricule():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class AnneeScolaire(Base):
    __tablename__ = 'annee_scolaire'
    id = Column(Integer, primary_key=True)
    debut = Column(Integer, nullable=False)
    fin = Column(Integer, nullable=False)
    actif = Column(Boolean, default=False)
    __table_args__ = (UniqueConstraint('debut', 'fin'),)

    niveaux = relationship('Niveau', back_populates='annee_scolaire', cascade='all, delete')
    classes = relationship('Classe', back_populates='annee_scolaire', cascade='all, delete')
    nos_classes = relationship('NosClasse', back_populates='annee_scolaire', cascade='all, delete')
    periodes = relationship('Periode', back_populates='annee_scolaire', cascade='all, delete')
    eleves = relationship('Eleve', back_populates='annee_scolaire', cascade='all, delete')
    paiements = relationship('PaiementEcolage', back_populates='annee_scolaire', cascade='all, delete')

    def __repr__(self):
        return f"{self.debut}-{self.fin}"


class Niveau(Base):
    __tablename__ = 'niveau'
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    type_niveau = Column(String(10), nullable=False)  # COLLEGE / LYCEE
    annee_scolaire_id = Column(Integer, ForeignKey('annee_scolaire.id'), nullable=False)

    annee_scolaire = relationship('AnneeScolaire', back_populates='niveaux')
    classes = relationship('Classe', back_populates='niveau', cascade='all, delete')
    periodes = relationship('Periode', back_populates='niveau', cascade='all, delete')
    professeurs = relationship('Professeur', back_populates='niveau')

    def __repr__(self):
        return f"{self.nom} ({self.type_niveau})"


class Classe(Base):
    __tablename__ = 'classe'
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    niveau_id = Column(Integer, ForeignKey('niveau.id'), nullable=False)
    annee_scolaire_id = Column(Integer, ForeignKey('annee_scolaire.id'), nullable=False)

    niveau = relationship('Niveau', back_populates='classes')
    annee_scolaire = relationship('AnneeScolaire', back_populates='classes')
    nos_classes = relationship('NosClasse', back_populates='classe', cascade='all, delete')
    matiere_classes = relationship('MatiereClasse', back_populates='classe', cascade='all, delete')
    frais = relationship('FraisScolarite', back_populates='classe', uselist=False)

    def __repr__(self):
        return self.nom


class NosClasse(Base):
    __tablename__ = 'nos_classe'
    id = Column(Integer, primary_key=True)
    classe_id = Column(Integer, ForeignKey('classe.id'), nullable=False)
    indice = Column(String(100))
    titulaire = Column(String(100))
    add_date = Column(DateTime, default=datetime.now)
    annee_scolaire_id = Column(Integer, ForeignKey('annee_scolaire.id'), nullable=False)

    classe = relationship('Classe', back_populates='nos_classes')
    annee_scolaire = relationship('AnneeScolaire', back_populates='nos_classes')
    eleves = relationship('Eleve', back_populates='nos_classe')
    matiere_classe_profs = relationship('MatiereClasseProfesseur', back_populates='nos_classe', cascade='all, delete')

    def __repr__(self):
        return f"{self.classe} - {self.indice}"


class TypeMatiere(Base):
    __tablename__ = 'type_matiere'
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    matieres = relationship('Matiere', back_populates='type_matiere')

    def __repr__(self):
        return self.nom


class Matiere(Base):
    __tablename__ = 'matiere'
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    type_matiere_id = Column(Integer, ForeignKey('type_matiere.id'), nullable=False)

    type_matiere = relationship('TypeMatiere', back_populates='matieres')
    matiere_classes = relationship('MatiereClasse', back_populates='matiere', cascade='all, delete')

    def __repr__(self):
        return self.nom


class MatiereClasse(Base):
    __tablename__ = 'matiere_classe'
    id = Column(Integer, primary_key=True)
    classe_id = Column(Integer, ForeignKey('classe.id'), nullable=False)
    matiere_id = Column(Integer, ForeignKey('matiere.id'), nullable=False)
    coefficient = Column(Integer, default=1)
    __table_args__ = (UniqueConstraint('classe_id', 'matiere_id'),)

    classe = relationship('Classe', back_populates='matiere_classes')
    matiere = relationship('Matiere', back_populates='matiere_classes')
    notes = relationship('Note', back_populates='matiere_classe', cascade='all, delete')
    profs = relationship('MatiereClasseProfesseur', back_populates='matiere_classe', cascade='all, delete')

    def __repr__(self):
        return f"{self.matiere.nom}"


class MatiereClasseProfesseur(Base):
    __tablename__ = 'matiere_classe_professeur'
    id = Column(Integer, primary_key=True)
    matiere_classe_id = Column(Integer, ForeignKey('matiere_classe.id'), nullable=False)
    nos_classe_id = Column(Integer, ForeignKey('nos_classe.id'), nullable=False)
    professeur = Column(String(100))
    annee_scolaire_id = Column(Integer, ForeignKey('annee_scolaire.id'), nullable=False)
    __table_args__ = (UniqueConstraint('matiere_classe_id', 'nos_classe_id'),)

    matiere_classe = relationship('MatiereClasse', back_populates='profs')
    nos_classe = relationship('NosClasse', back_populates='matiere_classe_profs')
    annee_scolaire = relationship('AnneeScolaire')


class Periode(Base):
    __tablename__ = 'periode'
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    niveau_id = Column(Integer, ForeignKey('niveau.id'), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    est_active = Column(Boolean, default=False)
    annee_scolaire_id = Column(Integer, ForeignKey('annee_scolaire.id'), nullable=False)

    niveau = relationship('Niveau', back_populates='periodes')
    annee_scolaire = relationship('AnneeScolaire', back_populates='periodes')
    notes = relationship('Note', back_populates='periode', cascade='all, delete')
    bulletins = relationship('Bulletin', back_populates='periode', cascade='all, delete')

    def __repr__(self):
        return f"{self.nom} - {self.niveau.nom if self.niveau else ''}"


class FraisScolarite(Base):
    __tablename__ = 'frais_scolarite'
    id = Column(Integer, primary_key=True)
    classe_id = Column(Integer, ForeignKey('classe.id'), nullable=False, unique=True)
    frais_d_inscription = Column(Integer, nullable=False)
    montant_d_ecolage = Column(Integer, nullable=False)
    annee_scolaire_id = Column(Integer, ForeignKey('annee_scolaire.id'), nullable=False)

    classe = relationship('Classe', back_populates='frais')
    annee_scolaire = relationship('AnneeScolaire')


class ConfigurationEtablissement(Base):
    __tablename__ = 'configuration_etablissement'
    id = Column(Integer, primary_key=True)
    nom_etablissement = Column(String(200), default='')
    adresse = Column(Text, default='')
    telephone = Column(String(50), default='')
    email = Column(String(100), default='')
    logo = Column(String(500), default='')
    devise = Column(String(200), default='')
    numero_paiement_1 = Column(String(50), default='')
    numero_paiement_2 = Column(String(50), default='')
    directeur = Column(String(200), default='')


class Eleve(Base):
    __tablename__ = 'eleve'
    id = Column(Integer, primary_key=True)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50), nullable=False)
    nos_classe_id = Column(Integer, ForeignKey('nos_classe.id'), nullable=True)
    sexe = Column(String(20))
    date_de_naissance = Column(Date)
    lieu_de_naissance = Column(String(100))
    nom_du_parent = Column(String(100))
    tel_parent = Column(String(20))
    adresse = Column(Text)
    est_nouveau = Column(Boolean, default=False)
    matricule = Column(String(10), unique=True)
    add_date = Column(DateTime, default=datetime.now)
    annee_scolaire_id = Column(Integer, ForeignKey('annee_scolaire.id'), nullable=False)
    photo = Column(String(500), default='')

    nos_classe = relationship('NosClasse', back_populates='eleves')
    annee_scolaire = relationship('AnneeScolaire', back_populates='eleves')
    paiements = relationship('PaiementEcolage', back_populates='eleve', cascade='all, delete')
    notes = relationship('Note', back_populates='eleve', cascade='all, delete')
    bulletins = relationship('Bulletin', back_populates='eleve', cascade='all, delete')

    def __repr__(self):
        return f"{self.nom} {self.prenom} ({self.matricule})"

    def montant_total_du(self, session):
        if not self.nos_classe:
            return 0
        frais = session.query(FraisScolarite).filter_by(classe_id=self.nos_classe.classe_id).first()
        return frais.montant_d_ecolage if frais else 0

    def montant_total_paye(self, session):
        from sqlalchemy import func
        result = session.query(func.sum(PaiementEcolage.montant)).filter_by(
            eleve_id=self.id, statut='valide'
        ).scalar()
        return result or 0

    def reste_a_payer(self, session):
        return self.montant_total_du(session) - self.montant_total_paye(session)


class PaiementEcolage(Base):
    __tablename__ = 'paiement_ecolage'
    id = Column(Integer, primary_key=True)
    eleve_id = Column(Integer, ForeignKey('eleve.id'), nullable=False)
    montant = Column(Integer, nullable=False)
    date_paiement = Column(DateTime, default=datetime.now)
    statut = Column(String(20), default='en_attente')  # en_attente, valide, rejete
    mode_paiement = Column(String(50), default='')
    reference = Column(String(100), default='')
    annee_scolaire_id = Column(Integer, ForeignKey('annee_scolaire.id'), nullable=False)
    commentaire = Column(Text, default='')

    eleve = relationship('Eleve', back_populates='paiements')
    annee_scolaire = relationship('AnneeScolaire', back_populates='paiements')
    recu = relationship('RecuPaiement', back_populates='paiement', uselist=False, cascade='all, delete')

    def __repr__(self):
        return f"Paiement {self.montant} FCFA - {self.statut}"


class RecuPaiement(Base):
    __tablename__ = 'recu_paiement'
    id = Column(Integer, primary_key=True)
    paiement_id = Column(Integer, ForeignKey('paiement_ecolage.id'), nullable=False, unique=True)
    numero_recu = Column(String(50), unique=True)
    date_emission = Column(DateTime, default=datetime.now)

    paiement = relationship('PaiementEcolage', back_populates='recu')


class Note(Base):
    __tablename__ = 'note'
    id = Column(Integer, primary_key=True)
    eleve_id = Column(Integer, ForeignKey('eleve.id'), nullable=False)
    matiere_classe_id = Column(Integer, ForeignKey('matiere_classe.id'), nullable=False)
    periode_id = Column(Integer, ForeignKey('periode.id'), nullable=False)
    valeur = Column(Integer, nullable=False)
    __table_args__ = (UniqueConstraint('eleve_id', 'matiere_classe_id', 'periode_id'),)

    eleve = relationship('Eleve', back_populates='notes')
    matiere_classe = relationship('MatiereClasse', back_populates='notes')
    periode = relationship('Periode', back_populates='notes')


class Bulletin(Base):
    __tablename__ = 'bulletin'
    id = Column(Integer, primary_key=True)
    eleve_id = Column(Integer, ForeignKey('eleve.id'), nullable=False)
    periode_id = Column(Integer, ForeignKey('periode.id'), nullable=False)
    moyenne = Column(Integer, nullable=True)
    rang = Column(Integer, nullable=True)
    appreciation = Column(String(200), default='')
    __table_args__ = (UniqueConstraint('eleve_id', 'periode_id'),)

    eleve = relationship('Eleve', back_populates='bulletins')
    periode = relationship('Periode', back_populates='bulletins')


class Professeur(Base):
    __tablename__ = 'professeur'
    id = Column(Integer, primary_key=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    telephone = Column(String(20), default='')
    email = Column(String(100), default='')
    specialite = Column(String(200), default='')
    niveau_id = Column(Integer, ForeignKey('niveau.id'), nullable=True)
    annee_scolaire_id = Column(Integer, ForeignKey('annee_scolaire.id'), nullable=False)
    matricule = Column(String(20), default='')
    add_date = Column(DateTime, default=datetime.now)

    niveau = relationship('Niveau', back_populates='professeurs')
    emplois_du_temps = relationship('EmploiDuTemps', back_populates='professeur', cascade='all, delete')

    def __repr__(self):
        return f"{self.nom} {self.prenom}"


class EmploiDuTemps(Base):
    __tablename__ = 'emploi_du_temps'
    id = Column(Integer, primary_key=True)
    professeur_id = Column(Integer, ForeignKey('professeur.id'), nullable=False)
    jour = Column(String(20), nullable=False)
    heure_debut = Column(String(10), nullable=False)
    heure_fin = Column(String(10), nullable=False)
    nos_classe_id = Column(Integer, ForeignKey('nos_classe.id'), nullable=True)
    matiere = Column(String(100), default='')

    professeur = relationship('Professeur', back_populates='emplois_du_temps')
    nos_classe = relationship('NosClasse')

    def __repr__(self):
        return f"{self.jour} {self.heure_debut}-{self.heure_fin} ({self.matiere})"


class Notification(Base):
    __tablename__ = 'notification'
    id = Column(Integer, primary_key=True)
    titre = Column(String(200))
    message = Column(Text)
    date_creation = Column(DateTime, default=datetime.now)
    lue = Column(Boolean, default=False)
    type_notif = Column(String(50), default='info')  # info, warning, success, error
