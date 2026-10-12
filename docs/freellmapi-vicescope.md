# FreeLLMAPI no ViceScope

Pesquisa e arquitetura revisadas em 12/10/2026.

## Decisão

O ViceScope usará o [FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi) como gateway privado entre o n8n e provedores com cotas gratuitas.

Ele não substitui Gemini, Groq ou outros provedores. Ele centraliza as chaves, expõe um único endpoint compatível com OpenAI, acompanha cotas e tenta outro modelo quando ocorre limite, timeout ou erro.

A versão homologada é `v0.13.10`. Essa versão corrigiu falhas em CPUs x86 antigas sem SSE4.2, condição relevante para o Core 2 Duo do Fly-Core.

## O que é gratuito de verdade

- O software é open source sob licença MIT.
- A execução no Fly-Core não gera cobrança própria.
- Cada provedor mantém sua própria cota e seus próprios termos.
- O número divulgado de bilhões de tokens representa a soma teórica das cotas disponíveis, não uma franquia garantida para uma única conta.
- Modelos, limites e disponibilidade podem mudar sem aviso.
- A edição gratuita recebe o catálogo assinado com atraso de aproximadamente 30 dias em relação ao catálogo premium.

Para o ViceScope isso serve como camada de redundância e economia, não como promessa de disponibilidade ilimitada.

## Papel no pipeline

| Etapa | Uso recomendado |
| --- | --- |
| Radar | Sem IA sempre que regras determinísticas forem suficientes |
| Triagem | Modelo rápido para classificar pauta e risco |
| Editorial | Modelo de melhor qualidade disponível para criar título, roteiro e três direções de capa |
| Auditoria | Segundo modelo/provedor para procurar invenções, clichês e conflito com as fontes |
| Aprovação | Telegram em português; decisão humana |
| Render | GitHub Actions com Kokoro e FFmpeg |
| Publicação | Manual |

Uma resposta produzida e revisada por modelos diferentes reduz erro, mas não substitui a confirmação das fontes.

## Provedores

Começar apenas com contas legítimas e chaves próprias:

1. Google Gemini — criação e análise geral, observando a cota vigente.
2. Groq — revisão rápida, classificação e validação de JSON.
3. Cerebras ou Mistral — fallback adicional quando disponível.
4. OpenRouter — somente rotas gratuitas permitidas pela conta.

Cuidados:

- GitHub Models é voltado a experimentação e prototipagem.
- NVIDIA NIM gratuito tem restrições de avaliação; não tratar como backend de produção.
- Cohere não deve entrar na cadeia padrão por conflito entre seus termos atuais e uso pessoal.
- Nunca criar contas duplicadas para ampliar cotas.
- Nunca compartilhar ou revender o endpoint.

## Segurança

FreeLLMAPI é single-user. O próprio projeto recomenda não expô-lo diretamente à internet.

A configuração do ViceScope:

- publica a interface somente em `127.0.0.1:3001`;
- conecta n8n e FreeLLMAPI pela rede Docker privada `fly-ai`;
- guarda o banco SQLite em `/dados/fly/freellmapi/data`;
- criptografa chaves com `ENCRYPTION_KEY`;
- limita o container a 768 MB de memória;
- não habilita Watchtower nem acesso ao socket Docker;
- não armazena segredos no Git.

Perder a `ENCRYPTION_KEY` torna as chaves armazenadas indecifráveis. Faça backup seguro dela e do diretório de dados.

## Instalação no Fly-Core

Execute somente depois de revisar o arquivo `infra/freellmapi/compose.yaml`.

```bash
sudo mkdir -p /dados/fly/freellmapi/data
sudo chown -R fly:fly /dados/fly/freellmapi

sudo docker network inspect fly-ai >/dev/null 2>&1 ||   sudo docker network create fly-ai

cd /dados/fly/freellmapi
openssl rand -hex 32 | sed 's/^/ENCRYPTION_KEY=/' > .env
printf 'PORT=3001\n' >> .env
chmod 600 .env

# Coloque compose.yaml desta pasta em /dados/fly/freellmapi/compose.yaml.
sudo docker compose up -d
sudo docker compose ps
curl -fsS http://127.0.0.1:3001/api/ping
```

Não use o instalador `curl | bash` no Fly-Core. O compose versionado permite auditar e repetir a implantação.

## Conectar o n8n

O serviço `fly-n8n` também precisa participar da rede externa `fly-ai`. No compose do n8n, adicione a rede ao serviço e declare:

```yaml
services:
  n8n:
    networks:
      - fly-ai

networks:
  fly-ai:
    external: true
```

Depois recrie o container do n8n e teste sem executar workflows:

```bash
sudo docker exec fly-n8n node -e "fetch('http://freellmapi:3001/api/ping').then(async r=>console.log(r.status,await r.text())).catch(e=>{console.error(e);process.exit(1)})"
```

## Abrir o painel com segurança

No Windows PowerShell:

```powershell
ssh -N -L 13001:127.0.0.1:3001 fly@192.168.0.104
```

Depois abra `http://localhost:13001`, crie a conta administrativa, adicione as chaves dos provedores e copie a chave unificada `freellmapi-...`.

Não cole essa chave no workflow. Crie uma credencial Header Auth no n8n.

## Contrato HTTP do n8n

```http
POST http://freellmapi:3001/v1/chat/completions
Authorization: Bearer <credencial-do-n8n>
Content-Type: application/json
```

```json
{
  "model": "auto",
  "temperature": 0.4,
  "messages": [
    {
      "role": "system",
      "content": "Siga a política editorial ViceScope e responda somente em JSON válido."
    },
    {
      "role": "user",
      "content": "Analise o lote recebido do Radar."
    }
  ]
}
```

O nó seguinte deve validar o JSON, limites de caracteres, presença de fontes e flags de risco. Em falha, o item vai para revisão, nunca diretamente para renderização.

## Operação

```bash
cd /dados/fly/freellmapi
sudo docker compose ps
sudo docker compose logs --tail 100 freellmapi
sudo docker stats --no-stream fly-freellmapi fly-n8n
```

Atualizações devem ser testadas conscientemente:

```bash
sudo docker compose pull
sudo docker compose up -d
curl -fsS http://127.0.0.1:3001/api/ping
```

Antes de mudar a tag da imagem, revisar release notes e compatibilidade com CPU antiga. Não usar `:latest` no ambiente estável.

## Critérios para considerar pronto

- container saudável após reinicialização;
- painel acessível somente por túnel SSH;
- n8n alcança `http://freellmapi:3001/api/ping`;
- pelo menos duas chaves de provedores diferentes testadas;
- chave unificada armazenada apenas no cofre do n8n;
- teste editorial retorna JSON válido;
- indisponibilidade de um provedor aciona fallback;
- nenhum fluxo publica conteúdo automaticamente.
