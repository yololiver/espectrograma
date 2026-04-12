# Levantamento de Requisitos

**Projecto:** Espectrograma — Análise e Interpretação de Áudio para Utilizadores Não Especialistas  
**Versão:** 1.0 · Abril 2026  
**Referência MoSCoW:** https://www.productplan.com/glossary/moscow-prioritization/

---

## 1. Levantamento de Requisitos (MoSCoW)

O método MoSCoW classifica os requisitos em quatro categorias: **Must Have** (obrigatório para o MVP), **Should Have** (importante mas não crítico), **Could Have** (desejável se houver tempo), e **Won't Have** (fora do âmbito desta iteração).

---

### 1.1 Must Have

Requisitos essenciais sem os quais o MVP não é funcional ou entregável.

| ID | Requisito | Critério de aceitação resumido |
|----|-----------|-------------------------------|
| M01 | Upload de ficheiro de áudio (WAV/MP3, ≤ 10 MB) | Upload bem-sucedido inicia análise; ficheiro inválido gera mensagem de erro clara |
| M02 | Geração e visualização do espectrograma 2D | Espectrograma apresentado após upload, com eixo temporal (X) e de frequência (Y) |
| M03 | Deteção de segmentos de silêncio | Identifica ≥ 80% dos silêncios num áudio de teste; apresenta timestamps |
| M04 | Deteção de clipping (distorção por saturação) | Identifica picos de clipping com timestamps; confirma ausência quando não existe |
| M05 | Análise de ruído de fundo | Classifica ruído como "baixo", "moderado" ou "alto", sem métricas técnicas |
| M06 | Deteção de eventos sonoros relevantes | Identifica ≥ 70% dos eventos por variação de energia/frequência; apresenta timestamps |
| M07 | Anotação visual de eventos no espectrograma | ≥ 3 tipos de eventos representados com cores distintas e legíveis sem conhecimento técnico |
| M08 | Feedback automático em linguagem simples | ≥ 3 observações sobre qualidade do áudio, sem termos técnicos (ex.: sem "FFT", "RMS") |
| M09 | Interface web utilizável por não especialistas | Utilizador sem experiência completa o fluxo (upload → análise → interpretação) sem erros |

---

### 1.2 Should Have

Requisitos importantes que melhoram significativamente a experiência, mas cuja ausência não inviabiliza o MVP.

| ID | Requisito |
|----|-----------|
| S01 | Navegação por segmentos do áudio (clicar num evento e ouvir o segmento correspondente) |
| S02 | Indicador de progresso durante o processamento do áudio |
| S03 | Exportação do relatório de análise em formato texto ou PDF |
| S04 | Responsividade da interface para diferentes resoluções de ecrã |
| S05 | Suporte a ficheiros MP3 com bitrate variável (VBR) |

---

### 1.3 Could Have

Requisitos desejáveis, implementados apenas se o calendário o permitir.

| ID | Requisito |
|----|-----------|
| C01 | Visualização 3D interactiva do espectrograma (Three.js) |
| C02 | Limpeza automática de áudio (redução de ruído e normalização via `noisereduce`) |
| C03 | Ferramenta de selecção por região no espectrograma (marquee tool) |
| C04 | Histórico de ficheiros analisados na sessão actual |
| C05 | Tooltips explicativos sobre cada tipo de evento detectado |

---

### 1.4 Won't Have

Requisitos explicitamente excluídos desta iteração do projecto.

| ID | Requisito | Justificação |
|----|-----------|-------------|
| W01 | Autenticação de utilizadores / contas persistentes | Fora do âmbito do MVP; complexidade desnecessária nesta fase |
| W02 | Processamento em tempo real (streaming de áudio ao vivo) | Requer arquitectura de baixa latência fora do âmbito actual |
| W03 | Suporte a formatos de áudio sem perdas (FLAC, AIFF, OGG) | Limitado a WAV e MP3 no MVP |
| W04 | Transcrição de fala (speech-to-text) | Funcionalidade distinta com requisitos de ML específicos |
| W05 | API pública para integração com terceiros | Não previsto nesta versão |

---

## 2. Arquitectura do Sistema (C4 — Nível 1 e 2)

### 2.1 Nível 1 — Diagrama de Contexto (System Context)

O diagrama de contexto descreve o sistema na sua relação com os actores externos.

