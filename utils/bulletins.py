from database.models import Bulletin, Note, MatiereClasse, Periode, Eleve, NosClasse
from sqlalchemy import func


def generer_bulletin_eleve(eleve_id, session):
    eleve = session.get(Eleve, eleve_id)
    if not eleve or not eleve.nos_classe:
        return

    periodes = session.query(Periode).filter_by(
        niveau_id=eleve.nos_classe.classe.niveau_id if eleve.nos_classe.classe else None
    ).all()

    for periode in periodes:
        notes = session.query(Note).filter_by(
            eleve_id=eleve_id,
            periode_id=periode.id
        ).all()
        if not notes:
            continue

        total_points = 0
        total_coef = 0
        for note in notes:
            mc = session.get(MatiereClasse, note.matiere_classe_id)
            coef = mc.coefficient if mc else 1
            total_points += note.valeur * coef
            total_coef += coef

        moyenne = round(total_points / total_coef, 2) if total_coef > 0 else 0

        if moyenne >= 16:
            appreciation = "Très bien"
        elif moyenne >= 14:
            appreciation = "Bien"
        elif moyenne >= 12:
            appreciation = "Assez bien"
        elif moyenne >= 10:
            appreciation = "Passable"
        else:
            appreciation = "Insuffisant"

        existing = session.query(Bulletin).filter_by(
            eleve_id=eleve_id, periode_id=periode.id
        ).first()

        if existing:
            existing.moyenne = moyenne
            existing.appreciation = appreciation
        else:
            session.add(Bulletin(
                eleve_id=eleve_id,
                periode_id=periode.id,
                moyenne=moyenne,
                appreciation=appreciation
            ))

    session.commit()
    _calculer_rangs(session, eleve, periodes)


def _calculer_rangs(session, eleve, periodes):
    if not eleve.nos_classe:
        return
    for periode in periodes:
        eleves_classe = session.query(Eleve).filter_by(
            nos_classe_id=eleve.nos_classe_id
        ).all()
        bulletins = []
        for e in eleves_classe:
            b = session.query(Bulletin).filter_by(eleve_id=e.id, periode_id=periode.id).first()
            if b and b.moyenne is not None:
                bulletins.append((e.id, b.moyenne, b))

        bulletins.sort(key=lambda x: x[1], reverse=True)
        for rang, (_, _, b) in enumerate(bulletins, 1):
            b.rang = rang
    session.commit()


def generer_bulletins_classe(nos_classe_id, session):
    eleves = session.query(Eleve).filter_by(nos_classe_id=nos_classe_id).all()
    for eleve in eleves:
        generer_bulletin_eleve(eleve.id, session)
