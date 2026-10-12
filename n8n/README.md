# ViceScope no n8n

Esta pasta guarda os workflows importáveis do projeto ViceScope.

## Etapa 1 — Radar GTA VI

Arquivo: `vicescope-01-radar-gta6.json`

O workflow:

- executa manualmente ou a cada 30 minutos;
- monitora o canal oficial da Rockstar Games;
- monitora Rockstar Newswire e tendências do GTA VI pelo Google News RSS;
- separa o título limpo, o veículo e o link usado na descoberta;
- dá prioridade a fontes oficiais;
- marca links do Google News para resolução no Fluxo 02;
- marca rumores, datas anormais e fontes desconhecidas;
- remove propaganda e pautas repetidas;
- mantém temas adultos relevantes ao GTA VI, mas exige abordagem jornalística não explícita;
- mantém no máximo uma pauta por tema e uma pauta externa por veículo;
- entrega no máximo seis candidatos em `ready_for_editorial_ai`;
- inclui o contrato exato aceito pelo `render.yml`.

Esta etapa não precisa de API, token ou credencial.

## Idiomas do pipeline

- narração, título e subtítulo do vídeo: inglês (`en-US`);
- resumo enviado ao Mael para aprovação: português (`pt-BR`).

## Limites do renderizador

- narração: até 1.200 caracteres;
- título: até 50 caracteres;
- subtítulo: até 70 caracteres;
- vozes: `am_adam`, `am_michael`, `af_heart` ou `af_bella`;
- velocidades: `0.95`, `1.00`, `1.08` ou `1.15`.

## Como importar e testar

1. Abra o n8n.
2. Crie um workflow novo.
3. No menu do workflow, escolha **Import from File**.
4. Selecione `vicescope-01-radar-gta6.json`.
5. Execute usando **Teste manual**.
6. Abra o último nó, **Radar pronto**, e confira o JSON.

Não publique o workflow até o Fluxo 02 estar conectado.

## Deduplicação

O radar mantém URLs por 14 dias usando os dados estáticos do workflow.

O n8n não persiste esses dados durante testes manuais. A memória passa a ser salva quando o workflow é publicado e executado pelo agendamento. Por isso, ver os mesmos itens em dois testes manuais não significa falha.

## Segurança editorial

O RSS serve apenas para descobrir possíveis pautas. Um título não é tratado como fato confirmado.

Antes de criar roteiro, o Fluxo 02 deverá:

1. resolver links intermediários do Google News;
2. confirmar a afirmação na página de origem;
3. procurar confirmação oficial ou uma segunda fonte independente;
4. rejeitar pauta sem evidência suficiente;
5. em temas adultos, reescrever título e miniatura sem termos ou imagens explícitas;
6. produzir roteiro estruturado dentro dos limites do renderizador.

## Próximas etapas

1. Gemini cria ângulos editoriais e um roteiro em inglês.
2. Groq audita fatos, clichês, risco e originalidade.
3. Telegram envia resumo em português para aprovação do Mael.
4. GitHub Actions recebe apenas o roteiro aprovado.
5. O vídeo é gerado como artefato; publicação automática continuará desativada.

## Versão Master 1.2

A camada Master mantém a criatividade ligada à pauta e não a um personagem usado de forma aleatória.

- `vicescope-master-policy.json`: regras permanentes de fonte, personagens, temas 18+, vazamentos, capas e aprovação.
- `prompts/vicescope-editorial-master.md`: prompt do editor com saída JSON obrigatória.
- `vicescope-02-editorial-master.json`: subworkflow importável e sem credenciais que converte o lote do Radar em três briefings de capa por pauta.
- a galeria oficial da Rockstar é a primeira opção de mídia;
- frames vazados nunca são reutilizados;
- arte gerada é conceito, nunca é chamada de gameplay;
- a imagem atribuída a Lucia com biquíni vermelho permanece pendente de confirmação direta do arquivo oficial;
- geração automática de imagem do Gemini fica desligada por padrão porque os modelos de imagem não têm Free Tier em 12/10/2026;
- publicação continua sempre manual.
