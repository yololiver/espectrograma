import os
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    current_app,
    jsonify,
)
from werkzeug.utils import secure_filename

main_bp = Blueprint("main", __name__)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config.get("ALLOWED_EXTENSIONS", {"wav", "mp3"})
    )


@main_bp.route("/", methods=["GET", "POST"])
def upload():
    error = None

    if request.method == "POST":
        file = request.files.get("audio")

        if not file or file.filename == "":
            error = "Nenhum ficheiro selecionado."
        elif not allowed_file(file.filename):
            error = "Formato não suportado. Utilize WAV ou MP3 com menos de 10 MB."
        else:
            filename = secure_filename(file.filename)
            upload_folder = current_app.config["UPLOAD_FOLDER"]
            os.makedirs(upload_folder, exist_ok=True)
            save_path = os.path.join(upload_folder, filename)
            file.save(save_path)

            size_bytes = os.path.getsize(save_path)
            size_mb = round(size_bytes / (1024 * 1024), 1)

            session["filename"] = filename
            session["size_mb"] = size_mb

            return redirect(url_for("main.analysis"))

    return render_template("upload.html", error=error)


@main_bp.route("/analise")
def analysis():
    filename = session.get("filename")
    if not filename:
        return redirect(url_for("main.upload"))

    return render_template(
        "analysis_current.html",
        filename=filename,
    )


@main_bp.route("/feedback")
def feedback():
    filename = session.get("filename")
    if not filename:
        return redirect(url_for("main.upload"))

    return render_template(
        "feedback_current.html",
        filename=filename,
    )


@main_bp.route("/reset")
def reset():
    filename = session.get("filename")
    if filename:
        file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass

    session.clear()
    return redirect(url_for("main.upload"))


@main_bp.route("/api/status")
def status():
    return jsonify({"status": "ok", "message": "Flask backend is running"})