```
┌─────────────────────────────────────────────────────────────┐
│                       CONTEXTO DO SISTEMA                   │
└─────────────────────────────────────────────────────────────┘

        ┌──────────────────┐
        │   Utilizador     │
        │  Não Especialista│
        │ (estudante,      │
        │  jornalista,     │
        │  criador conteúdo│
        └────────┬─────────┘
                 │
                 │  Faz upload de áudio
                 │  Recebe espectrograma anotado
                 │  e feedback em linguagem simples
                 ▼
        ┌──────────────────────────────────────┐
        │                                      │
        │         ESPECTROGRAMA                │
        │  Análise e Interpretação de Áudio    │
        │       (Aplicação Web)                │
        │                                      │
        └──────────────────────────────────────┘
```

**Actores externos:**

| Actor | Tipo | Interacção |
|-------|------|------------|
| Utilizador não especialista | Pessoa | Carrega ficheiros de áudio; visualiza espectrograma e relatório gerado |

> Nota: O sistema não depende de serviços externos de terceiros. Todo o processamento é realizado localmente no servidor Flask.

---

### 2.2 Nível 2 — Diagrama de Contentores (Container Diagram)

O diagrama de contentores decompõe o sistema nos seus principais blocos tecnológicos e nas comunicações entre eles.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          SISTEMA: ESPECTROGRAMA                        │
│                                                                        │
│  ┌──────────────────────────────────┐                                  │
│  │         FRONTEND                 │                                  │
│  │  React + Vite                    │                                  │
│  │                                  │                                  │
│  │  • Interface de upload           │                                  │
│  │  • Visualização do espectrograma │                                  │
│  │    (Canvas API / Three.js)       │                                  │
│  │  • Anotação visual de eventos    │                                  │
│  │  • Painel de feedback textual    │                                  │
│  │  • Web Audio API (reprodução)    │                                  │
│  └──────────────┬───────────────────┘                                  │
│                 │                                                       │
│        HTTP REST (JSON + multipart/form-data)                          │
│                 │                                                       │
│  ┌──────────────▼───────────────────┐                                  │
│  │         BACKEND (API)            │                                  │
│  │  Flask (Python)                  │                                  │
│  │                                  │                                  │
│  │  • Recepção e validação de upload│                                  │
│  │  • Orquestração do pipeline      │                                  │
│  │    de análise                    │                                  │
│  │  • Serialização dos resultados   │                                  │
│  │    em JSON                       │                                  │
│  └──────────────┬───────────────────┘                                  │
│                 │                                                       │
│        Chamadas Python internas                                        │
│                 │                                                       │
│  ┌──────────────▼───────────────────┐                                  │
│  │     MÓDULO DE PROCESSAMENTO      │                                  │
│  │     DE ÁUDIO (Python)            │                                  │
│  │                                  │                                  │
│  │  • librosa  → espectrograma,     │                                  │
│  │               deteção de eventos │                                  │
│  │  • numpy    → operações matriciais│                                 │
│  │  • scipy    → filtragem de sinal │                                  │
│  │  • pydub    → leitura/conversão  │                                  │
│  │               de formatos        │                                  │
│  │  • noisereduce → análise de ruído│                                  │
│  └──────────────────────────────────┘                                  │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

**Descrição dos contentores:**

| Contentor | Tecnologia | Responsabilidade principal |
|-----------|------------|---------------------------|
| **Frontend** | React (Vite), Canvas API, Three.js, Web Audio API | Apresentação da interface, visualização do espectrograma, reprodução de segmentos de áudio, exibição de anotações e feedback |
| **Backend (API)** | Flask (Python) | Exposição de endpoints REST, validação dos ficheiros recebidos, orquestração do pipeline de análise, formatação e devolução dos resultados |
| **Módulo de Processamento** | librosa, numpy, scipy, pydub, noisereduce | Extracção de características do sinal de áudio: geração do espectrograma, deteção de silêncio, clipping, ruído de fundo e eventos sonoros |

**Fluxo principal de dados:**

1. O utilizador selecciona e envia um ficheiro de áudio via interface web.
2. O Frontend envia o ficheiro por `multipart/form-data` para o Backend Flask.
3. O Backend valida o ficheiro e invoca o Módulo de Processamento.
4. O Módulo de Processamento analisa o sinal e devolve os resultados ao Backend.
5. O Backend serializa os resultados em JSON e responde ao Frontend.
6. O Frontend renderiza o espectrograma anotado e apresenta o feedback ao utilizador.

---

## 3. Modelo de Dados Preliminar

