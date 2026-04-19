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


@main_bp.route("/test-simple")
def test_simple():
    return jsonify({"message": "Test route working", "timestamp": "test"})


def process_audio_file(file_path):
    """Processa ficheiro de áudio e retorna dados de espectrograma."""
    if not librosa:
        print("Librosa não está instalado")
        return None
    
    try:
        print(f"Carregando áudio de: {file_path}")
        # Carrega o áudio
        y, sr = librosa.load(file_path, sr=None)
        print(f"Áudio carregado: {len(y)} samples, {sr} Hz")
        
        # Gera o espectrograma (STFT)
        D = librosa.stft(y)
        S_db = librosa.power_to_db(np.abs(D) ** 2, ref=np.max)
        
        # Normaliza para 0-255
        S_norm = ((S_db - S_db.min()) / (S_db.max() - S_db.min()) * 255).astype(np.uint8)
        
        # Redimensiona para tamanho manejável se necessário
        if S_norm.shape[0] > 128:
            S_norm = S_norm[::S_norm.shape[0]//128, :]
        
        print(f"Espectrograma gerado: {S_norm.shape}")
        return {
            "spec": S_norm.tolist(),
            "duration": len(y) / sr,
            "sample_rate": sr,
            "n_fft": 2048,
            "hop_length": 512,
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
