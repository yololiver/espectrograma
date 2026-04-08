# Projeto Final em Engenharia Informática

## Espectrograma  
### Análise e Interpretação de Áudio para Utilizadores Não Especialistas

**Paulo Silva - 2100537**  
**Pedro Pestana**  
**25-03-2026**

---

## Sinopse

Ferramentas de análise de áudio, como o Audacity, permitem visualizar sinais sonoros, mas exigem conhecimento técnico para interpretar espectrogramas, ruído de fundo e distorções. Utilizadores não especialistas — como estudantes, criadores de conteúdo ou jornalistas — enfrentam dificuldades em compreender o que está a acontecer num áudio e em identificar problemas ou eventos relevantes.

Propõe-se, neste projeto, o desenvolvimento de uma aplicação web para análise e interpretação de áudio em linguagem simples. O sistema irá identificar características relevantes do sinal — como silêncio, distorção, ruído e eventos sonoros — e apresentá-las de forma visual e acessível, recorrendo a um espectrograma anotado e a descrições compreensíveis para utilizadores sem formação técnica.

Espera-se obter uma ferramenta funcional que permita explorar e compreender áudio de forma rápida e intuitiva. O sistema deverá identificar e destacar eventos relevantes, apresentar feedback em linguagem simples e permitir a navegação por segmentos do áudio. O sucesso do projeto será avaliado pela implementação do MVP definido e pela capacidade do sistema de produzir resultados claros, úteis e interpretáveis para o utilizador final.

---

## MVP — Funcionalidades e critérios de aceitação

### 1. Upload de ficheiro de áudio

O utilizador pode carregar um ficheiro de áudio para análise.

**Critérios de aceitação:**

- Dado um ficheiro válido (WAV ou MP3 até 10 MB), o sistema realiza o upload e inicia a análise  
- Dado um ficheiro inválido, o sistema apresenta uma mensagem de erro clara sem falhas  

---

### 2. Visualização do espectrograma

O sistema apresenta o espectrograma do áudio carregado.

**Critérios de aceitação:**

- O espectrograma é apresentado após o upload  
- O utilizador consegue visualizar tempo (eixo X) e frequência (eixo Y)  
- O espectrograma corresponde ao conteúdo do áudio (validação manual)  

---

### 3. Deteção de silêncio

Identificação automática de segmentos silenciosos.

**Critérios de aceitação:**

- O sistema identifica pelo menos 80% dos segmentos silenciosos num áudio de teste  
- Os segmentos são apresentados com timestamps (ex.: 0:10–0:15)  

---

### 4. Deteção de clipping (distorção)

Identificação de picos de sinal que causam distorção.

**Critérios de aceitação:**

- O sistema identifica corretamente picos de clipping e apresenta os respetivos timestamps  
- Caso não exista clipping, o sistema apresenta “Sem distorção detectada”  

---

### 5. Análise de ruído de fundo

Estimativa da presença de ruído contínuo no áudio.

**Critérios de aceitação:**

- O sistema classifica o ruído como “baixo”, “moderado” ou “alto”  
- O resultado é apresentado sem métricas técnicas  

---

### 6. Deteção de eventos sonoros relevantes

Identificação de eventos sonoros relevantes definidos como:

- Variações abruptas de energia (aumentos súbitos de volume)  
- Mudanças significativas no espectro de frequência  
- Sons transitórios (ex.: batidas, cliques, impactos)  

A deteção é baseada em métricas simples como energia do sinal e variação espectral entre frames consecutivos.

**Critérios de aceitação:**

- O sistema identifica eventos relevantes com base em mudanças de energia ou frequência  
- Os eventos são apresentados com timestamps  
- O sistema detecta pelo menos 70% dos eventos num áudio de teste  

---

### 7. Anotação visual de eventos

Representação visual dos diferentes tipos de eventos no espectrograma e/ou no timeline.

**Critérios de aceitação:**

