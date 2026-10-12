# ViceScope — instruções para agentes

## Objetivo

O ViceScope produz Shorts em inglês sobre GTA VI com custo adicional zero, revisão factual e aprovação humana antes de renderizar ou publicar.

## Fontes de verdade

- Regras editoriais: `n8n/vicescope-master-policy.json`
- Radar: `n8n/vicescope-01-radar-gta6.json`
- Mestre editorial: `n8n/vicescope-02-editorial-master.json`
- Renderização: `.github/workflows/render.yml`
- Integração de IA: `docs/freellmapi-vicescope.md`

## Pipeline

1. O Radar encontra pautas e classifica risco.
2. O Mestre Editorial resolve fontes e monta o briefing.
3. FreeLLMAPI fornece uma API compatível com OpenAI para geração, revisão e fallback entre cotas gratuitas.
4. O Mael aprova a pauta.
5. GitHub Actions gera áudio e vídeo.
6. A publicação permanece manual.

## Gateway FreeLLMAPI

- Upstream oficial: https://github.com/tashfeenahmed/freellmapi
- Versão homologada no Fly-Core: `v0.13.10`
- Imagem: `ghcr.io/tashfeenahmed/freellmapi:v0.13.10`
- Endpoint interno: `http://freellmapi:3001/v1`
- Modelo padrão: `auto`
- Implantação: `infra/freellmapi/compose.yaml`

Não copie o código-fonte upstream para este repositório e não troque a versão sem revisar release notes, compatibilidade com CPU antiga e segurança.

## Regras obrigatórias

- Nunca grave API keys, token unificado, senha, `ENCRYPTION_KEY` ou conteúdo de `.env` no Git.
- Credenciais pertencem ao cofre de credenciais do n8n ou ao arquivo local protegido no Fly-Core.
- Não exponha a porta 3001 à internet. O serviço é single-user.
- Não tente contornar cotas, criar contas duplicadas ou violar termos dos provedores.
- Trate a saída do modelo como rascunho; fatos externos exigem confirmação.
- Preserve inglês para narração e português para aprovação.
- Não habilite publicação automática.
- Não altere limites do contrato do `render.yml`: narração 1.200, título 50, subtítulo 70 caracteres.
- Mantenha temas adultos em abordagem jornalística não explícita.
- Não apresente arte gerada como screenshot oficial ou gameplay.

## Uso pelo n8n

Use um nó HTTP Request com:

- método: `POST`
- URL: `http://freellmapi:3001/v1/chat/completions`
- autenticação: Header Auth no cofre do n8n
- cabeçalho: `Authorization: Bearer <chave-unificada>`
- `model`: `auto`
- timeout inicial: 120 segundos

A resposta deve passar por validação de esquema e por revisão factual antes de seguir para aprovação humana.
