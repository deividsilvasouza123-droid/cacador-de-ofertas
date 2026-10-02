# Caçador de Ofertas — Automação de Conteúdo

Sistema-base para transformar a operação do Caçador de Ofertas em um ciclo:

**produtos → seleção → roteiros → vídeo → Metricool → métricas → aprendizado → próximos roteiros**

## O que já está preparado

- Base com 100 produtos da Shopee.
- Ranking automático por combinação de vendas, comissão e preço.
- Geração de roteiros com 5 ângulos por produto.
- Versão Google Flow e versão YT CREAT.
- Fallback local: funciona sem API de IA usando templates.
- Integração preparada para a API do Metricool.
- Registro de desempenho em CSV.
- Análise semanal para extrair padrões de hook/ângulo.
- GitHub Actions para rodar automaticamente.

## O que ainda exige credenciais/configuração

O GitHub connector conectado ao ChatGPT não expõe criação de repositório nesta sessão. Por isso este pacote é **GitHub-ready**, mas não foi publicado em um repositório automaticamente.

Para automação completa, configure os Secrets do GitHub:

- `OPENAI_API_KEY` — opcional para geração dinâmica com IA.
- `OPENAI_MODEL` — opcional; padrão sugerido: `gpt-6-luna`.
- `METRICOOL_TOKEN` — token REST API do Metricool.
- `METRICOOL_USER_ID` — seu userId no Metricool.
- `METRICOOL_BLOG_ID` — ID da marca/perfil no Metricool.
- `METRICOOL_CREATOR_EMAIL` — e-mail usado como criador.
- `METRICOOL_AUTO_PUBLISH` — `true` para publicação direta; `false` para deixar pendente.
- `MEDIA_URL_TEMPLATE` — opcional, por exemplo `https://cdn.seudominio.com/videos/{item_id}.mp4`.

## Importante sobre vídeo

O GitHub Actions consegue gerar os roteiros e chamar a API do Metricool, mas não cria sozinho os arquivos de vídeo do Google Flow/YC CREAT. O vídeo precisa existir em um local acessível pela API (ou ser anexado por outro processo). A variável `MEDIA_URL_TEMPLATE` permite ligar esse armazenamento ao agendador.

## Fluxo automático

### Todos os dias — 03:00 (America/Sao_Paulo)

1. Lê `data/produtos.csv`.
2. Seleciona os melhores produtos ainda não processados.
3. Gera 5 ângulos de roteiro por produto.
4. Salva os roteiros em `output/roteiros/`.
5. Quando configurado, agenda no Metricool para Instagram, TikTok e YouTube.
6. Registra a operação.

### Toda semana — domingo 23:00

1. Lê `data/desempenho.csv`.
2. Calcula médias por hook, ângulo e categoria.
3. Produz `output/metricas/recomendacoes.json`.
4. As recomendações passam a orientar a próxima geração de roteiros.

## Como cadastrar métricas

Preencha `data/desempenho.csv` com uma linha por publicação:

`data,product_id,product_name,network,hook,angle,views,likes,comments,shares,saves,profile_visits,outbound_clicks,conversions,revenue`

O analisador usa esses dados para indicar quais estruturas devem ser testadas mais vezes.

## Segurança

Nunca coloque tokens no código. Use GitHub Secrets. O token do Metricool deve ficar no backend/runner e não em JavaScript de navegador.

## Como colocar no GitHub

Crie um repositório vazio, copie os arquivos deste pacote e faça o primeiro push. Depois configure os Secrets e habilite Actions.

Exemplo:

```bash
git init
git add .
git commit -m "chore: estrutura inicial do cacador de ofertas"
git branch -M main
git remote add origin SEU_REPOSITORIO
 git push -u origin main
```

## Primeira execução manual

Depois de configurar os Secrets, execute o workflow **Daily Content Engine** manualmente antes de deixar o cron rodar sozinho.
