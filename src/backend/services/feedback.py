"""Geração de feedback em linguagem simples (requisito M08)."""

NOISE_LABELS = {
    "baixo": "Ruído de fundo baixo",
    "moderado": "Ruído de fundo moderado",
    "alto": "Ruído de fundo alto",
    "desconhecido": "Ruído de fundo não avaliado",
}

NOISE_PILL_CLASS = {
    "baixo": "noise-pill--low",
    "moderado": "noise-pill--mid",
    "alto": "noise-pill--high",
    "desconhecido": "noise-pill--unknown",
}


def build_analysis_summary(spec_data):
    """Extrai métricas leves para feedback e sessão (sem a matriz do espectrograma)."""
    events = spec_data.get("events", [])
    silence_segments = spec_data.get("silence_segments", [])
    clipping_segments = spec_data.get("clipping_segments", [])

    def count_type(event_type):
        return sum(1 for ev in events if ev.get("type") == event_type)

    total_silence = sum(s.get("duration", 0) for s in silence_segments)
    duration = float(spec_data.get("duration", 0))

    return {
        "duration": round(duration, 2),
        "background_noise": spec_data.get("background_noise", "desconhecido"),
        "silence_count": count_type("silence"),
        "clipping_count": count_type("clip"),
        "energy_count": count_type("energy"),
        "spectral_count": count_type("spectral"),
        "transient_count": count_type("transient"),
        "total_silence_seconds": round(total_silence, 2),
        "has_clipping": bool(clipping_segments),
        "clipping_segments": len(clipping_segments),
    }


def format_duration(seconds):
    if seconds < 60:
        return f"{seconds:.0f} segundos"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if secs == 0:
        return f"{minutes} minuto{'s' if minutes != 1 else ''}"
    return f"{minutes} min {secs} s"


def _compute_verdict(summary):
    """Resumo global em linguagem simples."""
    noise = summary.get("background_noise", "desconhecido")
    has_clipping = summary.get("has_clipping", False)
    activity = (
        summary.get("energy_count", 0)
        + summary.get("spectral_count", 0)
        + summary.get("transient_count", 0)
    )

    issues = 0
    if noise == "alto":
        issues += 2
    elif noise == "moderado":
        issues += 1
    if has_clipping:
        issues += 2
    if summary.get("silence_count", 0) > 5:
        issues += 1

    if issues >= 3:
        return {
            "label": "Precisa de atenção",
            "detail": "Foram encontrados vários pontos que podem afetar a qualidade da gravação.",
            "tone": "warn",
        }
    if issues >= 1:
        return {
            "label": "Qualidade razoável",
            "detail": "O áudio está utilizável, mas há alguns aspectos a rever no resumo abaixo.",
            "tone": "caution",
        }
    return {
        "label": "Boa qualidade geral",
        "detail": "Não foram detetados problemas graves. Consulte o detalhe para confirmar.",
        "tone": "good",
    }


