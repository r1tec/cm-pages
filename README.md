# Contem Magia Pages

**Para publicar, digite no terminal (dentro desta pasta):** `./publicar.sh`

Páginas de venda estáticas da Escola Contém Magia. Cada pasta é uma rota.

```
coe/index.html   ->  /coe   Manual de Como Ouvir Suas Entidades
```

Cada `index.html` é autocontido: HTML, CSS, JS e imagens no mesmo arquivo. Não
depende de framework, CDN nem build. Basta servir a pasta.

## Publicar

**Hospedagem com painel (cPanel, TurboCloud e similares)**
Envie a pasta `coe` para dentro de `public_html`. A página responde em
`seudominio.com.br/coe`.

**Netlify, Cloudflare Pages, Vercel**
Aponte o serviço para a raiz deste repositório. As pastas viram rotas
automaticamente.

**Deploy por FTP a cada push**
Use o workflow em `.github/workflows/deploy-ftp.yml` e cadastre em
Settings > Secrets and variables > Actions:

- `FTP_SERVER` (ex: ftp.seudominio.com.br)
- `FTP_USERNAME`
- `FTP_PASSWORD`
- `FTP_DIR` (ex: /public_html/)

## Regras da página COE

- Botão de compra: `https://pay.contemmagia.com.br/c/coe`, texto sempre
  `QUERO OUVIR MEUS GUIAS`
- A aula ao vivo nunca é descrita como recorrente. Sempre "a próxima terça"
- O aviso de que a prática caminha ao lado do acompanhamento médico e
  psicológico aparece no FAQ e no rodapé, e não sai
- Nenhum preço antes da dobra da oferta
