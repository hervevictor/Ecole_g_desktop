from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from database.models import Base, generer_matricule
import os
from utils.paths import get_app_dir

DB_PATH = os.path.join(get_app_dir(), 'g_ecole.db')
ENGINE = create_engine(f'sqlite:///{DB_PATH}', echo=False)
Session = sessionmaker(bind=ENGINE)

_session = None


def get_session():
    global _session
    if _session is None:
        _session = Session()
    return _session


def init_db():
    Base.metadata.create_all(ENGINE)
    _migrate_db()
    _seed_config()


def _migrate_db():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(utilisateur)")
    existing = {row[1] for row in cursor.fetchall()}
    new_cols = [
        ("telephone",  "VARCHAR(20) DEFAULT ''"),
        ("photo_path", "VARCHAR(500) DEFAULT ''"),
    ]
    for col, defn in new_cols:
        if col not in existing:
            cursor.execute(f"ALTER TABLE utilisateur ADD COLUMN {col} {defn}")
    conn.commit()
    conn.close()


def _seed_config():
    session = get_session()
    from database.models import ConfigurationEtablissement, Utilisateur
    if not session.query(ConfigurationEtablissement).first():
        session.add(ConfigurationEtablissement(
            nom_etablissement='Mon École',
            devise='Excellence et Discipline',
        ))
        session.commit()
    # Créer l'admin par défaut s'il n'existe pas
    if not session.query(Utilisateur).filter_by(username='admin').first():
        admin = Utilisateur(
            username='admin',
            role='admin',
            nom='Administrateur',
            prenom='',
            is_active=True,
        )
        admin.set_password('admin123')
        session.add(admin)
        session.commit()
