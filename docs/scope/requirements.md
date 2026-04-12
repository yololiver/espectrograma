# Levantamento de Requisitos

**Projecto:** Espectrograma — Análise e Interpretação de Áudio para Utilizadores Não Especialistas  
**Versão:** 1.0 · Abril 2026  
**Referência MoSCoW:** https://www.productplan.com/glossary/moscow-prioritization/

---

## Método MoSCoW

| Categoria | Significado |
|-----------|------------|
| **Must have** | Obrigatório. Sem isto o projecto não é entregável. |
| **Should have** | Importante mas não crítico. Incluir se o tempo permitir. |
| **Could have** | Desejável. Só se tudo o resto estiver concluído. |
| **Won't have** | Explicitamente fora do âmbito desta versão. |

---

## Requisitos funcionais

<!-- O que o sistema faz. -->

### Must have

- RF01 — **Upload de ficheiro de áudio:** O utilizador pode carregar um ficheiro WAV ou MP3 até 10 MB; o sistema inicia a análise automaticamente após upload válido e apresenta mensagem de erro clara para ficheiros inválidos.
- RF02 — **Visualização do espectrograma 2D:** O sistema apresenta o espectrograma após o upload, com eixo temporal (X) e de frequência (Y), correspondente ao conteúdo real do áudio.
- RF03 — **Deteção de segmentos de silêncio:** O sistema identifica automaticamente segmentos silenciosos (≥ 80% de cobertura num áudio de teste) e apresenta-os com timestamps (ex.: 0:10–0:15).
- RF04 — **Deteção de clipping (distorção):** O sistema identifica picos de saturação com os respectivos timestamps; quando não existe clipping, apresenta "Sem distorção detectada".
- RF05 — **Análise de ruído de fundo:** O sistema classifica o ruído contínuo como "baixo", "moderado" ou "alto", sem recurso a métricas técnicas.
- RF06 — **Deteção de eventos sonoros relevantes:** O sistema identifica variações abruptas de energia, mudanças significativas no espectro e sons transitórios (ex.: batidas, cliques), com timestamps e cobertura ≥ 70% num áudio de teste.
- RF07 — **Anotação visual de eventos:** O espectrograma e/ou timeline apresentam pelo menos 3 tipos de eventos (ruído de fundo, clipping, eventos sonoros) com cores distintas, distinguíveis sem conhecimento técnico.
- RF08 — **Feedback automático em linguagem simples:** O sistema gera pelo menos 3 observações sobre a qualidade do áudio, sem termos técnicos (ex.: "O áudio apresenta ruído de fundo leve", "Existem picos de distorção em alguns momentos").
- RF09 — **Interface web utilizável por não especialistas:** Um utilizador sem experiência técnica consegue completar o fluxo completo (upload → análise → interpretação) sem erros visuais críticos.

### Should have

- RF10 — **Navegação por segmentos:** O utilizador pode clicar num evento anotado e ouvir o segmento de áudio correspondente directamente na interface.
- RF11 — **Indicador de progresso:** A interface apresenta feedback visual durante o processamento do áudio (ex.: barra de progresso ou spinner com estado).
- RF12 — **Exportação do relatório:** O utilizador pode exportar o relatório de análise em formato texto ou PDF.
- RF13 — **Interface responsiva:** A interface adapta-se correctamente a diferentes resoluções de ecrã (desktop e tablet).
- RF14 — **Suporte a MP3 com bitrate variável (VBR):** O sistema processa correctamente ficheiros MP3 com bitrate variável sem falhas na análise.

### Could have

- RF15 — **Visualização 3D do espectrograma:** Representação tridimensional e interactiva do espectrograma utilizando Three.js.
- RF16 — **Limpeza automática de áudio:** Redução de ruído e normalização do sinal via `noisereduce`, com possibilidade de download do áudio tratado.
- RF17 — **Ferramenta de selecção por região (marquee tool):** O utilizador pode seleccionar uma região específica no espectrograma por tempo e frequência para análise localizada.
- RF18 — **Histórico de sessão:** A interface mantém um histórico dos ficheiros analisados durante a sessão actual.
- RF19 — **Tooltips explicativos:** Cada tipo de evento anotado disponibiliza um tooltip com explicação acessível ao utilizador.

### Won't have (nesta versão)

- RF20 — **Autenticação e contas persistentes:** Fora do âmbito do MVP; introduziria complexidade de backend desnecessária nesta fase.
- RF21 — **Processamento em tempo real (streaming ao vivo):** Requer arquitectura de baixa latência não prevista na stack actual.
- RF22 — **Suporte a formatos adicionais (FLAC, AIFF, OGG):** O MVP limita-se a WAV e MP3; outros formatos serão considerados em versões futuras.
- RF23 — **Transcrição de fala (speech-to-text):** Funcionalidade distinta com requisitos de modelos de ML específicos, fora do âmbito deste projecto.
- RF24 — **API pública para integração com terceiros:** Não previsto nesta versão; poderá ser considerado após consolidação do MVP.

---

## Requisitos não-funcionais

<!-- Como o sistema se comporta: performance, segurança, usabilidade, escalabilidade. -->

### Must have

- RNF01 — **Performance:** O sistema conclui a análise e apresenta o espectrograma anotado em menos de 10 segundos para ficheiros até 10 MB, em condições normais de utilização.
- RNF02 — **Segurança:** Os ficheiros de áudio carregados são validados no backend antes de qualquer processamento; ficheiros inválidos ou com formato não suportado são rejeitados sem expor detalhes internos do servidor.
- RNF03 — **Usabilidade:** A interface é utilizável sem formação prévia por utilizadores do perfil alvo (estudantes, jornalistas, criadores de conteúdo), completando o fluxo principal sem necessidade de documentação.

### Should have

- RNF04 — **Escalabilidade:** A arquitectura Flask permite configuração futura com workers concorrentes (ex.: Gunicorn) para suportar múltiplos pedidos simultâneos sem refactoring major.
- RNF05 — **Manutenibilidade:** Os módulos de processamento de áudio dispõem de testes unitários cobrindo os casos principais de deteção (silêncio, clipping, ruído, eventos).

### Could have

- RNF06 — **Suporte multilingue:** A interface e os textos de feedback automático poderão ser disponibilizados em inglês, além do português, numa versão futura.

---

## Histórico de alterações

| Versão | Data | Alteração | Razão |
|--------|------|-----------|-------|
| 1.0 | Abril 2026 | Versão inicial | Proposta de projecto (semanas 3–4) |
| | | | |
