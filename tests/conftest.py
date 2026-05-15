import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def sample_rate():
    return 22050


@pytest.fixture
def tmp_wav_factory(tmp_path):
    def _make(name, y, sr=22050):
        path = tmp_path / name
        y_int = np.clip(y * 32767, -32767, 32767).astype(np.int16)
        wavfile.write(str(path), sr, y_int)
        return str(path)

    return _make


@pytest.fixture
def tone_wav(tmp_wav_factory, sample_rate):
    """Tom contínuo com silêncio no meio."""
    sr = sample_rate
    t = np.linspace(0, 2.0, int(2.0 * sr), endpoint=False)
    y = 0.3 * np.sin(2 * np.pi * 440 * t)
    mid = len(y) // 2
    y[mid : mid + int(0.5 * sr)] = 0.0
    return tmp_wav_factory("tone_silence.wav", y, sr)


@pytest.fixture
def clipped_wav(tmp_wav_factory, sample_rate):
    """Tom com pico saturado."""
    sr = sample_rate
    t = np.linspace(0, 1.0, int(1.0 * sr), endpoint=False)
    y = 0.5 * np.sin(2 * np.pi * 220 * t)
    y[int(0.5 * sr) : int(0.55 * sr)] = 1.0
    return tmp_wav_factory("clipped.wav", y, sr)
