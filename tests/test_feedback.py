from backend.services.feedback import build_analysis_summary, generate_feedback


def _sample_spec_data():
    return {
        "duration": 42.5,
        "background_noise": "moderado",
        "silence_segments": [{"start": 1.0, "end": 2.0, "duration": 1.0}],
        "clipping_segments": [],
        "events": [
            {"type": "silence", "badge": "silêncio"},
            {"type": "energy", "badge": "energia"},
            {"type": "transient", "badge": "transitório"},
        ],
    }


def test_build_analysis_summary():
    summary = build_analysis_summary(_sample_spec_data())
    assert summary["duration"] == 42.5
    assert summary["background_noise"] == "moderado"
    assert summary["silence_count"] == 1
    assert summary["has_clipping"] is False


def test_generate_feedback_minimum_three_items():
    summary = build_analysis_summary(_sample_spec_data())
    result = generate_feedback(summary)
    assert "noise_level" in result
    assert "verdict" in result
    assert "stats" in result
    assert len(result["feedback_items"]) >= 3
    for item in result["feedback_items"]:
        assert "text" in item and "color" in item
        assert "title" in item and "category" in item
        text = item["text"].lower()
        for term in ("fft", "rms", "stft", "hz", "librosa", "espectro stft"):
            assert term not in text


def test_generate_feedback_clipping_message():
    spec = _sample_spec_data()
    spec["clipping_segments"] = [{"start": 0.5, "end": 0.6, "duration": 0.1}]
    spec["events"].append({"type": "clip", "badge": "clipping"})
    summary = build_analysis_summary(spec)
    result = generate_feedback(summary)
    texts = " ".join(i["text"] for i in result["feedback_items"]).lower()
    assert "distor" in texts or "alto" in texts or "estal" in texts