- O sistema apresenta pelo menos 3 tipos de eventos:
  - ruído de fundo  
  - clipping  
  - eventos sonoros  
- Cada tipo é representado com cor distinta  
- O utilizador consegue distinguir visualmente os tipos sem conhecimento técnico  

---

### 8. Feedback automático em linguagem simples

Geração de um resumo textual sobre a qualidade do áudio.

**Critérios de aceitação:**

- O sistema apresenta pelo menos 3 observações relevantes sobre o áudio  
- O texto não contém termos técnicos (ex.: “FFT”, “RMS”)  

**Exemplo:**

- “O áudio apresenta ruído de fundo leve”  
- “Existem picos de distorção em alguns momentos”  

---

### 9. Interface simples e utilizável

Interface web intuitiva e acessível.

**Critérios de aceitação:**

- Um utilizador sem experiência consegue completar o fluxo (upload + análise + interpretação)  
- A interface não apresenta erros visuais críticos  

---

### 10. Funcionalidades futuras (Nice to Have)

- Visualização 3D do espectrograma  
- Limpeza automática de áudio (redução de ruído e normalização)  
- Seleção avançada por tempo e frequência (marquee tool completa)  

---

## Calendário

O calendário segue o template do guia da unidade curricular, adaptado às necessidades do projecto.

### Sem. 1–2 (17–28 mar)
- Definição da proposta (sinopse, MVP, stack, calendário)  
- Submissão da proposta  

### Sem. 3–4 (31 mar–11 abr)
- Levantamento de requisitos (MoSCoW)  
- Definição da arquitectura (C4 nível 1 e 2)  
- Modelo de dados preliminar  
- Setup do repositório (estrutura + documentação inicial)  

### Sem. 5–6 (14–25 abr)
- Criação de wireframes da interface  
- Definição das principais decisões de arquitectura (ADRs)  
- Implementação inicial:
  - Upload de áudio  
  - Geração de espectrograma 2D  

### Sem. 7 (28 abr–2 mai)
- Continuação da implementação do núcleo  
- Demo interna:
  - Upload + espectrograma funcional  
  - Primeiras versões de deteção (silêncio/clipping)  

### Sem. 8 (5–6 mai)
- Submissão do relatório intercalar  
- Documentação completa de:
  - Introdução  
  - Desenho do sistema  

### Sem. 9–10 (7–16 mai)
- Implementação das funcionalidades principais:
  - Deteção de silêncio  
  - Deteção de clipping  
  - Análise de ruído  
  - Deteção de eventos  

### Sem. 11–12 (19–30 mai)
- Implementação de:
  - Anotação visual no espectrograma  
  - Feedback automático em linguagem simples  
- Testes iniciais (unitários e integração)  

### Sem. 13 (2–6 jun)
- Integração completa do sistema  
- Validação dos critérios de aceitação  
- Melhorias de interface  

### Sem. 14 (9–13 jun)
- Testes finais (funcionalidade e desempenho)  
- Capturas de ecrã e exemplos para relatório  
- Redação dos capítulos finais  

### Sem. 15 (16–20 jun)
- Preparação da defesa  
- Revisão do relatório  
- Simulação de perguntas  

### Sem. 16 (24 jun)
- Submissão final do relatório  
- Entrega do código e demo  

---

## Stack tecnológica

O sistema segue uma arquitetura em camadas, separando a interface do utilizador, a lógica de backend e o processamento de áudio.

O frontend é responsável pela interação e visualização dos dados, incluindo representações 2D. O backend, implementado em Flask, funciona como camada intermédia que gere pedidos HTTP, processamento de ficheiros e comunicação entre frontend e módulos de análise. O processamento de áudio é realizado em Python com recurso a bibliotecas científicas como librosa e numpy.

### Frontend

- React (Vite)  
- Three.js  
- Web Audio API  
- Canvas API  

### Backend

- Flask  
- Python  

### Processamento

- librosa  
- numpy  
- scipy  
- pydub  
- noisereduce  