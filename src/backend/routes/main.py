import os
import json

from flask import (
    Blueprint,
    make_response,
    render_template,
    request,
    redirect,
    url_for,
    session,
    current_app,
    jsonify,
    send_file,
)
from werkzeug.utils import secure_filename

from backend.services import (
    process_audio_file,
    build_analysis_summary,
    generate_feedback,
)

main_bp = Blueprint("main", __name__)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config.get("ALLOWED_EXTENSIONS", {"wav", "mp3"})
    )


def _get_uploaded_file_path():
    filename = session.get("filename")
    if not filename:
        return None, None
    file_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(file_path):
        return filename, None
    return filename, file_path


@main_bp.route("/", methods=["GET", "POST"])
def upload():
    error = None

    if request.method == "POST":
        file = request.files.get("audio")
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

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
            session.pop("analysis_summary", None)

            if is_ajax:
                return jsonify({"status": "ok", "redirect": url_for("main.analysis")})
            return redirect(url_for("main.analysis"))

        if is_ajax:
            return jsonify({"status": "error", "message": error}), 400

    return render_template("upload.html", error=error)


@main_bp.route("/analise")
def analysis():
    filename, file_path = _get_uploaded_file_path()
    if not filename:
        return redirect(url_for("main.upload"))
    if not file_path:
        return redirect(url_for("main.upload"))

    spec_data = process_audio_file(file_path)
    if not spec_data:
        return render_template(
            "analysis_current.html",
            filename=filename,
        )

    summary = build_analysis_summary(spec_data)
    session["analysis_summary"] = summary

    events = spec_data.get("events", [])
    silence_events = [ev for ev in events if ev.get("type") == "silence"]
    clipping_events = [ev for ev in events if ev.get("type") == "clip"]
    other_events = [ev for ev in events if ev.get("type") not in {"silence", "clip"}]
    has_clipping = bool(clipping_events)
    background_noise = spec_data.get("background_noise", "desconhecido")
    event_types_present = {ev.get("type") for ev in events}

    return render_template(
        "analysis.html",
        filename=filename,
        duration=f"{spec_data['duration']:.1f} s",
        sample_rate=f"{spec_data['sample_rate']} Hz",
        channels="mono",
        spec_data=json.dumps(spec_data["spec"]),
        spec_duration=spec_data["duration"],
        spec_sr=spec_data["sample_rate"],
        annotations=spec_data.get("annotations", []),
        silence_events=silence_events,
        clipping_events=clipping_events,
        other_events=other_events,
        has_clipping=has_clipping,
        background_noise=background_noise,
        event_types_present=event_types_present,
    )


@main_bp.route("/analise/3d")
def analysis_3d():
    filename, file_path = _get_uploaded_file_path()
    if not filename:
        return redirect(url_for("main.upload"))
    if not file_path:
        return redirect(url_for("main.upload"))

    spec_data = process_audio_file(file_path)
    if not spec_data:
        return redirect(url_for("main.analysis"))

    return render_template(
        "analysis_3d.html",
        filename=filename,
        spec_data=json.dumps(spec_data["spec"]),
        spec_duration=spec_data["duration"],
        spec_sr=spec_data["sample_rate"],
    )


@main_bp.route("/feedback")
def feedback():
    filename, file_path = _get_uploaded_file_path()
    if not filename:
        return redirect(url_for("main.upload"))
    if not file_path:
        return redirect(url_for("main.upload"))

    summary = session.get("analysis_summary")
    if not summary:
        spec_data = process_audio_file(file_path)
        if not spec_data:
            return redirect(url_for("main.analysis"))
        summary = build_analysis_summary(spec_data)
        session["analysis_summary"] = summary

    feedback_data = generate_feedback(summary)
    size_mb = session.get("size_mb", "—")

    html = render_template(
        "feedback.html",
        filename=filename,
        size_mb=size_mb,
        noise_level=feedback_data["noise_level"],
        noise_pill_class=feedback_data["noise_pill_class"],
        feedback_items=feedback_data["feedback_items"],
        stats=feedback_data["stats"],
        highlights=feedback_data["highlights"],
        verdict=feedback_data["verdict"],
    )
    response = make_response(html)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response


@main_bp.route("/audio")
def audio():
    filename, file_path = _get_uploaded_file_path()
    if not file_path:
        return "", 404
    return send_file(file_path)


def _load_demo_spec():
    demo_json = os.path.join(
        os.path.dirname(current_app.root_path), "backend", "static", "demo", "demo_result.json"
    )
    if not os.path.exists(demo_json):
        return None
    with open(demo_json, encoding="utf-8") as f:
        return json.load(f)


