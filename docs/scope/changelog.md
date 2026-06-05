# Changelog

<!-- Uma entrada por semana, até domingo à noite. -->
<!-- Formato fixo: três linhas por entrada. Não elaborar além do necessário. -->
<!-- O changelog é verificado nas três entregas formais. -->

---

## Sem. 1 · 17–21 mar

**Feito:** [O que foi concluído esta semana]  
**Bloqueou:** [O que impediu progresso, ou "Nada"]
**Próxima semana:** [O que está planeado]

---

## Sem. 2 · 24–28 mar
**Feito:** 
Definição da proposta (sinopse, MVP, stack, calendário)
Submissão da proposta
**Bloqueou:**
Nada
**Próxima semana:**
Levantamento de requisitos (MoSCoW)  
Definição da arquitectura (C4 nível 1 e 2)  
Modelo de dados preliminar  
Setup do repositório (estrutura + documentação inicial)
---

## Sem. 3 · 31 mar–4 abr

**Feito:** 
Levantamento de requisitos (MoSCoW)  
Definição da arquitectura (C4 nível 1 e 2)  
**Bloqueou:**
Nada 
**Próxima semana:**
Modelo de dados preliminar
Setup do repositório (estrutura + documentação inicial)

---

## Sem. 4 · 7–11 abr

**Feito:**
Modelo de dados preliminar  
Setup do repositório (estrutura + documentação inicial)
Criação de wireframes da interface 
**Bloqueou:**
Nada
**Próxima semana:**
Finalização de wireframes da interface
Implementação inicial:
Upload de áudio  
Geração de espectrograma 2D 

---

## Sem. 5 · 14–17 abr

**Feito:**  
Finalização de wireframes da interface
Implementação inicial:
Upload de áudio  
Geração de espectrograma 2D 
**Bloqueou:**  
**Próxima semana:**
Continuação da implementação do núcleo e melhoria da vizualização do espectrograma
Demo interna:
Upload + espectrograma funcional  
Primeiras versões de deteção (silêncio/clipping)  


---

## Sem. 6 · 22–25 abr

**Feito:**  
Continuação da implementação do núcleo e melhoria da vizualização do espectrograma
Demo interna:
Upload + espectrograma funcional  
Primeiras versões de deteção (silêncio/clipping)  
**Bloqueou:**  
**Próxima semana:**
Submissão do relatório intercalar 
Documentação completa de: 
Introdução 
Desenho do sistema


---

## Sem. 7 · 28 abr–2 mai · DEMO INTERNA

**Feito:**  
Demo interna: upload, espectrograma, deteção de silêncio/clipping/ruído e eventos com filtros na UI  
Anotação visual com ≥ 5 tipos de eventos no espectrograma  
**Bloqueou:**  
Nada  
**Próxima semana:**  
Feedback automático (M08); relatório intercalar; diagramas C4

---

## Sem. 8 · 5–6 mai · INTERCALAR

**Feito:**  
Feedback em linguagem simples (≥ 3 observações, requisito M08)  
Refactor: `backend/services/` (análise + feedback); testes pytest de fumo  
Diagramas C4 e modelo de dados (`docs/architecture/*.svg`)  
Relatório intercalar (`docs/report/relatorio-intercalar.pdf`)  
README alinhado com stack real (Flask + Jinja2)  
**Bloqueou:**  
Nada  
**Próxima semana:**  
Indicador de progresso no upload; refinamento da UI; testes com áudios de referência

---

## Sem. 9 · 7–9 mai

**Feito:**  
Validação pós-intercalar; testes com ficheiros de referência WAV e MP3  
**Bloqueou:**  
Nada  
**Próxima semana:**  
Extensão da deteção com 3 novos tipos de evento (energia, espectro, transitório); botões de filtro por tipo na UI

---

## Sem. 10 · 12–16 mai

**Feito:**  
Extensão de `audio_analysis.py` com deteção de variação de energia, mudança espectral e transitórios (onset detection) — 5 tipos de evento no total  
Botões de filtro interativos no ecrã de análise (filtragem por tipo de evento com anotações no espectrograma)  
Relatório intercalar corrigido e submetido em `docs/report/`  
**Bloqueou:**  
Nada  
**Próxima semana:**  
Correção de compatibilidade Chrome; refinamento da lógica de filtros; dropdown colapsável de eventos

---

## Sem. 11 · 19–23 mai

**Feito:**  
Correção de representação visual no Chrome (rendering canvas)  
Lógica de filtros refatorada (estado correto ao activar/desactivar múltiplos filtros)  
Menu dropdown colapsável para listas de eventos no ecrã de análise  
**Bloqueou:**  
Nada  
**Próxima semana:**  
Vista 3D do espectrograma; otimização do render 2D; animação de fundo

---

## Sem. 12 · 26–30 mai

**Feito:**  
Investigação e prototipagem da vista 3D (Three.js + WebGL); planeamento da arquitectura de render  
**Bloqueou:**  
Nada  
**Próxima semana:**  
Implementação da vista 3D; Web Worker para renderização sem bloqueio; cache do espectrograma em sessionStorage

---

## Sem. 13 · 2–6 jun

**Feito:**  
Vista 3D do espectrograma com Three.js/WebGL (malha de barras, iluminação, controlos de órbita, HUD com navegação)  
Renderização do espectrograma 2D movida para Web Worker (ArrayBuffer transferável; elimina bloqueio da UI)  
Cache do espectrograma em `sessionStorage` com chave por ficheiro (evita re-render ao navegar para trás)  
Animação de notas musicais flutuantes no fundo (canvas fixo, adapta cores ao tema claro/escuro)  
Correção das cores do espectrograma (overlay de grayscale removido da vista por defeito; mantido apenas no modo de filtro)  
Remoção do painel de debug de escala de UI  
**Bloqueou:**  
Nada  
**Próxima semana:**  
Relatório final; polimento da UI; preparação da defesa

---

## Sem. 14 · 9–13 jun

**Feito:**  
**Bloqueou:**  
**Próxima semana:**

---

## Sem. 15 · 16–20 jun · PREP. DEFESA

**Feito:**  
**Bloqueou:**  
**Próxima semana:**

---

## Sem. 16 · 24 jun · ENTREGA FINAL

**Feito:**  
**Bloqueou:** —  
**Próxima semana:** — Defesa pública.
