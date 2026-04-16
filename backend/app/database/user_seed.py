# este modulo cria linhas minimas na tabela user profiles sem passar pelo router http
# e usado no arranque do seed e pelos endpoints de perfil quando falta uma linha
# mantemos tres ids fixos para demo e permitimos criar mais ids se o cabecalho pedir
from sqlalchemy.orm import Session

from backend.app.database import models as M

# tupla imutavel com os ids que o frontend lista no selector de utilizador
DEFAULT_PROFILE_IDS = (1, 2, 3)

# dicionario com texto inicial para cada id demo
# chave e o id inteiro
# valor e um dicionario com colunas do modelo user profile
_DEFAULT_ROWS = {
    1: dict(
        display_name="ana silva",
        email="ana.silva@exemplo.edu",
        organization="laboratorio de engenharia demo",
        role="researcher",
        bio=None,
        preferred_language="pt",
    ),
    2: dict(
        display_name="bruno costa",
        email="bruno.costa@exemplo.edu",
        organization="grupo de reatores demo",
        role="engineer",
        bio=None,
        preferred_language="pt",
    ),
    3: dict(
        display_name="carla mendes",
        email="carla.mendes@exemplo.edu",
        organization="mestrado em engenharia quimica demo",
        role="student",
        bio=None,
        preferred_language="pt",
    ),
}


def _ensure_one_profile(db: Session, user_id: int) -> M.UserProfile:
    # funcao interna que garante uma linha para um id concreto
    # db e a sessao sqlalchemy aberta pelo chamador
    # user_id e a chave primaria desejada
    # passo um procuramos se ja existe
    row = db.query(M.UserProfile).filter(M.UserProfile.id == user_id).first()
    if row:
        return row
    # passo dois escolhemos dados default
    # se o id estiver em default rows usamos texto rico
    # senao criamos texto generico com o numero no nome
    base = _DEFAULT_ROWS.get(
        user_id,
        dict(
            display_name=f"utilizador {user_id}",
            email=f"user{user_id}@local",
            organization="local",
            role="researcher",
            bio=None,
            preferred_language="pt",
        ),
    )
    # passo tres instanciamos o modelo e gravamos
    row = M.UserProfile(id=user_id, **base)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def ensure_default_profiles(db: Session) -> None:
    # percorre apenas os tres ids demo
    # util para o seed e para list users saber que a tabela tem linhas base
    for uid in DEFAULT_PROFILE_IDS:
        _ensure_one_profile(db, uid)


def ensure_profile_by_id(db: Session, user_id: int) -> M.UserProfile:
    # primeiro garantimos os tres perfis demo
    # depois garantimos o id pedido pelo cabecalho atual
    # se o id for novo criamos linha generica
    ensure_default_profiles(db)
    row = db.query(M.UserProfile).filter(M.UserProfile.id == user_id).first()
    if row:
        return row
    return _ensure_one_profile(db, user_id)