@main_bp.route("/demo")
def demo():
    spec_data = _load_demo_spec()
    if not spec_data:
        return "Ficheiro de demo não encontrado. Corre scripts/generate_demo.py primeiro.", 404

    events = spec_data.get("events", [])
    silence_events = [ev for ev in events if ev.get("type") == "silence"]
    clipping_events = [ev for ev in events if ev.get("type") == "clip"]
    other_events = [ev for ev in events if ev.get("type") not in {"silence", "clip"}]

    return render_template(
        "analysis.html",
        filename="demo — soundreality-intro-noise.mp3",
        duration=f"{spec_data['duration']:.1f} s",
        sample_rate=f"{spec_data['sample_rate']} Hz",
        channels="mono",
        spec_data=json.dumps(spec_data["spec"]),
        spec_duration=spec_data["duration"],
        spec_sr=spec_data["sample_rate"],
        annotations=spec_data.get("annotations", []),
        silence_events=silence_events,
        clipping_events=clipping_events,
        other_events=other_events,
        has_clipping=bool(clipping_events),
        background_noise=spec_data.get("background_noise", "desconhecido"),
        event_types_present={ev.get("type") for ev in events},
        audio_url=url_for("main.demo_audio"),
        url_3d=url_for("main.demo_3d"),
        url_feedback=url_for("main.demo_feedback"),
        url_reset=url_for("main.upload"),
    )


@main_bp.route("/demo/3d")
def demo_3d():
    spec_data = _load_demo_spec()
    if not spec_data:
        return redirect(url_for("main.demo"))

    return render_template(
        "analysis_3d.html",
        filename="demo — soundreality-intro-noise.mp3",
        spec_data=json.dumps(spec_data["spec"]),
        spec_duration=spec_data["duration"],
        spec_sr=spec_data["sample_rate"],
    )


@main_bp.route("/demo/feedback")
def demo_feedback():
    spec_data = _load_demo_spec()
    if not spec_data:
        return redirect(url_for("main.demo"))

    summary = build_analysis_summary(spec_data)
    feedback_data = generate_feedback(summary)

    html = render_template(
        "feedback.html",
        filename="demo — soundreality-intro-noise.mp3",
        size_mb="0.1",
        noise_level=feedback_data["noise_level"],
        noise_pill_class=feedback_data["noise_pill_class"],
        feedback_items=feedback_data["feedback_items"],
        stats=feedback_data["stats"],
        highlights=feedback_data["highlights"],
        verdict=feedback_data["verdict"],
        url_analysis=url_for("main.demo"),
        url_reset=url_for("main.upload"),
    )
    response = make_response(html)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return response


@main_bp.route("/demo/audio")
def demo_audio():
    audio_path = os.path.join(
        os.path.dirname(current_app.root_path), "backend", "static", "demo", "demo_audio.mp3"
    )
    if not os.path.exists(audio_path):
        return "", 404
    return send_file(audio_path)


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


@main_bp.route("/test-simple")
def test_simple():
    return jsonify({"message": "Test route working", "timestamp": "test"})


@main_bp.route("/test-analysis")
def test_analysis():
    """Rota de teste para visualização do espectrograma."""
    try:
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        audio_file = os.path.join(upload_folder, "file_example_MP3_700KB.mp3")
        if not os.path.exists(audio_file):
            return jsonify({"error": "Ficheiro não encontrado"}), 404

        spec_data = process_audio_file(audio_file)
        if not spec_data:
            return jsonify({"error": "Erro ao processar áudio"}), 500

        events = spec_data.get("events", [])
        silence_events = [ev for ev in events if ev.get("type") == "silence"]
        clipping_events = [ev for ev in events if ev.get("type") == "clip"]
        other_events = [ev for ev in events if ev.get("type") not in {"silence", "clip"}]
        has_clipping = bool(clipping_events)
        event_types_present = {ev.get("type") for ev in events}

        return render_template(
            "analysis.html",
            filename="file_example_MP3_700KB.mp3",
            duration=f"{spec_data['duration']:.1f} s",
            sample_rate=f"{spec_data['sample_rate']} Hz",
            channels="mono",
            spec_data=json.dumps(spec_data["spec"]),
            spec_duration=spec_data["duration"],
            spec_sr=spec_data["sample_rate"],
            annotations=spec_data.get("annotations", []),
            silence_events=silence_events,
            clipping_events=clipping_events,
            other_events=other_events,
            has_clipping=has_clipping,
            background_noise=spec_data.get("background_noise", "desconhecido"),
            event_types_present=event_types_present,
        )
    except Exception as e:
        import traceback

        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500
