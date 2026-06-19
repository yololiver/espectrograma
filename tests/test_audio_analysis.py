import numpy as np
import pytest

librosa = pytest.importorskip("librosa")

from backend.services.audio_analysis import normalize_spectrogram_db, process_audio_file


def test_normalize_spectrogram_db_uniform_avoids_division_by_zero():
    uniform = np.full((32, 64), -40.0)
    result = normalize_spectrogram_db(uniform)
    assert result.shape == uniform.shape
    assert result.dtype == np.uint8
    assert np.all(result == 0)


def test_normalize_spectrogram_db_spans_full_range():
    S_db = np.linspace(-80.0, 0.0, 100, dtype=np.float32).reshape(10, 10)
    result = normalize_spectrogram_db(S_db)
    assert int(result.min()) == 0
    assert int(result.max()) == 255


def test_process_silent_audio(tmp_wav_factory, sample_rate):
    sr = sample_rate
    y = np.zeros(int(1.0 * sr), dtype=np.float64)
    path = tmp_wav_factory("silent.wav", y, sr)
    result = process_audio_file(path)
    assert result is not None
    assert len(result["spec"]) > 0
    assert all(isinstance(row, list) for row in result["spec"])


@pytest.mark.parametrize(
    "fixture_name",
    ["tone_wav", "clipped_wav"],
)
def test_process_audio_returns_expected_keys(request, fixture_name):
    path = request.getfixturevalue(fixture_name)
    result = process_audio_file(path)
    assert result is not None
    for key in (
        "spec",
        "duration",
        "sample_rate",
        "events",
        "annotations",
        "background_noise",
        "silence_segments",
        "clipping_segments",
    ):
        assert key in result
    assert result["background_noise"] in {"baixo", "moderado", "alto", "desconhecido"}
    assert isinstance(result["spec"], list)
    assert len(result["spec"]) > 0


def test_silence_detected_on_tone_with_gap(tone_wav):
    result = process_audio_file(tone_wav)
    assert result is not None
    assert len(result["silence_segments"]) >= 1


def test_clipping_detected_on_saturated_wav(clipped_wav):
    result = process_audio_file(clipped_wav)
    assert result is not None
    clip_events = [e for e in result["events"] if e["type"] == "clip"]
    assert len(clip_events) >= 1


# ---------------------------------------------------------------------------
# Falsos positivos — garantir que sinais limpos não disparam alertas errados
# ---------------------------------------------------------------------------


def test_no_clipping_false_positive_on_clean_loud_sine(tmp_wav_factory, sample_rate):
    """Seno limpo a 0.95 de amplitude (sem flat-top) não deve reportar clipping."""
    sr = sample_rate
    t = np.linspace(0, 2.0, int(2.0 * sr), endpoint=False)
    y = 0.95 * np.sin(2 * np.pi * 440 * t)
    path = tmp_wav_factory("loud_clean_sine.wav", y, sr)
    result = process_audio_file(path)
    assert result is not None
    clip_events = [e for e in result["events"] if e["type"] == "clip"]
    assert len(clip_events) == 0, (
        f"Falso positivo: seno limpo a 0.95 reportado como clipping "
        f"({len(clip_events)} segmento(s))"
    )


def test_no_high_noise_false_positive_on_constant_clean_tone(tmp_wav_factory, sample_rate):
    """Tom sinusoidal limpo e contínuo não deve ser classificado como ruído 'alto'.

    A gama dinâmica é ≈0 dB (sem pausas) → algoritmo deve retornar 'desconhecido',
    nunca 'alto'. Confirma que a relação p10/max não é usada.
    """
    sr = sample_rate
    t = np.linspace(0, 2.0, int(2.0 * sr), endpoint=False)
    y = 0.5 * np.sin(2 * np.pi * 440 * t)
    path = tmp_wav_factory("constant_tone.wav", y, sr)
    result = process_audio_file(path)
    assert result is not None
    assert result["background_noise"] != "alto", (
        f"Falso positivo de ruído: tom limpo classificado como '{result['background_noise']}'"
    )


# ---------------------------------------------------------------------------
# Cobertura (recall) — critérios ≥80 % silêncio / ≥70 % eventos
# ---------------------------------------------------------------------------


def test_silence_recall_gte_80_percent(tmp_wav_factory, sample_rate):
    """Pelo menos 80 % dos segmentos de silêncio conhecidos devem ser detetados."""
    sr = sample_rate
    total_dur = 6.0
    silence_windows = [(0.5, 0.9), (1.5, 1.9), (2.5, 2.9), (3.5, 3.9), (4.5, 4.9)]
    t = np.linspace(0, total_dur, int(total_dur * sr), endpoint=False)
    y = 0.3 * np.sin(2 * np.pi * 440 * t)
    for s, e in silence_windows:
        y[int(s * sr) : int(e * sr)] = 0.0
    path = tmp_wav_factory("multi_silence.wav", y, sr)
    result = process_audio_file(path)
    assert result is not None

    detected = result["silence_segments"]
    found = sum(
        1
        for s, e in silence_windows
        if any(
            max(d["start"], s) < min(d["end"], e) - 0.05  # ≥50 ms de sobreposição
            for d in detected
        )
    )
    recall = found / len(silence_windows)
    assert recall >= 0.80, (
        f"Recall de silêncio {recall:.0%} abaixo de 80 % "
        f"(detetou {found}/{len(silence_windows)})"
    )


def test_transient_event_recall_gte_70_percent(tmp_wav_factory, sample_rate):
    """Pelo menos 70 % dos eventos transitórios conhecidos devem ser detetados."""
    sr = sample_rate
    total_dur = 5.5
    impulse_times = [0.5, 1.0, 2.0, 3.0, 4.0]
    n = int(total_dur * sr)
    t = np.linspace(0, total_dur, n, endpoint=False)
    y = 0.02 * np.sin(2 * np.pi * 200 * t)
    for imp_t in impulse_times:
        idx = int(imp_t * sr)
        if idx + 100 <= n:
            y[idx : idx + 100] += 0.8
    path = tmp_wav_factory("transient_events.wav", y, sr)
    result = process_audio_file(path)
    assert result is not None

    activity_events = [e for e in result["events"] if e["type"] in ("energy", "transient")]
    detected_times = []
    for e in activity_events:
        try:
            detected_times.append(float(e["time"].split("s")[0]))
        except ValueError:
            pass

    found = sum(
        1
        for t_known in impulse_times
        if any(abs(t_det - t_known) <= 0.3 for t_det in detected_times)
    )
    recall = found / len(impulse_times)
    assert recall >= 0.70, (
        f"Recall de eventos {recall:.0%} abaixo de 70 % "
        f"(detetou {found}/{len(impulse_times)})"
    )
