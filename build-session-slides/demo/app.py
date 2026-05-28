
import os
import uuid
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from ascii_magic import AsciiArt

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
UPLOAD_DIR = "/tmp/uploads"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8MB uploads
os.makedirs(UPLOAD_DIR, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/upload")
def upload():
    # Flask file upload pattern: multipart/form-data, request.files dict [1](https://flask.palletsprojects.com/en/stable/patterns/fileuploads/)
    if "file" not in request.files:
        return render_template("index.html", error="No file part in request."), 400

    f = request.files["file"]
    if not f or f.filename == "":
        return render_template("index.html", error="No file selected."), 400

    if not allowed_file(f.filename):
        return render_template(
            "index.html",
            error=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        ), 400

    safe_name = secure_filename(f.filename)
    unique_name = f"{uuid.uuid4().hex}_{safe_name}"
    path = os.path.join(UPLOAD_DIR, unique_name)
    f.save(path)

    # Generate ASCII art
    # ascii-magic quickstart uses AsciiArt.from_image(...) [2](https://pypi.org/project/ascii-magic/)
    cols = int(request.form.get("cols", "120"))
    cols = max(40, min(cols, 240))

    art = AsciiArt.from_image(path)
    ascii_text = art.to_ascii(columns=cols)

    # Clean up uploaded file (optional)
    try:
        os.remove(path)
    except OSError:
        pass

    return render_template("result.html", ascii_text=ascii_text, cols=cols)


if __name__ == "__main__":
    # For local/dev. In container we’ll typically hit gunicorn, but this works too.
    app.run(host="0.0.0.0", port=8080, debug=False)

