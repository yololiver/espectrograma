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
        "analysis.html",
        filename=filename,
        size_mb=session.get("size_mb", "?"),
        duration="42 s",
        sample_rate="44 100 Hz",
        channels="mono",
        events=[
            {"type": "silence", "badge": "silêncio", "desc": "pausa longa", "time": "0:04–0:09", "color": "#378ADD"},
            {"type": "clip",    "badge": "clipping",  "desc": "pico de distorção", "time": "0:14–0:16", "color": "#E24B4A"},
            {"type": "event",   "badge": "evento",    "desc": "variação de energia",   "time": "0:22–0:24", "color": "#EF9F27"},
            {"type": "silence", "badge": "silêncio",  "desc": "pausa longa",           "time": "0:32–0:38", "color": "#378ADD"},
        ],
        annotations=[
            {"left": "9%",  "width": "11%", "color": "#378ADD"},
            {"left": "34%", "width": "3%",  "color": "#E24B4A"},
            {"left": "52%", "width": "4%",  "color": "#EF9F27"},
            {"left": "76%", "width": "10%", "color": "#378ADD"},
        ],
    )


@main_bp.route("/feedback")
def feedback():
    filename = session.get("filename")
    if not filename:
        return redirect(url_for("main.upload"))

    return render_template(
        "feedback.html",
        filename=filename,
        size_mb=session.get("size_mb", "?"),
        noise_level="nível moderado",
        feedback_items=[
            {"color": "#378ADD", "text": "O áudio tem duas pausas longas, aos 4 e aos 32 segundos. Podem ser momentos de hesitação ou troca de interlocutor."},
            {"color": "#E24B4A", "text": "Existe um pico de distorção aos 14 segundos. O som ficou saturado, provavelmente por o microfone estar demasiado perto."},
            {"color": "#EF9F27", "text": "Detectou-se uma variação súbita de volume aos 22 segundos — pode ser uma batida ou mudança abrupta de voz."},
            {"color": "#888780", "text": "O ruído de fundo é moderado ao longo de toda a gravação. Pode ser filtrado com ferramentas de redução de ruído."},
        ],
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
