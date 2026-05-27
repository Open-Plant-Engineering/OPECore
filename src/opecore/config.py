import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env automatically
load_dotenv()


@dataclass(frozen=True)
class Config:
    env: str
    debug: bool

    db_path: str

    cache_size: int
    sync_on_write: bool

    log_level: str


def _get_bool(key: str, default: str = "false") -> bool:
    return os.getenv(key, default).lower() in ("1", "true", "yes")


def load_config() -> Config:
    return Config(
        env=os.getenv("OPECORE_ENV", "development"),
        debug=_get_bool("OPECORE_DEBUG", "true"),

        db_path=os.getenv("OPECORE_DB_PATH", "./data/mydb.dat"),

        cache_size=int(os.getenv("OPECORE_CACHE_SIZE", "10000")),
        sync_on_write=_get_bool("OPECORE_SYNC_ON_WRITE", "true"),

        log_level=os.getenv("OPECORE_LOG_LEVEL", "INFO"),
    )


# Singleton config
config = load_config()
