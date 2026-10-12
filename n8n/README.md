# ViceScope no n8n

Esta pasta guarda os workflows importáveis do projeto ViceScope.

## Etapa 1 — Radar GTA VI

Arquivo: `vicescope-01-radar-gta6.json`

O workflow:

- executa manualmente ou a cada 30 minutos;
- monitora o canal oficial da Rockstar Games;
- monitora o Rockstar Newswire e tendências do GTA VI pelo Google News RSS;
- aceita apenas itens relacionados ao GTA VI;
- dá prioridade a fontes oficiais;
- marca fontes externas como `needs_verification`;
- remove URLs repetidas durante 14 dias;
- entrega um lote em `ready_for_ai` para a próxima etapa.

Esta etapa não precisa de API, token ou credencial.

## Como importar

1. Abra o n8n.
2. Crie um workflow novo.
3. No menu do workflow, escolha **Import from File**.
4. Selecione `vicescope-01-radar-gta6.json`.
5. Clique em **Test workflow**.
6. Abra o último nó, **Radar pronto**, e confira o JSON de saída.

Não ative a execução automática antes do teste manual.

## Próximas etapas

1. Gemini cria três ângulos editoriais e o primeiro roteiro.
2. Groq audita fatos, clichês e originalidade.
3. Telegram envia os candidatos para aprovação do Mael.
4. GitHub Actions recebe o roteiro aprovado e renderiza o vídeo.
5. YouTube recebe primeiro como não listado para revisão final.
