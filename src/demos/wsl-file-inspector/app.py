from flask import Flask, request, render_template_string
import subprocess
import os
import tempfile
import html

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB limit

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🐧 WSL File Inspector</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: #0d1117; color: #c9d1d9;
      min-height: 100vh; padding: 2rem;
    }
    .container { max-width: 800px; margin: 0 auto; }
    h1 { color: #58a6ff; margin-bottom: 0.5rem; font-size: 2rem; }
    .subtitle { color: #8b949e; margin-bottom: 2rem; }
    .upload-zone {
      border: 2px dashed #30363d; border-radius: 12px;
      padding: 3rem; text-align: center; margin-bottom: 2rem;
      transition: border-color 0.2s;
    }
    .upload-zone:hover { border-color: #58a6ff; }
    input[type="file"] { margin: 1rem 0; }
    button {
      background: #238636; color: white; border: none;
      padding: 0.75rem 2rem; border-radius: 6px; font-size: 1rem;
      cursor: pointer; transition: background 0.2s;
    }
    button:hover { background: #2ea043; }
    .results { margin-top: 2rem; }
    .tool-card {
      background: #161b22; border: 1px solid #30363d;
      border-radius: 8px; margin-bottom: 1rem; overflow: hidden;
    }
    .tool-header {
      background: #21262d; padding: 0.75rem 1rem;
      font-weight: 600; color: #58a6ff;
      display: flex; align-items: center; gap: 0.5rem;
    }
    .tool-output {
      padding: 1rem; font-family: 'Cascadia Code', 'Fira Code', monospace;
      font-size: 0.85rem; white-space: pre-wrap; word-break: break-all;
      max-height: 400px; overflow-y: auto; line-height: 1.5;
    }
    .badge {
      background: #1f6feb; color: white; font-size: 0.7rem;
      padding: 0.15rem 0.5rem; border-radius: 10px;
    }
    .filename { color: #f0883e; font-size: 1.2rem; margin-bottom: 1rem; }
    .footer { text-align: center; margin-top: 3rem; color: #484f58; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🐧 WSL File Inspector</h1>
    <p class="subtitle">Upload any file — Linux tools will reveal its secrets</p>

    <form method="POST" enctype="multipart/form-data" class="upload-zone">
      <p>📁 Drop a file here or click to browse</p>
      <input type="file" name="file" required>
      <br>
      <button type="submit">🔍 Inspect File</button>
    </form>

    {% if results %}
    <div class="results">
      <p class="filename">📄 {{ filename }}</p>
      {% for tool in results %}
      <div class="tool-card">
        <div class="tool-header">
          🔧 {{ tool.name }}
          <span class="badge">{{ tool.desc }}</span>
        </div>
        <div class="tool-output">{{ tool.output }}</div>
      </div>
      {% endfor %}
    </div>
    {% endif %}

    <div class="footer">
      <p>Powered by Linux tools running in Docker on WSL 🐧</p>
      <p style="margin-top:0.5rem">file · exiftool · strings · hexdump · wc · stat</p>
    </div>
  </div>
</body>
</html>
"""


def run_tool(cmd, filepath):
    """Run a shell command and return its output."""
    try:
        full_cmd = cmd.replace("{file}", filepath)
        result = subprocess.run(
            full_cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        output = result.stdout.strip() or result.stderr.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        output = "(timed out)"
    except Exception as e:
        output = f"(error: {e})"
    return html.escape(output)


TOOLS = [
    {"name": "file", "cmd": "file {file}", "desc": "Identify file type"},
    {"name": "stat", "cmd": "stat {file}", "desc": "File metadata & permissions"},
    {"name": "exiftool", "cmd": "exiftool {file}", "desc": "EXIF & embedded metadata"},
    {
        "name": "strings",
        "cmd": "strings {file} | head -40",
        "desc": "Readable text strings",
    },
    {
        "name": "hexdump",
        "cmd": "hexdump -C {file} | head -32",
        "desc": "Raw hex view",
    },
    {
        "name": "wc",
        "cmd": 'wc -c {file} | awk \'{{printf "Size: %s bytes", $1}}\'',
        "desc": "Byte count",
    },
    {
        "name": "sha256sum",
        "cmd": "sha256sum {file}",
        "desc": "SHA-256 checksum",
    },
]


@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    filename = None
    if request.method == "POST":
        f = request.files.get("file")
        if f and f.filename:
            filename = f.filename
            with tempfile.NamedTemporaryFile(delete=False, suffix="_" + filename) as tmp:
                f.save(tmp.name)
                tmp_path = tmp.name

            results = []
            for tool in TOOLS:
                output = run_tool(tool["cmd"], tmp_path)
                results.append(
                    {"name": tool["name"], "desc": tool["desc"], "output": output}
                )

            os.unlink(tmp_path)

    return render_template_string(HTML_TEMPLATE, results=results, filename=filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
