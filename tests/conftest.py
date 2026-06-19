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
    """Tom com pausa de silêncio e saturação real (flat-top consecutivo a 1.0).

    A pausa permite ao algoritmo de ruído distinguir piso de sinal;
    o flat-top de 50 ms (≫ 3 amostras) representa clipping real, não sinal alto limpo.
    """
    sr = sample_rate
    t = np.linspace(0, 2.0, int(2.0 * sr), endpoint=False)
    y = 0.5 * np.sin(2 * np.pi * 220 * t)
    y[int(0.3 * sr) : int(0.6 * sr)] = 0.0          # pausa de silêncio
    y[int(1.0 * sr) : int(1.05 * sr)] = 1.0          # saturação real: flat-top 50 ms
    return tmp_wav_factory("clipped.wav", y, sr)
