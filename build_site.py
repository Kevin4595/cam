import os
from pathlib import Path
from urllib.parse import urlsplit

from hack import page_for


ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
signaling_origin = os.environ.get("SIGNALING_ORIGIN", "").rstrip("/")
parsed_origin = urlsplit(signaling_origin)

if (
    parsed_origin.scheme != "https"
    or not parsed_origin.netloc
    or parsed_origin.path not in ("", "/")
    or parsed_origin.query
    or parsed_origin.fragment
    or parsed_origin.username
    or parsed_origin.password
):
    raise SystemExit(
        "Set SIGNALING_ORIGIN to the HTTPS origin of the VPS, "
        "for example https://api.example.com"
    )

SITE.mkdir(exist_ok=True)
(SITE / "index.html").write_text(page_for("viewer"), encoding="utf-8")
(SITE / "camera.html").write_text(page_for("camera"), encoding="utf-8")
(SITE / "_redirects").write_text(
    f"/api/* {signaling_origin}/api/:splat 200!\n"
    "/camera /camera.html 200\n"
    "/* /index.html 200\n",
    encoding="utf-8",
)
print(f"Built Netlify site with signaling proxy to {signaling_origin}")