O sistema não utiliza base de dados persistente. Toda a informação é gerada em memória durante o ciclo de vida de um pedido HTTP e descartada após a resposta. O estado no frontend é mantido em React state e desaparece ao fechar ou recarregar a página.

A documentação que se segue descreve as estruturas de dados em memória — os objectos Python produzidos no backend e o JSON transmitido ao frontend.

### 3.1 Fluxo de dados em memória

```
Utilizador
    │  ficheiro de áudio (WAV / MP3)
    ▼
[Frontend — React state]
    │  multipart/form-data
    ▼
[Backend Flask]
    │  bytes em memória (BytesIO)
    ▼
[Módulo de Processamento]
    │  objectos Python (AudioFile → AnalysisResult)
    ▼
[Backend Flask]
    │  serialização → JSON
    ▼
[Frontend — React state]        ← descartado ao fechar/recarregar
```

### 3.2 Estruturas de dados Python (backend / módulo de processamento)

```python
@dataclass
class AudioFile:
    filename: str
    duration_seconds: float
    sample_rate: int          # Hz, ex.: 44100
    channels: int             # 1 = mono, 2 = stereo
    data: np.ndarray          # sinal em memória (librosa)

@dataclass
class SilenceSegment:
    start: float              # segundos
    end: float

@dataclass
class ClippingSegment:
    start: float
    end: float

@dataclass
class SoundEvent:
    start: float
    end: float
    type: str                 # "impacto" | "variacao_energia" | "variacao_espectral"

@dataclass
class AnalysisResult:
    noise_level: str          # "baixo" | "moderado" | "alto"
    spectrogram_b64: str      # PNG codificado em base64
    time_axis: list[float]
    freq_axis: list[float]
    silence_segments: list[SilenceSegment]
    clipping_segments: list[ClippingSegment]
    sound_events: list[SoundEvent]
    feedback: list[str]       # observações em linguagem simples
```

### 3.3 Estrutura da resposta da API (JSON)

```json
{
  "audio_info": {
    "filename": "gravacao.wav",
    "duration_seconds": 42.3,
    "sample_rate": 44100,
    "channels": 1
  },
  "spectrogram": {
    "image_base64": "<string base64>",
    "time_axis": [0.0, 0.023, 0.046],
    "frequency_axis": [0.0, 43.0, 86.0]
  },
  "analysis": {
    "noise_level": "moderado",
    "silence_segments": [
      { "start": 2.1, "end": 4.8 },
      { "start": 18.0, "end": 20.5 }
    ],
    "clipping_segments": [
      { "start": 7.3, "end": 7.4 }
    ],
    "sound_events": [
      { "start": 5.0, "end": 5.2, "type": "impacto" },
      { "start": 11.4, "end": 11.7, "type": "variacao_energia" }
    ]
  },
  "feedback": [
    "O áudio apresenta ruído de fundo moderado ao longo de toda a gravação.",
    "Existem picos de distorção aos 7 segundos.",
    "Foram detectadas duas pausas prolongadas entre os 2 e os 20 segundos."
  ]
}
```

> O JSON é descartado no backend após envio. No frontend, os dados são mantidos em React state (`useState`) enquanto a sessão estiver activa.

### 3.4 Entidades e atributos

| Entidade | Atributo | Tipo | Descrição |
|----------|----------|------|-----------|
| `AudioFile` | `filename` | string | Nome do ficheiro carregado |
| | `duration_seconds` | float | Duração total em segundos |
| | `sample_rate` | int | Taxa de amostragem (Hz) |
| | `channels` | int | 1 = mono, 2 = stereo |
| | `data` | np.ndarray | Sinal de áudio em memória |
| `AnalysisResult` | `noise_level` | enum | `"baixo"` \| `"moderado"` \| `"alto"` |
| | `spectrogram_b64` | string | Imagem PNG do espectrograma codificada em base64 |
| | `time_axis` | float[] | Instantes temporais das colunas do espectrograma |
| | `freq_axis` | float[] | Frequências das linhas do espectrograma |
| | `feedback` | string[] | Observações em linguagem simples |
| `SilenceSegment` | `start`, `end` | float | Intervalo temporal (segundos) |
| `ClippingSegment` | `start`, `end` | float | Intervalo temporal do pico de saturação |
| `SoundEvent` | `start`, `end` | float | Intervalo temporal do evento |
| | `type` | string | `"impacto"` \| `"variacao_energia"` \| `"variacao_espectral"` |

---

*Documentação gerada para o Projecto Final em Engenharia Informática — Universidade Aberta, 2026.*
