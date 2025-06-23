from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def get_current_date():
    """Retorna data atual em UTC."""
    return datetime.now(timezone.utc).astimezone(ZoneInfo("America/Cuiaba")).date()
