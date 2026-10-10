from pathlib import Path

from hack import page_for


ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"

SITE.mkdir(exist_ok=True)
(SITE / "index.html").write_text(page_for("viewer"), encoding="utf-8")
(SITE / "camera.html").write_text(page_for("camera"), encoding="utf-8")
(SITE / ".nojekyll").write_text("", encoding="utf-8")
print("Built static GitHub Pages website.")
