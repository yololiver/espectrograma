import os
import json
import base64
import numpy as np
from io import BytesIO
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

try:
    import librosa
except ImportError:
    librosa = None

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

            if is_ajax:
                return jsonify({"status": "ok", "redirect": url_for("main.analysis")})
            return redirect(url_for("main.analysis"))

        if is_ajax:
            return jsonify({"status": "error", "message": error}), 400

    return render_template("upload.html", error=error)


@main_bp.route("/analise")
def analysis():
    filename = session.get("filename")
    if not filename:
        return redirect(url_for("main.upload"))

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    file_path = os.path.join(upload_folder, filename)
    if not os.path.exists(file_path):
        return redirect(url_for("main.upload"))

    spec_data = process_audio_file(file_path)
    if not spec_data:
        return render_template(
            "analysis_current.html",
            filename=filename,
        )

    return render_template(
        "analysis.html",
        filename=filename,
        duration=f"{spec_data['duration']:.1f} s",
        sample_rate=f"{spec_data['sample_rate']} Hz",
        channels="stereo",
        spec_data=json.dumps(spec_data["spec"]),
        spec_duration=spec_data["duration"],
        spec_sr=spec_data["sample_rate"],
        annotations=spec_data.get("annotations", []),
        events=spec_data.get("events", []),
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


@main_bp.route("/test-simple")
def test_simple():
    return jsonify({"message": "Test route working", "timestamp": "test"})


def process_audio_file(file_path):
    """Processa ficheiro de áudio e retorna dados de espectrograma e silêncio."""
    if not librosa:
        print("Librosa não está instalado")
        return None
    
    try:
        print(f"Carregando áudio de: {file_path}")
        # Carrega o áudio em mono para detecção consistente
        y, sr = librosa.load(file_path, sr=None, mono=True)
        print(f"Áudio carregado: {len(y)} samples, {sr} Hz")

        duration = len(y) / sr
        frame_length = 2048
        hop_length = 512
        top_db = 40

        # Detecta segmentos não silenciosos e extrai silêncios
        nonsilent = librosa.effects.split(
            y,
            top_db=top_db,
            frame_length=frame_length,
            hop_length=hop_length,
        )

        silence_segments = []
        last_end = 0
        for start_frame, end_frame in nonsilent:
            start = last_end / sr
            end = start_frame / sr
            if end - start >= 0.12:
                silence_segments.append({
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "duration": round(end - start, 2),
                })
            last_end = end_frame

        if last_end < len(y):
            start = last_end / sr
            end = duration
            if end - start >= 0.12:
                silence_segments.append({
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "duration": round(end - start, 2),
                })

        # Gera o espectrograma (STFT)
        D = librosa.stft(y, n_fft=2048, hop_length=hop_length)
        S_db = librosa.power_to_db(np.abs(D) ** 2, ref=np.max)

        # Normaliza para 0-255
        S_norm = ((S_db - S_db.min()) / (S_db.max() - S_db.min()) * 255).astype(np.uint8)

        # Redimensiona para tamanho manejável se necessário
        if S_norm.shape[0] > 128:
            S_norm = S_norm[::S_norm.shape[0]//128, :]

        silence_events = []
        silence_annotations = []
        for segment in silence_segments:
            start = segment["start"]
            end = segment["end"]
            left = (start / duration) * 100 if duration > 0 else 0
            width = ((end - start) / duration) * 100 if duration > 0 else 0
            silence_events.append({
                "type": "silence",
                "badge": "silêncio",
                "desc": "Segmento de silêncio detectado",
                "time": f"{start:.2f}s – {end:.2f}s",
            })
            silence_annotations.append({
                "left": f"{left:.2f}%",
                "width": f"{width:.2f}%",
                "color": "rgba(0, 100, 200, 0.25)",
            })

        print(f"Espectrograma gerado: {S_norm.shape}")
        return {
            "spec": S_norm.tolist(),
            "duration": duration,
            "sample_rate": sr,
            "n_fft": 2048,
            "hop_length": hop_length,
            "silence_segments": silence_segments,
            "events": silence_events,
            "annotations": silence_annotations,
        }
    except Exception as e:
        print(f"Erro ao processar áudio: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


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
        
        return render_template(
            "analysis.html",
            filename="file_example_MP3_700KB.mp3",
            duration=f"{spec_data['duration']:.1f} s",
            sample_rate=f"{spec_data['sample_rate']} Hz",
            channels="stereo",
            spec_data=json.dumps(spec_data["spec"]),
            spec_duration=spec_data['duration'],
            spec_sr=spec_data['sample_rate'],
        )
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500
