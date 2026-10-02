# Configuração do robô

## 1. GitHub

Crie um repositório vazio e suba esta pasta.

## 2. Secrets obrigatórios

`METRICOOL_TOKEN`
`METRICOOL_USER_ID`
`METRICOOL_BLOG_ID`
`METRICOOL_CREATOR_EMAIL`
`METRICOOL_AUTO_PUBLISH`

Para geração dinâmica com IA:

`OPENAI_API_KEY`
`OPENAI_MODEL`

Para ligar vídeos:

`MEDIA_URL_TEMPLATE`

Exemplo de template:
`https://cdn.exemplo.com/cacador/{item_id}.mp4`

## 3. Modo de implantação recomendado

Primeiro use `METRICOOL_AUTO_PUBLISH=false` e rode o workflow manualmente. Confirme no Planner se os posts e os horários estão corretos. Depois mude para `true`.

## 4. Produto amarelo do TikTok Shop

Este robô não promete vincular automaticamente o produto amarelo. O vínculo depende do recurso/API disponível na conta e do método suportado pela plataforma. O fluxo foi desenhado para automatizar o restante sem inventar essa etapa.
