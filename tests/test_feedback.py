import pytest
from backend.services.feedback import build_analysis_summary, generate_feedback, format_duration


def _make_spec_data(**overrides):
    base = {
        "duration": 42.5,
        "background_noise": "baixo",
        "silence_segments": [],
        "clipping_segments": [],
        "events": [],
    }
    base.update(overrides)
    return base


TECHNICAL_TERMS = ("fft", "rms", "stft", "hz", "librosa", "espectro stft")


# ── format_duration ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("seconds,expected", [
    (30,  "30 segundos"),
    (60,  "1 minuto"),
    (120, "2 minutos"),
    (90,  "1 min 30 s"),
])
def test_format_duration(seconds, expected):
    assert format_duration(seconds) == expected


# ── build_analysis_summary ───────────────────────────────────────────────────

def test_build_analysis_summary():
    spec = _make_spec_data(
        duration=42.5,
        background_noise="moderado",
        silence_segments=[{"start": 1.0, "end": 2.0, "duration": 1.0}],
        events=[
            {"type": "silence", "badge": "silêncio"},
            {"type": "energy",  "badge": "energia"},
            {"type": "transient", "badge": "transitório"},
        ],
    )
    summary = build_analysis_summary(spec)
    assert summary["duration"] == 42.5
    assert summary["background_noise"] == "moderado"
    assert summary["silence_count"] == 1
    assert summary["has_clipping"] is False


# ── sem termos técnicos ──────────────────────────────────────────────────────

def test_feedback_no_technical_terms():
    summary = build_analysis_summary(_make_spec_data(
        background_noise="moderado",
        duration=42.5,
        silence_segments=[{"start": 1.0, "end": 2.0, "duration": 1.0}],
        events=[
            {"type": "silence",   "badge": "silêncio"},
            {"type": "energy",    "badge": "energia"},
            {"type": "transient", "badge": "transitório"},
        ],
    ))
    result = generate_feedback(summary)
    assert "noise_level" in result
    assert "verdict" in result
    assert "stats" in result
    assert len(result["feedback_items"]) >= 3
    for item in result["feedback_items"]:
        assert "text" in item and "color" in item
        assert "title" in item and "category" in item
        text = item["text"].lower()
        for term in TECHNICAL_TERMS:
            assert term not in text


# ── ruído de fundo ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("noise,expected_color", [
    ("baixo",       "#22c55e"),
    ("moderado",    "#eab308"),
    ("alto",        "#ef4444"),
    ("desconhecido","#94a3b8"),
])
def test_noise_feedback_color(noise, expected_color):
    summary = build_analysis_summary(_make_spec_data(background_noise=noise))
    result = generate_feedback(summary)
    item = next(i for i in result["feedback_items"] if i["category"] == "ruido")
    assert item["color"] == expected_color


# ── silêncios ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("silence_segments,expected_fragment", [
    ([], "não foram encontradas"),
    (
        [{"start": 1.0, "end": 2.0, "duration": 1.0}],
        "uma pausa",
    ),
    (
        [
            {"start": 1.0, "end": 2.0, "duration": 1.0},
            {"start": 5.0, "end": 6.0, "duration": 1.0},
        ],
        "2 pausas",
    ),
])
def test_silence_feedback(silence_segments, expected_fragment):
    events = [{"type": "silence", "badge": "silêncio"} for _ in silence_segments]
    summary = build_analysis_summary(_make_spec_data(
        silence_segments=silence_segments,
        events=events,
    ))
    result = generate_feedback(summary)
    item = next(i for i in result["feedback_items"] if i["category"] == "silencio")
    assert expected_fragment in item["text"].lower()


# ── clipping ─────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("clipping_segments,expected_fragment,expected_color", [
    (
        [],
        "estalar",
        "#22c55e",
    ),
    (
        [{"start": 0.5, "end": 0.6, "duration": 0.1}],
        "demasiado alto",
        "#ef4444",
    ),
    (
        [
            {"start": 0.5, "end": 0.6, "duration": 0.1},
            {"start": 1.0, "end": 1.1, "duration": 0.1},
        ],
        "2 momentos",
        "#ef4444",
    ),
])
def test_clipping_feedback(clipping_segments, expected_fragment, expected_color):
    events = [{"type": "clip", "badge": "clipping"} for _ in clipping_segments]
    summary = build_analysis_summary(_make_spec_data(
        clipping_segments=clipping_segments,
        events=events,
    ))
    result = generate_feedback(summary)
    item = next(i for i in result["feedback_items"] if i["category"] == "distorcao")
    assert expected_fragment in item["text"].lower()
    assert item["color"] == expected_color


# ── atividade ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("activity_count,expected_fragment", [
    (0, "uniforme"),
    (3, "3 momentos"),
    (6, "bastante dinâmico"),
])
def test_activity_feedback(activity_count, expected_fragment):
    events = [{"type": "energy", "badge": "energia"} for _ in range(activity_count)]
    summary = build_analysis_summary(_make_spec_data(events=events))
    result = generate_feedback(summary)
    item = next(i for i in result["feedback_items"] if i["category"] == "actividade")
    assert expected_fragment in item["text"].lower()


# ── veredicto ────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("spec_overrides,expected_label", [
    (
        {"background_noise": "baixo"},
        "Boa qualidade geral",
    ),
    (
        {"background_noise": "moderado"},
        "Qualidade razoável",
    ),
    (
        {
            "background_noise": "alto",
            "clipping_segments": [{"start": 0.5, "end": 0.6, "duration": 0.1}],
            "events": [{"type": "clip", "badge": "clipping"}],
        },
        "Precisa de atenção",
    ),
])
def test_verdict(spec_overrides, expected_label):
    summary = build_analysis_summary(_make_spec_data(**spec_overrides))
    result = generate_feedback(summary)
    assert result["verdict"]["label"] == expected_label
