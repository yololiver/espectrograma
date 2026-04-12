# Gestão de Riscos

**Projecto:** Espectrograma — Análise e Interpretação de Áudio para Utilizadores Não Especialistas  
**Versão:** 1.0 · Abril 2026

---

## Tabela de riscos

<!-- Identificar 3 a 5 riscos reais ao projecto. -->
<!-- Probabilidade: Alta / Média / Baixa -->
<!-- Impacto: Alto / Médio / Baixo -->
<!-- Mitigação: o que se faz para reduzir probabilidade ou impacto -->

| ID | Risco | Probabilidade | Impacto | Mitigação |
|----|-------|--------------|---------|-----------|
| R01 | **Deriva de âmbito** — pressão para adicionar funcionalidades além do MVP (ex.: transcrição de fala, suporte a mais formatos, autenticação) durante o desenvolvimento | Média | Alto | MVP contratualizado com critérios de aceitação explícitos na proposta. Qualquer extensão requer aprovação prévia do orientador. Funcionalidades extra registadas como *Won't Have* no levantamento de requisitos. |
| R02 | **Complexidade da integração frontend/backend** — a serialização do espectrograma (matriz NumPy → base64 → Canvas) e a sincronização das anotações visuais com o timeline podem revelar-se mais complexas do que o previsto | Alta | Médio | Implementar e validar o pipeline de integração completo (upload → análise → renderização) nas semanas 5–6, antes de adicionar funcionalidades. Não deixar integração para a fase final. |
| R03 | **Precisão insuficiente da deteção automática** — os algoritmos baseados em energia e variação espectral (sem ML) podem não atingir os limiares definidos nos critérios de aceitação (≥ 80% silêncio, ≥ 70% eventos) em áudios reais e variados | Média | Alto | Testar com áudios de referência diversificados desde a semana 7. Ajustar limiares de deteção iterativamente. Documentar limitações conhecidas caso os critérios não sejam atingidos na totalidade. |
| R04 | **Calendário apertado na fase de implementação** — as semanas 9–12 concentram a maioria das funcionalidades do núcleo; qualquer atraso nas semanas anteriores propaga-se directamente para a entrega | Média | Alto | Seguir o calendário semanal com entregas internas definidas. Priorizar funcionalidades *Must Have* antes de qualquer *Should Have*. Identificar atraso na demo interna da semana 7 e ajustar âmbito se necessário. |
| R05 | **Desempenho insuficiente no processamento de áudio** — ficheiros próximos do limite (10 MB, ~10 min de áudio mono) podem exceder o tempo de resposta aceitável no servidor Flask em modo single-threaded | Baixa | Médio | Testar com ficheiros de tamanho máximo durante a semana 13. Se necessário, limitar a duração máxima do áudio ou configurar Gunicorn com workers assíncronos para processar pedidos sem bloquear a interface. |

---

## Histórico de actualização

| Data | Risco | Evento | Estado |
|------|-------|--------|--------|
| Abril 2026 | — | Identificação inicial dos riscos | Em monitorização |

