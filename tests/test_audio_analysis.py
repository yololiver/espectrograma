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
    assert result["background_noise"] in {"baixo", "moderado", "alto"}
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
