"""
Configuração da Conexão com o Banco de Dados (SQLite com SQLAlchemy)
Resolve caminhos absolutos para evitar erros de permissão em containers Docker.
"""
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import get_settings, BASE_DIR

settings = get_settings()

db_url = settings.DATABASE_URL

# Tratamento para garantir caminho absoluto e pasta existente no SQLite
if db_url.startswith("sqlite:///"):
    raw_path = db_url.replace("sqlite:///", "")
    # Se for caminho relativo, baseia-se no BASE_DIR
    if not raw_path.startswith("/") and not (len(raw_path) > 2 and raw_path[1] == ":"):
        db_file = (BASE_DIR / raw_path).resolve()
    else:
        db_file = Path(raw_path).resolve()

    try:
        db_file.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[WARN] Nao foi possivel criar diretorio pai do banco: {e}")

    # Converte de volta para formato URL compativel com Linux/Windows
    db_url = f"sqlite:///{db_file.as_posix()}"

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
    echo=(settings.LOG_LEVEL.upper() == "DEBUG"),
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Gerador de sessão de banco de dados para injeção de dependência."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializa as tabelas do banco de dados se não existirem."""
    import app.database.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
