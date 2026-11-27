import sys
from datetime import UTC, datetime, timedelta

import jwt

from config.settings import get_settings

USERS = {
    "astana": {"sub": "user-astana", "org_id": 1, "org_type": "company"},
    "distributor-a": {"sub": "user-dist-a", "org_id": 2, "org_type": "distributor"},
    "distributor-b": {"sub": "user-dist-b", "org_id": 3, "org_type": "distributor"},
}

TOKEN_LIFETIME = timedelta(days=7)


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in USERS:
        names = ", ".join(USERS)
        raise SystemExit(f"Usage: python -m scripts.issue_token <{names}>")
    payload = {**USERS[sys.argv[1]], "exp": datetime.now(UTC) + TOKEN_LIFETIME}
    print(jwt.encode(payload, get_settings().JWT_SECRET, algorithm="HS256"))


if __name__ == "__main__":
    main()
