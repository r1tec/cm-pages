#!/usr/bin/env bash
# Afina uma pagina ATE a nota de performance que voce quer — sozinho.
#
# O ciclo (repetido ate a nota bater ou acabar o que da pra fazer com seguranca):
#   1. publica a pagina                (./publicar.sh <slug>)
#   2. mede no PageSpeed de verdade     (python3 medir.py <slug> --json)
#   3. se a nota ja bateu -> pronto
#   4. se ainda falta E o PageSpeed apontou imagem grande -> encolhe essa imagem
#      (mexe SO no reduzir.json, que e reversivel), e volta ao passo 1
#   5. se nao ha mais imagem grande p/ encolher -> para e explica o que sobrou
#      (em geral e peso de terceiro: GTM/Facebook/Cloudflare, que se resolve no
#       painel do Google, nao no codigo)
#
# So mexe em IMAGEM (seguro e reversivel). Nunca mexe em cor/contraste sozinho
# (isso e design: nasce certo no Claude Design). Nunca passa do numero de rodadas.
#
# Uso:
#   ./afinar.sh <slug> [nota_alvo=90] [max_rodadas=4]
#     ex: ./afinar.sh ecm-26-v2
#         ./afinar.sh ecm-26-v2 95 5

set -euo pipefail
cd "$(dirname "$0")"

SLUG="${1:-}"
ALVO="${2:-90}"
MAX="${3:-4}"

if [ -z "$SLUG" ] || [ ! -f "$SLUG/index.html" ]; then
  echo "uso: ./afinar.sh <slug> [nota_alvo] [max_rodadas]" >&2
  echo "  (a pasta <slug>/ precisa existir com index.html)" >&2
  exit 1
fi

CFG="$SLUG/reduzir.json"

for RODADA in $(seq 1 "$MAX"); do
  echo ""
  echo "======== AFINAR $SLUG · rodada $RODADA/$MAX (alvo: $ALVO) ========"

  ./publicar.sh "$SLUG"

  echo "Esperando o cache limpar antes de medir..."
  sleep 8

  # Mede no PageSpeed uma vez: o relatorio legivel sai na tela (stderr) e o
  # json (nota + imagens grandes) fica no stdout, que capturamos aqui.
  SAIDA="$(python3 medir.py "$SLUG" --json)"

  NOTA="$(printf '%s' "$SAIDA" | python3 -c 'import sys,json;print(json.load(sys.stdin)["score"])')"
  echo ">>> Nota nesta rodada: $NOTA/100 (alvo $ALVO)"

  if [ "$NOTA" -ge "$ALVO" ]; then
    echo ""
    echo "✓ Alvo atingido: $SLUG esta com $NOTA/100. Nada mais a fazer aqui."
    exit 0
  fi

  # Tenta aplicar as reducoes de imagem que o PageSpeed sugeriu, SO se mudarem algo
  MUDOU="$(printf '%s' "$SAIDA" | python3 - "$CFG" <<'PY'
import sys, json, os
cfg_path = sys.argv[1]
sug = json.load(sys.stdin).get("reduzir", {})
atual = {}
if os.path.isfile(cfg_path):
    try: atual = json.load(open(cfg_path, encoding="utf-8"))
    except Exception: atual = {}
mudou = False
for uu, wh in sug.items():
    # so aceita se for NOVA imagem ou um alvo MENOR que o ja configurado (encolher)
    if uu not in atual or int(wh[0]) < int(atual[uu][0]):
        atual[uu] = [int(wh[0]), int(wh[1])]
        mudou = True
if mudou:
    json.dump(atual, open(cfg_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    open(cfg_path, "a").write("\n")
print("SIM" if mudou else "NAO")
PY
)"

  if [ "$MUDOU" != "SIM" ]; then
    echo ""
    echo "Parei: a nota ($NOTA) ainda esta abaixo do alvo ($ALVO), mas nao ha mais"
    echo "imagem grande p/ encolher. O que sobra nao e do codigo da pagina — em"
    echo "geral e peso das tags de terceiros (Google Tag Manager, Facebook,"
    echo "Cloudflare). Isso se resolve no painel do Google, nao aqui."
    echo "Veja o relatorio acima (secao 'Peso que NAO e do nosso codigo')."
    exit 0
  fi

  echo "Ajustei o $CFG com as imagens que o PageSpeed apontou; republico e meco de novo."
done

echo ""
echo "Cheguei ao limite de $MAX rodadas. Rode 'python3 medir.py $SLUG' p/ ver onde parou."
