# ADR-001 — Player de Áudio Integrado na Página de Análise

**Data:** 2026-06-19
**Estado:** Aceite  
**Decisores:** Paulo Silva

---

## Contexto

A página de análise apresenta o espectrograma anotado do ficheiro carregado, com identificação visual de eventos sonoros (silêncio, clipping, transientes, etc.). No entanto, o utilizador não tinha forma de ouvir o áudio na própria página para confirmar se os eventos detetados correspondiam ao que era audível. Para validar os resultados, era obrigado a recorrer a uma ferramenta externa, o que quebra o fluxo de utilização e contradiz o objetivo de acessibilidade para não especialistas.

---

## Decisão

Adicionar um player de áudio minimalista diretamente na página de análise, composto por:

- Uma rota Flask `/audio` que serve o ficheiro da sessão atual via `send_file`, sem alterações ao pipeline de análise existente.
- Um elemento HTML5 `<audio>` com `preload="metadata"` para carregar apenas os metadados (duração) na abertura da página, sem transferir o ficheiro completo antecipadamente.
- Controlos implementados em JavaScript puro: botão de reprodução/pausa (▶/⏸), barra de progresso clicável e indicadores de tempo decorrido e duração total com larguras fixas para evitar deslocamento de layout.

O player é posicionado entre a legenda do espectrograma e os filtros de eventos, mantendo a hierarquia visual da página.

Não foram introduzidas novas dependências. A rota `/audio` reutiliza o helper `_get_uploaded_file_path()` já existente e o ficheiro servido é o mesmo que foi carregado e analisado na sessão.

---

## Alternativas consideradas

| Alternativa | Razão de rejeição |
|------------|------------------|
| Não adicionar player | O utilizador continuaria a necessitar de ferramentas externas para ouvir o áudio, dificultando a correlação entre o espectrograma e a perceção auditiva dos eventos detetados. |
| Incorporar o áudio como Base64 no HTML | Aumentaria o tamanho da página de forma proporcional ao ficheiro (até ~13 MB adicionais para ficheiros de 10 MB), com impacto direto no tempo de carregamento. |
| Player externo em iframe | Dependência de um serviço externo. Incompatível com a restrição arquitetural de processamento exclusivamente local e sem serviços de terceiros. |

---

## Consequências

**Positivas:**
- O utilizador pode ouvir o áudio e comparar diretamente com o espectrograma, melhorando a interpretação dos eventos detetados.
- Implementação sem novas dependências e sem alterações ao pipeline de análise.
- A rota `/audio` é consistente com as restantes rotas da aplicação e reutiliza mecanismos já existentes (sessão Flask, helper `_get_uploaded_file_path()`).

**Negativas / trade-offs:**
- A rota `/audio` não tem controlo de acesso — qualquer utilizador com acesso ao servidor pode descarregar o ficheiro enquanto a sessão estiver ativa. Aceitável no contexto de protótipo sem autenticação.
- O ficheiro é eliminado na rota `/reset`, pelo que o player deixa de funcionar após essa ação. Comportamento esperado e consistente com a ausência de persistência entre sessões.

---

*Para criar um novo ADR: copiar este ficheiro, incrementar o número, preencher e actualizar o estado.*
