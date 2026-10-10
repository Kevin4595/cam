import json
import os
from pathlib import Path

from hack import page_for


ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
FIREBASE_CONFIG_KEYS = {
    "apiKey",
    "authDomain",
    "databaseURL",
    "projectId",
    "appId",
    "messagingSenderId",
    "storageBucket",
}


def build_site() -> None:
    raw_config = os.environ.get("FIREBASE_CONFIG", "").strip()
    firebase_config = None
    if raw_config:
        try:
            supplied_config = json.loads(raw_config)
        except json.JSONDecodeError as error:
            raise SystemExit("FIREBASE_CONFIG must contain valid Firebase web-app JSON.") from error
        if not isinstance(supplied_config, dict):
            raise SystemExit("FIREBASE_CONFIG must be a JSON object from Firebase console.")
        firebase_config = {
            key: value
            for key, value in supplied_config.items()
            if key in FIREBASE_CONFIG_KEYS and isinstance(value, str)
        }
        required_keys = {"apiKey", "authDomain", "databaseURL", "projectId", "appId"}
        missing_keys = sorted(required_keys - firebase_config.keys())
        if missing_keys:
            raise SystemExit(
                "FIREBASE_CONFIG is missing required Firebase web-app fields: "
                + ", ".join(missing_keys)
            )

    SITE.mkdir(exist_ok=True)
    (SITE / "index.html").write_text(page_for("viewer"), encoding="utf-8")
    (SITE / "camera.html").write_text(page_for("camera"), encoding="utf-8")
    config_json = json.dumps(firebase_config, separators=(",", ":"), ensure_ascii=True)
    (SITE / "firebase-config.js").write_text(
        f"window.FIREBASE_CONFIG = {config_json};\n",
        encoding="utf-8",
    )
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    print("Built static GitHub Pages website.")


if __name__ == "__main__":
    build_site()