def generate_feedback(summary):
    """
    Produz ≥ 3 observações em português simples, sem termos técnicos.
    Retorna noise_level, feedback_items (com category/title), stats e verdict.
    """
    duration = summary.get("duration", 0)
    noise = summary.get("background_noise", "desconhecido")
    silence_count = summary.get("silence_count", 0)
    silence_secs = summary.get("total_silence_seconds", 0)
    has_clipping = summary.get("has_clipping", False)
    clipping_count = summary.get("clipping_count", 0)
    energy = summary.get("energy_count", 0)
    spectral = summary.get("spectral_count", 0)
    transient = summary.get("transient_count", 0)
    activity_count = energy + spectral + transient

    items = []

    if noise == "baixo":
        items.append({
            "category": "ruido",
            "title": "Ruído de fundo",
            "text": (
                "O áudio parece limpo: o ruído de fundo é discreto e não deve "
                "atrapalhar a audição do conteúdo principal."
            ),
            "color": "#22c55e",
        })
    elif noise == "moderado":
        items.append({
            "category": "ruido",
            "title": "Ruído de fundo",
            "text": (
                "Existe um ruído de fundo perceptível. Pode ser aceitável, "
                "mas convém prestar atenção se estiver a gravar ou editar."
            ),
            "color": "#eab308",
        })
    elif noise == "alto":
        items.append({
            "category": "ruido",
            "title": "Ruído de fundo",
            "text": (
                "O ruído de fundo é bastante presente. Considere gravar num "
                "ambiente mais silencioso ou reduzir o ruído na edição."
            ),
            "color": "#ef4444",
        })
    else:
        items.append({
            "category": "ruido",
            "title": "Ruído de fundo",
            "text": "Não foi possível avaliar o ruído de fundo deste ficheiro.",
            "color": "#94a3b8",
        })

    if silence_count == 0:
        items.append({
            "category": "silencio",
            "title": "Pausas e silêncio",
            "text": (
                f"Durante os {format_duration(duration)}, não foram encontradas "
                "pausas longas de silêncio — o som mantém-se contínuo."
            ),
            "color": "#0064C8",
        })
    elif silence_count == 1:
        items.append({
            "category": "silencio",
            "title": "Pausas e silêncio",
            "text": (
                f"Foi detetada uma pausa de silêncio (cerca de "
                f"{silence_secs:.0f} segundos no total). Pode ser uma respiração "
                "ou uma interrupção natural na gravação."
            ),
            "color": "#0064C8",
        })
    else:
        items.append({
            "category": "silencio",
            "title": "Pausas e silêncio",
            "text": (
                f"Foram detetadas {silence_count} pausas de silêncio, somando cerca de "
                f"{silence_secs:.0f} segundos. Verifique se estas pausas são intencionais."
            ),
            "color": "#0064C8",
        })

    if has_clipping:
        if clipping_count == 1:
            items.append({
                "category": "distorcao",
                "title": "Volume e distorção",
                "text": (
                    "Foi encontrado um momento em que o som está demasiado alto e "
                    "pode soar distorcido ou «estalado». Vale a pena baixar o volume "
                    "nessa zona."
                ),
                "color": "#ef4444",
            })
        else:
            items.append({
                "category": "distorcao",
                "title": "Volume e distorção",
                "text": (
                    f"Foram encontrados {clipping_count} momentos com som demasiado "
                    "alto (possível distorção). Recomenda-se reduzir o volume ou "
                    "regravar essas partes."
                ),
                "color": "#ef4444",
            })
    else:
        items.append({
            "category": "distorcao",
            "title": "Volume e distorção",
            "text": (
                "Não foram detetados picos de volume excessivo — o áudio não "
                "parece estar «a estalar» por saturação."
            ),
            "color": "#22c55e",
        })

    if activity_count == 0:
        items.append({
            "category": "actividade",
            "title": "Variações no som",
            "text": (
                "O som mantém-se relativamente uniforme, sem mudanças bruscas "
                "de volume nem sons curtos muito destacados."
            ),
            "color": "#64748b",
        })
    elif activity_count <= 5:
        items.append({
            "category": "actividade",
            "title": "Variações no som",
            "text": (
                f"Foram encontrados {activity_count} momentos com mudanças de "
                "volume, timbre ou sons curtos (como batidas ou cliques). "
                "Consulte o espectrograma para ver quando ocorrem."
            ),
            "color": "#FF5500",
        })
    else:
        items.append({
            "category": "actividade",
            "title": "Variações no som",
            "text": (
                f"O áudio é bastante dinâmico: foram encontrados {activity_count} "
                "momentos com variações de som. Isto é normal em entrevistas, "
                "música ou ambientes com muitos ruídos."
            ),
            "color": "#FF5500",
        })

    if len(items) < 3:
        items.append({
            "category": "geral",
            "title": "Duração",
            "text": (
                f"A análise cobre {format_duration(duration)} de áudio. "
                "Pode voltar ao espectrograma para explorar os detalhes visuais."
            ),
            "color": "#64748b",
        })

    stats = {
        "duration_label": format_duration(duration),
        "silence_count": silence_count,
        "clipping_count": clipping_count,
        "activity_count": activity_count,
        "total_events": silence_count + clipping_count + activity_count,
    }

    highlights = [
        {"label": "Duração", "value": stats["duration_label"]},
        {"label": "Pausas", "value": str(silence_count)},
        {
            "label": "Distorção",
            "value": "Sim" if has_clipping else "Não",
            "warn": has_clipping,
        },
        {"label": "Variações", "value": str(activity_count)},
    ]

    return {
        "noise_level": NOISE_LABELS.get(noise, NOISE_LABELS["desconhecido"]),
        "noise_tone": noise,
        "noise_pill_class": NOISE_PILL_CLASS.get(noise, NOISE_PILL_CLASS["desconhecido"]),
        "feedback_items": items[:6],
        "stats": stats,
        "highlights": highlights,
        "verdict": _compute_verdict(summary),
    }
