Janela revisada: 9e476c6..36e3257
Revisado até: 36e325787454aff98419fb86f516294f8863daf7

# Revisão de design — Formação Saberes Ancestrais

Veredito da revisão inicial: **precisa de correções visuais antes da aprovação de design**. Cinco achados confirmados: um alto, três médios e um baixo. Execução e validação das correções registradas no fim deste documento.

Escopo: publicação em https://contemmagia.com.br/fsa/, exportação original `Formacao Saberes Ancestrais - Pagina de Vendas v2.html`, capturas fornecidas pelo usuário e alterações da conversão. Inclui problemas mobile herdados da exportação, conforme pedido expresso. Lentes: comparação controlada de tipografia e hero; revisão independente de mobile; revisão independente de fidelidade/contrato da conversão. Nenhuma correção, build ou publicação foi feita nesta revisão.

## Achados

### FSA-01 — Alto — Apresentação e primeiro botão ficam abaixo da primeira tela no celular
- Evidência: em 390×844, o hero tem aproximadamente 1171px; o primeiro CTA começa em y=1119,8 e termina em 1175,8. A fotografia ocupa o espaço anterior ao texto.
- Origem: spacer mobile com `min-height:52vh` e `flex-wrap:wrap-reverse`, herdado do template em `fsa/index.html:381`; a adaptação mantém a foto em `52vh` em `scripts/preparar-fsa.py:57`.
- Consequência: a primeira tela não entrega apresentação e ação completas, contrariando a orientação de primeira dobra de `_padroes/prompt-claude-design.md`.
- Correção mínima: recompor o hero mobile, reduzindo/removendo o spacer e integrando a foto sem empurrar título, apoio e botão; preservar legibilidade e enquadramento. Custo médio; validar também celulares baixos e texto ampliado.
- Evidência visual: `/tmp/fsa-sec-0.png` e `/tmp/fsa-review-public-390.png`.

### FSA-02 — Médio — Borda vertical visível na fotografia do hero desktop
- Evidência: o início da imagem está em x=648 no viewport de 1440px e x=733,5 em 1630px, sempre 45% da janela; corresponde à faixa indicada pelo usuário.
- Origem: `scripts/preparar-fsa.py:54` restringe a camada a 55% da largura. O gradiente original não fica totalmente opaco na nova borda, expondo uma mudança abrupta de cor.
- Consequência: a foto perde a integração suave com o fundo presente na referência. É uma regressão introduzida pelo ajuste de enquadramento da publicação.
- Correção mínima: refazer a mistura com o fundo, garantindo opacidade completa na borda ou uma máscara contínua; preservar mãos/vela no recorte. Custo baixo; testar várias larguras, não apenas uma captura.
- Evidência visual: `/tmp/fsa-review-public-1440.png` e `/tmp/fsa-review-public-1630.png`.

### FSA-03 — Médio — Animação remove temporariamente o escurecimento necessário à leitura
- Evidência: em “03b Virada” e “08 Pilares”, a entrada em 390×844 deixa o overlay com `opacity:0` e `translateY(34px) scale(.98)`, enquanto o título já está visível; a foto pode estar carregada durante a transição.
- Origem: `estatico.py:172` marca o primeiro `div` indiscriminadamente, incluindo camadas decorativas `aria-hidden="true"`; `estatico.py:50` aplica a ocultação e o movimento.
- Consequência: o contraste muda durante a leitura e aparecem bordas da fotografia durante a animação. O original mantém essas camadas fixas.
- Correção mínima: excluir overlays decorativos da seleção de animação e selecionar explicitamente conteúdo. Custo baixo; a função é compartilhada e exige conferir os outros consumidores afetados.

### FSA-04 — Baixo — Divisão desktop entre texto e fotografia difere da original
- Evidência: em “Você sente mas não sabe interpretar”, a coluna de texto original/publicada mede 511/482,39px em 900px; 586/556,80px em 1024px; 720/691,19px em 1440px.
- Origem: `scripts/preparar-fsa.py:31` remove `sizeB4()` e a linha 65 define `3fr 2fr`, calculando a proporção após descontar o gap de 48px.
- Consequência: mudam as quebras de texto e o recorte da foto; aos 900px também aumenta a altura do bloco.
- Correção mínima: reproduzir a divisão original em CSS, por exemplo `minmax(0,60%) minmax(0,1fr)`, validando o breakpoint e o limite do container. Custo baixo; não requer reintroduzir React.

