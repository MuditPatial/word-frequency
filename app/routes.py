"""
Flask Routes — REST API endpoints
"""

import os
import json
import csv
import io
import re

from flask import (
    Blueprint, request, jsonify, render_template,
    send_file, current_app, abort
)
from werkzeug.utils import secure_filename

from app.analyzer import WordFrequencyAnalyzer
from app.extractor import extract_text
from app.utils import clean_text

main = Blueprint("main", __name__)


def allowed_file(filename: str) -> bool:
    allowed = current_app.config["ALLOWED_EXTENSIONS"]
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


# ── In-memory last result (per-process; fine for single-user dev/demo) ──
_last_result: dict = {}
_last_text: str = ""


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Accepts either:
      - multipart/form-data  with field 'file' (PDF / DOCX / TXT)
      - JSON  { "text": "...", "top_n": 50, "remove_stopwords": true }
    """
    global _last_result, _last_text

    remove_sw = True
    top_n = 50
    text = ""

    # ── file upload path ──
    if "file" in request.files:
        f = request.files["file"]
        if f.filename == "":
            return jsonify({"error": "No file selected."}), 400
        if not allowed_file(f.filename):
            return jsonify({"error": "Unsupported file type. Use PDF, DOCX, or TXT."}), 400

        filename = secure_filename(f.filename)
        upload_dir = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)
        f.save(filepath)

        try:
            text = extract_text(filepath)
        except Exception as e:
            return jsonify({"error": f"Could not read file: {str(e)}"}), 422
        finally:
            # clean up uploaded file after extraction
            try:
                os.remove(filepath)
            except OSError:
                pass

        remove_sw = request.form.get("remove_stopwords", "true").lower() == "true"
        top_n = int(request.form.get("top_n", 50))

    # ── raw text / JSON path ──
    else:
        data = request.get_json(silent=True) or {}
        text = data.get("text", "")
        remove_sw = data.get("remove_stopwords", True)
        top_n = int(data.get("top_n", 50))

    if not text.strip():
        return jsonify({"error": "No text content found."}), 400

    text = clean_text(text)
    _last_text = text

    analyzer = WordFrequencyAnalyzer(remove_stopwords=remove_sw)
    result = analyzer.analyze(text, top_n=top_n)
    _last_result = result

    return jsonify(result)


@main.route("/api/search", methods=["POST"])
def search_word():
    """
    Search for a specific word in the last analysed text.
    Returns count, percentage, context snippets.
    """
    global _last_result, _last_text

    data = request.get_json(silent=True) or {}
    word = data.get("word", "").strip().lower()

    if not word:
        return jsonify({"error": "No search word provided."}), 400
    if not _last_text:
        return jsonify({"error": "No document analysed yet. Upload a file first."}), 400

    # exact count in raw (unfiltered) text
    pattern = re.compile(r"\b" + re.escape(word) + r"\b", re.IGNORECASE)
    matches = list(pattern.finditer(_last_text))
    count = len(matches)

    # frequency from analyzer result
    word_counts = _last_result.get("word_counts", {})
    filtered_count = _last_result.get("filtered_words", 0) or 1
    freq_count = word_counts.get(word, 0)
    percentage = round(freq_count / filtered_count * 100, 3)

    # extract up to 10 context snippets (±80 chars around each match)
    snippets = []
    for m in matches[:10]:
        start = max(0, m.start() - 80)
        end = min(len(_last_text), m.end() + 80)
        snippet = _last_text[start:end].replace("\n", " ").strip()
        # wrap the matched word in a marker for highlighting
        highlighted = re.sub(
            r"\b" + re.escape(word) + r"\b",
            f"<mark>{word}</mark>",
            snippet,
            flags=re.IGNORECASE,
        )
        snippets.append(highlighted)

    return jsonify({
        "word": word,
        "count": count,
        "percentage": percentage,
        "snippets": snippets,
        "in_top_words": word in word_counts,
    })


@main.route("/api/export/<fmt>", methods=["GET"])
def export(fmt: str):
    """Export last results as CSV or JSON."""
    global _last_result

    if not _last_result:
        return jsonify({"error": "Nothing to export yet."}), 400

    top_words = _last_result.get("top_words", [])

    if fmt == "json":
        buf = io.BytesIO(json.dumps(top_words, indent=2).encode())
        buf.seek(0)
        return send_file(buf, mimetype="application/json",
                         as_attachment=True, download_name="word_frequency.json")

    elif fmt == "csv":
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["word", "count", "percentage"])
        writer.writeheader()
        writer.writerows(top_words)
        buf = io.BytesIO(output.getvalue().encode())
        buf.seek(0)
        return send_file(buf, mimetype="text/csv",
                         as_attachment=True, download_name="word_frequency.csv")

    else:
        abort(404)


@main.route("/api/samples")
def samples():
    sample_dir = os.path.join(current_app.root_path, "..", "static", "assets", "samples")
    sample_dir = os.path.normpath(sample_dir)
    files = []
    if os.path.isdir(sample_dir):
        for name in sorted(os.listdir(sample_dir)):
            if name.endswith(".txt"):
                files.append({"name": name.replace("_", " ").replace(".txt", "").title(), "file": name})
    return jsonify(files)


@main.route("/api/sample/<filename>")
def load_sample(filename: str):
    sample_dir = os.path.join(current_app.root_path, "..", "static", "assets", "samples")
    sample_dir = os.path.normpath(sample_dir)
    safe = secure_filename(filename)
    path = os.path.join(sample_dir, safe)
    if not os.path.isfile(path):
        return jsonify({"error": "Sample not found."}), 404
    with open(path, encoding="utf-8") as fh:
        return jsonify({"text": fh.read()})
