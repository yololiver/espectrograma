"""Processamento de áudio e geração de espectrograma com deteção de eventos."""

import numpy as np

try:
    import librosa
except ImportError:
    librosa = None


def normalize_spectrogram_db(S_db):
    """
    Normaliza matriz dB para 0–255.
    Se todos os valores forem iguais (áudio silencioso ou conteúdo uniforme),
    devolve matriz uniforme em vez de dividir por zero.
    """
    S_db = np.nan_to_num(S_db, nan=0.0, neginf=0.0, posinf=0.0)
    s_min = float(S_db.min())
    s_max = float(S_db.max())
    span = s_max - s_min
    if span < 1e-10:
        return np.zeros(S_db.shape, dtype=np.uint8)
    return ((S_db - s_min) / span * 255).astype(np.uint8)


def process_audio_file(file_path):
    """Processa ficheiro de áudio e retorna dados de espectrograma e eventos."""
    if not librosa:
        print("Librosa não está instalado")
        return None

    try:
        y, sr = librosa.load(file_path, sr=None, mono=True)
        duration = len(y) / sr
        frame_length = 2048
        hop_length = 256
        top_db = 40

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

        clip_threshold = 0.9
        clipping_mask = np.abs(y) >= clip_threshold
        clipping_segments = []
        if clipping_mask.any():
            clip_changes = np.flatnonzero(
                np.diff(clipping_mask.astype(int), prepend=0, append=0)
            )
            for i in range(0, len(clip_changes), 2):
                start_sample = clip_changes[i]
                end_sample = clip_changes[i + 1]
                start = start_sample / sr
                end = end_sample / sr
                if end - start >= 0.0001:
                    clipping_segments.append({
                        "start": round(start, 2),
                        "end": round(end, 2),
                        "duration": round(end - start, 2),
                    })

        merged_clipping_segments = []
        if clipping_segments:
            clipping_segments.sort(key=lambda x: x["start"])
            current = clipping_segments[0]
            for next_seg in clipping_segments[1:]:
                if current["end"] + 0.05 >= next_seg["start"]:
                    current["end"] = max(current["end"], next_seg["end"])
                    current["duration"] = round(current["end"] - current["start"], 2)
                else:
                    merged_clipping_segments.append(current)
                    current = next_seg
            merged_clipping_segments.append(current)
        clipping_segments = merged_clipping_segments

        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_length)[0]
        noise_floor = np.percentile(rms, 10) if len(rms) else 0.0
        peak_energy = np.max(rms) if len(rms) else 1e-9
        noise_ratio = noise_floor / max(peak_energy, 1e-9)
        if noise_ratio < 0.015:
            background_noise = "baixo"
        elif noise_ratio < 0.05:
            background_noise = "moderado"
        else:
            background_noise = "alto"

        energy_segments = []
        for i in range(1, len(rms)):
            if rms[i] > 2 * rms[i - 1] and rms[i] > 0.05:
                start = (i * hop_length) / sr
                end = min((i + 1) * hop_length / sr, duration)
                if end - start >= 0.01:
                    energy_segments.append({
                        "start": round(start, 2),
                        "end": round(end, 2),
                        "duration": round(end - start, 2),
                    })

        centroid = librosa.feature.spectral_centroid(
            y=y, sr=sr, n_fft=4096, hop_length=hop_length
        )[0]
        spectral_segments = []
        for i in range(1, len(centroid)):
            if abs(centroid[i] - centroid[i - 1]) > 1500:
                start = (i * hop_length) / sr
                end = min((i + 1) * hop_length / sr, duration)
                if end - start >= 0.01:
                    spectral_segments.append({
                        "start": round(start, 2),
                        "end": round(end, 2),
                        "duration": round(end - start, 2),
                    })

        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_length)
        transient_segments = []
        for frame in onset_frames:
            start = (frame * hop_length) / sr
            end = min(start + 0.1, duration)
            transient_segments.append({
                "start": round(start, 2),
                "end": round(end, 2),
                "duration": round(end - start, 2),
            })

        D = librosa.stft(y, n_fft=4096, hop_length=hop_length)
        power = np.abs(D) ** 2
        ref = float(np.max(power))
        if ref < 1e-12:
            S_db = np.zeros(power.shape, dtype=np.float32)
        else:
            S_db = librosa.power_to_db(power, ref=ref)
        S_norm = normalize_spectrogram_db(S_db)

        if S_norm.shape[0] > 512:
            S_norm = S_norm[:: S_norm.shape[0] // 512, :]

        def _build_events_and_annotations(segments, event_type, badge, desc, color):
            events = []
            annotations = []
            for segment in segments:
                start = segment["start"]
                end = segment["end"]
                left = (start / duration) * 100 if duration > 0 else 0
                width = ((end - start) / duration) * 100 if duration > 0 else 0
                events.append({
                    "type": event_type,
                    "badge": badge,
                    "desc": desc,
                    "time": f"{start:.2f}s – {end:.2f}s",
                })
                annotations.append({
                    "left": f"{left:.2f}%",
                    "width": f"{width:.2f}%",
                    "color": color,
                    "event_type": event_type,
                })
            return events, annotations

        silence_events, silence_annotations = _build_events_and_annotations(
            silence_segments,
            "silence",
            "silêncio",
            "Segmento de silêncio detectado",
            "rgba(0, 100, 200, 0.25)",
        )
        clipping_events, clipping_annotations = _build_events_and_annotations(
            clipping_segments,
            "clip",
            "clipping",
            "Pico de saturação detectado",
            "rgba(255, 0, 0, 0.25)",
        )
        energy_events, energy_annotations = _build_events_and_annotations(
            energy_segments,
            "energy",
            "energia",
            "Variação abrupta de energia detectada",
            "rgba(255, 100, 0, 0.25)",
        )
        spectral_events, spectral_annotations = _build_events_and_annotations(
            spectral_segments,
            "spectral",
            "espectro",
            "Mudança significativa no espectro detectada",
            "rgba(0, 255, 0, 0.25)",
        )
        transient_events, transient_annotations = _build_events_and_annotations(
            transient_segments,
            "transient",
            "transitório",
            "Som transitório detectado",
            "rgba(255, 255, 0, 0.25)",
        )

        all_events = (
            silence_events
            + clipping_events
            + energy_events
            + spectral_events
            + transient_events
        )
        all_annotations = (
            silence_annotations
            + clipping_annotations
            + energy_annotations
            + spectral_annotations
            + transient_annotations
        )

        return {
            "spec": S_norm.tolist(),
            "duration": duration,
            "sample_rate": sr,
            "n_fft": 4096,
            "hop_length": hop_length,
            "silence_segments": silence_segments,
            "clipping_segments": clipping_segments,
            "events": all_events,
            "annotations": all_annotations,
            "background_noise": background_noise,
        }
    except Exception as e:
        print(f"Erro ao processar áudio: {type(e).__name__}: {str(e)}")
        import traceback

        traceback.print_exc()
        return None
