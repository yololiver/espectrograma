# Espectrograma

> Ferramenta web que analisa ficheiros de áudio e explica o que contêm — em linguagem simples, sem exigir conhecimento técnico.

**Estudante:** Paulo Silva · 2100537  
**Orientador:** Pedro Pestana  
**UC:** Projecto de Engenharia Informática · Universidade Aberta · 2025/26  
**Repositório:** https://github.com/yololiver/espectrograma

---

## Estado actual

🟢 Verde — A correr conforme planeado.

---

## O que está implementado

- [x] Setup do repositório — estrutura de pastas e documentação inicial (previsto semanas 3–4)
- [ ] Wireframes da interface — previstos para as semanas 5–6
- [ ] Upload de ficheiro de áudio — aceitação de WAV/MP3 até 10 MB com validação e mensagem de erro
- [ ] Geração do espectrograma 2D — visualização com eixo temporal (X) e de frequência (Y)
- [ ] Deteção de silêncio — identificação de segmentos com timestamps
- [ ] Deteção de clipping — identificação de picos de saturação com timestamps
- [ ] Análise de ruído de fundo — classificação em "baixo", "moderado" ou "alto"
- [ ] Deteção de eventos sonoros — variações de energia, mudanças espectrais e sons transitórios
- [ ] Anotação visual de eventos — ≥ 3 tipos com cores distintas no espectrograma/timeline
- [ ] Feedback automático em linguagem simples — ≥ 3 observações sem termos técnicos
- [ ] Interface web utilizável — fluxo completo sem formação prévia
- [ ] Todas as funcionalidades do MVP — implementação prevista para as semanas 5–12 conforme calendário

---

## Como instalar e correr

### Pré-requisitos
---
### Instalação
---

## Decisões de arquitectura principais

| Decisão | Alternativa considerada | Razão da escolha |
|---------|------------------------|-----------------|
| Flask (backend) | FastAPI | Simplicidade e familiaridade; overhead mínimo para uma API sem requisitos de alta concorrência no MVP |
| React + Vite (frontend) | Vue.js | Ecossistema mais amplo; compatibilidade com Three.js e Web Audio API bem documentada |
| librosa (processamento de áudio) | essentia, torchaudio | API de alto nível orientada a análise; documentação extensa; não requer GPU |
| Espectrograma via Canvas API | biblioteca de charting (Chart.js, Plotly) | Controlo total sobre a renderização e anotação visual sem dependências adicionais |

---

## Referências e IA utilizada

### Referências técnicas

- [librosa — documentação oficial](https://librosa.org/doc/)
- [Web Audio API — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [Canvas API — MDN](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)
- [Flask — documentação oficial](https://flask.palletsprojects.com/)
- [noisereduce — repositório](https://github.com/timsainburg/noisereduce)

### Ferramentas de IA utilizadas

| Ferramenta | Para que foi usada |
|-----------|-------------------|
| Claude (Anthropic) | Apoio na redacção da documentação (requisitos MoSCoW, arquitectura C4, gestão de riscos, README) |

---

*Última actualização: Abril 2026 · Sem. 3–4*
