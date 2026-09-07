# Plano — Barras de progresso dinâmicas (ECM-26-v2)

Página: `ecm-26-v2/index.html`. Objetivo: as barras de ocupação deixarem de ser número fixo e
passarem a refletir os ingressos vendidos no Supabase, com teto que muda a cada semana.

## Realidade do banco (levantada em 07/09/2026)
- Tabela: `public.transactions`.
- Funil ECM-26: `funnel_id = c3aa74f5-ce41-4aac-83f0-68d09e21819e`.
- Produto principal (único do funil): `product_id = 190c9801-598f-432c-b010-153b5555d5ae`
  (`offer_product_name = 'ECM - Celebração Contém Magia'`).
- Duas ofertas do MESMO produto:
  - Semente → `offer_type = 'ENTRY'` — pagos: **75**
  - Raiz → `offer_type = 'TRANSACTION'` — pagos: **17**
- **Não há orderbump em produto separado neste funil** — "eliminar orderbump" hoje é no-op,
  mas a regra fica cravada: contar só `product_id = 190c9801…`.
- Pagos totais: **92** · clientes distintos: **74** · reembolsos: **0**.
- Status presentes: `paid`, `refused`, `expired`, `waiting`.

## ✅ Regra de contagem (decidida pelo dono, 07/09/2026)
- **Vendido** = `product_id = 190c9801…` (produto principal), Semente **+** Raiz,
  `transaction_status = 'paid'`, sem reembolso, **1 por transação**. → hoje = **92**.
- **Card Raiz** ("Restam X de 30") → **dinâmico**: `30 − pagos_raiz` (hoje = 13).
- Sem `waiting`/pendente na conta.

SQL de contagem (referência do build):
```sql
select
  count(*) filter (where offer_type in ('ENTRY','TRANSACTION')) as vendidos,
  count(*) filter (where offer_type = 'TRANSACTION')            as raiz_pagos
from public.transactions
where funnel_id = 'c3aa74f5-ce41-4aac-83f0-68d09e21819e'
  and product_id = '190c9801-598f-432c-b010-153b5555d5ae'
  and transaction_status = 'paid'
  and coalesce(refunded_amount_cents,0) = 0;
```

## Tetos por semana (alinhados às datas do contador)
| até | teto |
|---|---|
| 10/09 | 130 |
| 17/09 | 140 |
| 24/09 | 150 |
| 01/10 | 160 |
| 08/10 | 170 |
% preenchida = vendidos ÷ teto da semana vigente (mesma lógica de data do contador já na página).

## Arquitetura (a página é estática; precisa de uma fonte)
Opção recomendada: **edge function pública** (padrão `*-public` já existe no projeto, ex.
`get-checkout-offer-public`), `verify_jwt=false`, que roda a contagem e devolve JSON enxuto
`{ vendidos, teto, pct, raizRestantes }`. A página busca no carregamento e anima as barras.
- Sem PII no retorno (só números) → seguro para chave anon.
- Fallback: se a chamada falhar, a barra mantém o valor atual embutido (nada quebra, sem buraco visual).
- Para não pesar o banco a cada visita: contagem cacheada (cabeçalho de cache curto na função, ou
  valor materializado por cron). Detalhar no build.

Opção B (mais leve, não ao vivo): assar o número no publish (`publicar.sh` consulta e injeta).
Atualiza só quando republica. Fica registrada como alternativa.

## Builds (um a um, cada um com ACEITE)

### Build 1 — Endpoint público de contagem
- **Tem que fazer**: função pública devolve `{ vendidos, teto, pct, raizRestantes }` para a data de
  hoje, aplicando a regra aprovada na Decisão; teto escolhido pela data vigente.
- **Não pode acontecer**: vazar dado de cliente; devolver contagem de outro funil/produto; query
  pesada sem cache; retorno que quebre se a tabela crescer.

### Build 2 — Página consome o endpoint
- **Tem que fazer**: barra do hero e card Semente usam `pct` real; card Raiz usa `raizRestantes`;
  frase "X% das vagas preenchidas" idem. Fallback para o valor fixo atual se a chamada falhar.
- **Não pode acontecer**: página travar/piscar esperando a resposta; barra passar de 100%;
  perder o comportamento de "encerrado" (barras somem depois de 08/10, já implementado).

### Build 3 — Revisão de performance (pedido do dono)
- **Tem que fazer**: medir no PageSpeed a página com a chamada nova; conferir que a alteração
  anterior (datas + contador + min/seg) segue intacta; garantir zero regressão de nota.
- **Não pode acontecer**: nota de performance cair; a chamada bloquear a renderização;
  layout shift pela barra chegando depois.

## Estado atual (pendente de publicar)
Já aplicado na página, ainda NÃO no ar: datas semanais + contador que reseta + "inscrições
encerradas" após 08/10 + "Este valor termina em" + frase dinâmica + MIN/SEG abreviados.
Este plano das barras entra por cima disso.
