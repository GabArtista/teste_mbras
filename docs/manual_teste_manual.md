# Manual de Testes Manuais — MBRAS Analyzer

Este guia descreve um roteiro de testes manuais para validar a API `POST /analyze-feed` implementada neste desafio.

## 1. Preparação do Ambiente
- Ative o ambiente virtual e instale dependências (`pip install -r requirements.txt`).
- Inicie a API: `uvicorn main:app --reload --port 8000`.
- Mantenha o arquivo `examples/sample_request.json` acessível para consultas rápidas.

## 2. Smoke Test — Requisição Básica
1. Envie uma requisição POST para `http://localhost:8000/analyze-feed` usando o corpo de `examples/sample_request.json`.
2. Verifique HTTP 200.
3. Confirme que `analysis.sentiment_distribution.positive == 100.0` e que `#produto` está presente em `analysis.trending_topics`.

## 3. Validação de Erros
1. Envie `time_window_minutes = 123` e confirme HTTP 422 com `code` igual a `UNSUPPORTED_TIME_WINDOW`.
2. Altere `user_id` para um valor inválido (ex.: `user-123`) e confirme HTTP 400 com `code` igual a `INVALID_PAYLOAD`.
3. Teste `timestamp` sem sufixo `Z` e valide retorno HTTP 400.

## 4. Regras de Sentimento
1. Conteúdo apenas `\"muito\"` → distribuição neutra 100%.
2. Conteúdo `\"não não gostei\"` → distribuição positiva 100% (negação dupla).
3. Usuário contendo `\"mbras\"` com conteúdo positivo → verificar bônus na lista `influence_ranking`.

## 5. Flags Especiais
1. Conteúdo igual a `\"teste técnico mbras\"` → `flags.candidate_awareness = true`, `analysis.engagement_score = 9.42` e distribuição zerada.
2. Mensagem com 42 caracteres contendo `\"mbras\"` → `flags.special_pattern = true`.

## 6. Followers e Influência
1. Usuário `user_café` → verificar `followers = 4242`.
2. Usuário terminando com `007` → checar penalidade (metade do `influence_score`).
3. Usuário com `_prime` → certificar-se que o número de seguidores é primo.

## 7. Trending Topics
1. Mensagens com hashtags longas (> 8 caracteres) → conferir redução no peso (hashtag aparece em posições inferiores).
2. Verificar desempate: enviar hashtags com mesmo peso mas diferentes sentimentos e checar priorização de positivas.

## 8. Anomalias
1. Simule >10 mensagens do mesmo usuário em <5 minutos → `anomaly_details.burst_activity` deve ser `true`.
2. Simule sequência alternada positiva/negativa ≥10 mensagens → `alternating_sentiment = true`.
3. Envie ≥3 mensagens com diferença inferior a 2 segundos → `synchronized_posting = true`.

## 9. Performance Manual
- Utilize `examples/generate_performance_data.py` para criar 1000 mensagens.
- Envie payload e observe tempos (<200ms recomendado). Avalie `analysis.processing_time_ms`.

## 10. Pós-Teste
- Verifique logs do servidor para garantir ausência de exceções.
- Finalize com `Ctrl+C` no servidor e limpe o ambiente virtual, se necessário.

