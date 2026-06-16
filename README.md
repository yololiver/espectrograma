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

- [x] Setup do repositório — estrutura de pastas e documentação inicial
- [x] Wireframes da interface 
- [x] Upload de ficheiro de áudio — aceitação de WAV/MP3 até 10 MB com validação e mensagem de erro
- [x] Geração do espectrograma 2D — visualização com eixo temporal (X) e de frequência (Y)
- [x] Deteção de silêncio — identificação de segmentos com timestamps
- [x] Deteção de clipping — identificação de picos de saturação com timestamps
- [x] Análise de ruído de fundo — classificação em "baixo", "moderado" ou "alto"
- [x] Deteção de eventos sonoros — variações de energia, mudanças espectrais e sons transitórios
- [x] Anotação visual de eventos — ≥ 3 tipos com cores distintas no espectrograma/timeline
- [x] Feedback automático em linguagem simples — ≥ 3 observações sem termos técnicos
- [x] Interface web utilizável — fluxo completo (upload → análise → feedback)
- [x] Todas as funcionalidades do MVP — implementação prevista para as semanas 5–12 conforme calendário

---

## Como instalar e correr

### Pré-requisitos

- **Python** 3.8 ou superior
- **pip** (package manager do Python)
- **Git** (para clonar o repositório)

### Dependências

As dependências do projeto estão listadas em [`requirements.txt`](requirements.txt) e incluem:
- Flask 2.3+ — Framework web para a API backend
- librosa 0.10+ — Processamento e análise de áudio
- SciPy e NumPy — Cálculos científicos

### Instalação

1. **Clonar o repositório**
   ```bash
   git clone https://github.com/yololiver/espectrograma.git
   cd espectrograma
   ```

2. **Criar um ambiente virtual (recomendado)**
   ```bash
   python -m venv venv
   ```

3. **Ativar o ambiente virtual**
   
   **Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```

4. **Instalar as dependências do `requirements.txt`**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configurar variáveis de ambiente** (opcional)
   - Criar um ficheiro `.env` na raiz do projeto (usar `.env.example` como referência se disponível)
   - As configurações padrão funcionam para desenvolvimento local

### Executar a aplicação

```bash
python src/run.py
```

A aplicação estará disponível em **http://127.0.0.1:5000**

### Testes (opcional)

```bash
pip install -r requirements-dev.txt
pytest
```

## Decisões de arquitectura principais

| Decisão | Alternativa considerada | Razão da escolha |
|---------|------------------------|-----------------|
| Flask (backend + UI) | FastAPI + SPA separado | Monólito simples: rotas, templates Jinja2 e sessão num único processo |
| Templates Jinja2 + Canvas | React + Vite | Menos complexidade de integração no MVP; espectrograma renderizado em `<canvas>` com dados do servidor |
| librosa (processamento de áudio) | essentia, torchaudio | API de alto nível orientada a análise; documentação extensa; não requer GPU |
| Espectrograma via Canvas API | biblioteca de charting (Chart.js, Plotly) | Controlo total sobre a renderização e anotação visual sem dependências adicionais |
| Serviços em `backend/services/` | Toda a lógica nas rotas | Separação entre HTTP e análise/feedback; facilita testes com pytest |

---

## Referências e IA utilizada

### Referências técnicas

- [librosa — documentação oficial](https://librosa.org/doc/)
- [Flask — documentação oficial](https://flask.palletsprojects.com/)


### Ferramentas de IA utilizadas

| Ferramenta | Para que foi usada |
|-----------|-------------------|
| Claude (Anthropic) | Apoio na redacção da documentação (requisitos MoSCoW, arquitectura C4, gestão de riscos, README) |
| GitHub Copilot | Assistência no desenvolvimento de código, geração de templates, documentação de código-fonte |


---