### FSA-05 — Médio — Atalho “Religião” deixa o título encoberto pelo menu mobile
- Evidência: em 390×844, após clicar e aguardar a rolagem, o título do FAQ começa em y=60,34px, enquanto o menu fixo termina em y=77px; aproximadamente 17px ficam encobertos.
- Origem: `scripts/preparar-fsa.py:57` amplia o menu para duas linhas, mas `#religiao` conserva `scroll-margin-top:60px` em `fsa/index.html:381`, compatível apenas com o menu original de 56px.
- Consequência: o visitante chega a um título parcialmente escondido ao usar a navegação.
- Correção mínima: ajustar a margem dos destinos à altura mobile do menu, com respiro, e testar as quatro âncoras. Custo baixo; considerar variações de altura com texto ampliado.

## Fonte e percepção de escala

Não foi comprovada redução global de fonte na publicação. Na comparação controlada, original e publicada usam o mesmo H1 de 72px, peso 800, line-height 70,56px e caixa de 576px em larguras de 1440 e 1630px. O Chrome confirmou a mesma fonte efetiva `RobotoCondensed-ExtraBold`. Em 390px, ambos usam H1 de 42,75px e line-height de 41,895px. O apoio também coincide: 16px no desktop e 15,21px no mobile. As alturas das 20 seções em 1440×1000 coincidiram antes de interação.

Isso não invalida a diferença percebida nas capturas: falta uma comparação do editor original e da publicação com a mesma área útil e escala. Não há evidência suficiente para atribuir a causa ao zoom, nem para aplicar 110% globalmente. A alteração de proporção descrita em FSA-04 é real e separada desse diagnóstico.

## Cobertura e limites

- Comparação de original/publicado em 1440×1000, 1630×1000 e 390×1000, com DPR 1, fontes carregadas e medidas CSS efetivas.
- Inspeção das 20 seções no mobile e comparação das dimensões desktop; análise da conversão, cópia, preços, nove perguntas/respostas, fontes e tratamento das imagens.
- Sem overflow horizontal de títulos, parágrafos, listas, CTAs e FAQ nas larguras 320, 360, 390, 430, 899 e 900px. Os nove FAQs abriram por clique e suas respostas não transbordaram em 390px. Atalhos conferidos; defeito específico em FSA-05. Botões principais com 56px de altura.
- O primeiro botão permanece abaixo da primeira tela em todas as larguras mobile medidas com altura 844px: y=1193 em 320px, 1132 em 360px, 1120 em 390px e 1158 em 430px.
- Cópia e preços preservados; FAQ nativo mantém as nove perguntas e respostas. Ajustes de magenta têm finalidade de contraste e não foram classificados como defeito sem evidência adicional.
- A exportação local tenta carregar imagens `img/bg.jpg` e variantes inexistentes no arquivo fornecido. Por isso, a fotografia original tem como referência visual as capturas do usuário, além da análise do template, e não uma comparação pixel a pixel com imagens quebradas.
- Sem compra, envio de formulário ou teste de conversão real. Sem nova medição PageSpeed nesta revisão de design; os resultados anteriores não demonstram ausência dos defeitos acima.

## Aceitação para a correção

1. Hero desktop sem emenda aparente, com recorte e mistura compatíveis com a referência em larguras diferentes.
2. Hero mobile com título, apoio e ação acessíveis imediatamente nos tamanhos usuais, sem sobreposição nem redução excessiva de fonte; conteúdo continua acessível com texto ampliado.
3. Camadas de contraste permanecem estáveis durante toda a entrada das seções.
4. Proporções desktop corrigidas e nova passagem visual pelas 20 seções, inclusive nos limites dos breakpoints.
5. Após as correções: validar atalhos, FAQ, links e parâmetros de checkout, pixels e ausência de chat; publicar conforme autorização aplicável e medir novamente desempenho mobile/desktop, com meta de pelo menos 90.

## Execução das correções autorizadas

O dono autorizou expressamente corrigir e publicar, sem nova confirmação entre etapas. As cinco correções foram implementadas separadamente na branch `fix/fsa-design-review`, preservando os arquivos locais alheios. Original de Downloads intacto. Backup do build anterior: `/tmp/fsa-before-design-fixes-36e3257.tar.gz`.

