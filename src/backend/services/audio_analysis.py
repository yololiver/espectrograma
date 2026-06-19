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

        # Calcula RMS uma vez para silêncio, energia e ruído de fundo
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

        # Deteção de silêncio adaptativa: limiar entre o ruído de fundo (p10)
        # e o nível de sinal típico (p90), independente do ganho da gravação
        p10 = float(np.percentile(rms, 10)) if len(rms) else 0.0
        p90 = float(np.percentile(rms, 90)) if len(rms) else 0.0
        silence_thresh = p10 + (p90 - p10) * 0.15

        is_silent = rms < silence_thresh
        sil_changes = np.flatnonzero(
            np.diff(is_silent.astype(int), prepend=0, append=0)
        )
        silence_segments = []
        for i in range(0, len(sil_changes) - 1, 2):
            s_t = (sil_changes[i]     * hop_length) / sr
            e_t = min((sil_changes[i + 1] * hop_length) / sr, duration)
            if e_t - s_t >= 0.12:
                silence_segments.append({
                    "start": round(s_t, 2),
                    "end": round(e_t, 2),
                    "duration": round(e_t - s_t, 2),
                })

        # Clipping real = flat-top: amostras consecutivas encostadas ao full-scale
        # Um seno limpo a 0.95 nunca atinge 0.99 → sem falsos positivos de amplitude alta
        clip_threshold = 0.99
        clip_min_run = 3  # mínimo de amostras consecutivas a full-scale

        clipping_mask = np.abs(y) >= clip_threshold
        clipping_segments = []
        if clipping_mask.any():
            changes = np.diff(clipping_mask.astype(np.int8), prepend=0, append=0)
            run_starts = np.where(changes == 1)[0]
            run_ends = np.where(changes == -1)[0]
            for s, e in zip(run_starts, run_ends):
                if e - s >= clip_min_run:
                    clipping_segments.append({
                        "start": round(s / sr, 2),
                        "end": round(e / sr, 2),
                        "duration": round((e - s) / sr, 2),
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

        # Ruído de fundo: piso absoluto em dBFS, com controlo de gama dinâmica.
        # A razão p10/max era cientificamente frágil: um tom limpo e constante dá
        # ratio ≈ 1.0 e seria sempre classificado como "alto". Em vez disso:
        #   1. Mede o piso em dBFS (limiar inferior independente do ganho da gravação).
        #   2. Só classifica se a gama dinâmica for ≥ 6 dB, ou seja, se existirem
        #      momentos quietos que permitam distinguir o piso do sinal principal.
        #   3. Se a gama for < 6 dB (e.g. tom contínuo sem pausas), não é possível
        #      separar ruído de sinal → "desconhecido".
        noise_floor_rms = p10
        noise_floor_dbfs = 20.0 * np.log10(max(float(noise_floor_rms), 1e-9))
        peak_rms = float(np.percentile(rms, 90)) if len(rms) else 1e-9
        peak_dbfs = 20.0 * np.log10(max(peak_rms, 1e-9))
        dynamic_range_db = peak_dbfs - noise_floor_dbfs

        if dynamic_range_db < 6.0:
            background_noise = "desconhecido"
        elif noise_floor_dbfs < -50.0:
            background_noise = "baixo"
        elif noise_floor_dbfs < -35.0:
            background_noise = "moderado"
        else:
            background_noise = "alto"

        def _merge(segs, gap=0.15, min_dur=0.08):
            """Agrupa segmentos próximos e impõe duração mínima visível."""
            if not segs:
                return []
            segs = sorted(segs, key=lambda s: s["start"])
            out = [dict(segs[0])]
            for s in segs[1:]:
                if s["start"] - out[-1]["end"] <= gap:
                    out[-1]["end"] = max(out[-1]["end"], s["end"])
                    out[-1]["duration"] = round(out[-1]["end"] - out[-1]["start"], 2)
                else:
                    out.append(dict(s))
            for s in out:
                if s["end"] - s["start"] < min_dur:
                    s["end"] = round(min(s["start"] + min_dur, duration), 2)
                    s["duration"] = round(s["end"] - s["start"], 2)
            return out

        # Limiar adaptativo: acima de 35% do intervalo dinâmico
        energy_thresh = p10 + (p90 - p10) * 0.35
        n = min(len(rms), len(is_silent))
        raw = []
        for i in range(1, n):
            if rms[i] > 2.5 * rms[i - 1] and rms[i] > energy_thresh and not is_silent[i]:
                s = (i * hop_length) / sr
                e = min((i + 2) * hop_length / sr, duration)
                raw.append({"start": round(s, 2), "end": round(e, 2), "duration": round(e - s, 2)})
        energy_segments = _merge(raw, gap=0.2, min_dur=0.08)

        centroid = librosa.feature.spectral_centroid(
            y=y, sr=sr, n_fft=4096, hop_length=hop_length
        )[0]
        nc = min(len(centroid), len(is_silent))
        # Limiar adaptativo baseado no desvio-padrão do centróide em frames não-silenciosas
        active_mask = ~is_silent[:nc]
        centroid_std = float(np.std(centroid[:nc][active_mask])) if active_mask.any() else 1500.0
        spectral_thresh = max(800.0, centroid_std * 1.5)
        raw = []
        for i in range(1, nc):
            # Ignora transições que envolvam frames silenciosas (centróide aí é ruído)
            if is_silent[i] or is_silent[i - 1]:
                continue
            if abs(centroid[i] - centroid[i - 1]) > spectral_thresh:
                s = (i * hop_length) / sr
                e = min((i + 2) * hop_length / sr, duration)
                raw.append({"start": round(s, 2), "end": round(e, 2), "duration": round(e - s, 2)})
        spectral_segments = _merge(raw, gap=0.2, min_dur=0.08)

        onset_frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=hop_length)
        raw = []
        for frame in onset_frames:
            s = (frame * hop_length) / sr
            e = min(s + 0.1, duration)
            raw.append({"start": round(s, 2), "end": round(e, 2), "duration": round(e - s, 2)})
        transient_segments = _merge(raw, gap=0.05, min_dur=0.08)

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