- **FSA-01 — CONFIRMADO — `8796ed2`:** removido o spacer mobile e recomposta a imagem como fundo, preservando fonte e copy. Chrome com altura 844px: botão inteiro termina em y=746,59 (320px), 672,91 (390px), 709,69 (430px) e 719,67 (899px); nenhum overflow. Captura `/tmp/fsa-fixed-01-390.png`.
- **FSA-02 — CONFIRMADO — `707f1be`:** máscara gradual na borda da fotografia desktop. Conferida em 900, 1440 e 1630px; transição visual contínua, sem a emenda anterior. Captura `/tmp/fsa-fixed-02-1440.png`.
- **FSA-03 — CONFIRMADO — `8afa6d7`:** animação não atua quando o primeiro container é decorativo. Nas duas seções, entrada real em Chrome mantém overlay com opacidade 1 e transformação `none`; zero elementos decorativos marcados para animação. Caso de conteúdo comum da função compartilhada continua recebendo animação.
- **FSA-04 — CONFIRMADO — `d5dd228`:** coluna de texto novamente com 60% da largura original. Medidas texto/foto: 511,188/292,812px em 900px; 585,594/342,406px em 1024px; 720/432px em 1440px.
- **FSA-05 — CONFIRMADO — `dfc61d3`:** destinos mobile com margem de 6rem. Cliques nos quatro atalhos em 320, 390 e 430px deixam os títulos abaixo do menu de 77px; título do FAQ em aproximadamente 96px.

Verificação de sintaxe Python e `git diff --check` passaram. `verificar.py fsa /tmp/fsa-design-build` saiu com código 0: imagens no tamanho adequado e contraste aprovado. Este projeto não possui typecheck TypeScript; o código alterado é Python/CSS/template e foi validado pelo build e pelo navegador.

Revisão independente do diff `36e3257..dfc61d3`: limpa, sem regressões concretas. A lente conferiu template, copy, fontes, checkout e medidas em Chrome, além das capturas 320px/1440px.

### Estabilidade da primeira dobra após publicar

A primeira publicação das correções revelou um problema adicional de FSA-01 em rede lenta: a troca tardia das fontes deslocava o título, apoio e botão. PageSpeed móvel retornou 84 (LCP 3,2s; CLS 0,166; TBT 110ms) e a coleta detalhada seguinte retornou 87 (LCP 3,5s; CLS 0; TBT 0). Desktop: 96. Esses resultados não foram aceitos como entrega.

**Complemento FSA-01 — `f138c44`:** subconjuntos WOFF2 das fontes originais, gerados de todo o texto visível e das nove respostas, incorporados ao HTML; preload das três famílias usadas na abertura. Métricas e eixos preservados, mantendo recursos padrão de composição e fontes Latin-ext originais. Só incorporar os dados ainda permitia deslocamento no Lighthouse; antecipar a decodificação completou a correção.

Provas: atraso artificial de fontes reproduziu deslocamentos somados de aproximadamente 0,171 na versão anterior; versão incorporada não apresentou deslocamentos nesse cenário. Lighthouse local final: 93 mobile, LCP 2,9s, FCP 2,3s, TBT 0, CLS 0. Comparação antes/depois de 182 títulos, parágrafos, listas e perguntas em 390px e 1440px: texto, fonte, tamanho e dimensões idênticos. FAQs, imagens e links passaram novamente. A verificação do complemento de fontes foi feita pela raiz, sem alegar nova revisão independente.

Checkpoint após correções: f138c44

### Encerramento

**Corrigidos e publicados os cinco achados.** Publicação final pelo `./publicar.sh fsa`, conferência de imagens/contraste aprovada e cache de página, assets e campanhas invalidado. O espelho de hospedagem adicional estava desabilitado na configuração vigente; nenhuma mudança de domínio foi feita.

PageSpeed público da versão `f138c44`, URL https://contemmagia.com.br/fsa/:

| Dispositivo | Coleta UTC em 10/09/2026 | Desempenho | LCP | TBT | CLS |
| --- | --- | --- | --- | --- | --- |
| Celular | 23:03:35.812 | **97** | 2,3s | 0ms | **0** |
| Desktop | 23:03:35.028 | **97** | 0,8s | 0ms | **0** |

Evidências completas: `/tmp/fsa-psi-mobile-detail.json` e `/tmp/fsa-psi-desktop-detail.json`. A meta de pelo menos 90 foi cumprida nos dois dispositivos. Não é garantia de nota constante nem de atualização imediata do histórico de Core Web Vitals.

Testes públicos em 390px e 1440px: nove imagens carregadas, nove respostas do FAQ abrindo/fechando, sete links de checkout com UTM e oferta alternativa preservada, sem chat, sem overflow horizontal e sem erros JavaScript. Os quatro tamanhos mobile confirmaram a primeira dobra corrigida no domínio público. GTM conferido por tempo e por interação: uma instância, os dois IDs de pixel preservados. O teste confirmou inicialização; não comprovou recebimento de PageView no painel Meta, nem realizou compras ou conversões reais.

Preview do Orca recarregado na URL publicada. Conhecimento incorporado ao procedimento canônico `.claude/skills/publicar/PUBLICACAO-DESEMPENHO.md` e às regras do FSA. Nenhum dos cinco achados ficou pendente. Permanecem fora da verificação: Safari/iOS físico, compra real e confirmação de eventos no painel Meta.
