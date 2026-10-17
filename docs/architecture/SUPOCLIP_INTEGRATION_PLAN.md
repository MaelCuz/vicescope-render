# ViceScope | Plano de integração SupoClip
Data: 2026-10-17
Status: PLANEJADO / NAO IMPLANTADO
Repositório público: este arquivo NÃO contém credenciais, IPs privados nem segredos.

## Objetivo
Receber vídeo bruto + vídeo de referência e entregar cortes revisáveis em MP4 sem depender de Claude pago.

## Componentes
- n8n: coordenador, filas, estados, roteamento e revisão humana.
- Gemini: análise multimodal e plano editorial de referência; sujeito a limites de cota.
- SupoClip (https://github.com/FujiwaraChoki/supoclip): candidato prioritário para cortes baseados em fala, legendas, enquadramento vertical, renderização, API REST e MCP. Licença AGPL-3.0: revisar obrigações antes de distribuição/serviço.
- OpenMontage (https://github.com/Open-Montage-app/OpenMontage): candidato experimental para edição mais sofisticada. Ainda sem validação.
- FFmpeg / FFprobe / Python: executor determinístico, transformação, renderização e verificação técnica.
- Agency Agents: instruções e papéis de coordenador, analista, diretor, editor e revisor; NÃO substitui provedor LLM.
- Graft e Codebase Memory MCP: contexto para agentes de desenvolvimento, não para edição de vídeo.
- Memória ViceScope: registrar job, decisões, hashes, resultados e tentativas; evitar duplicações.

## Pipeline previsto
1. Entrada: upload original + referência + perfil editorial.
2. Validação: tipo, duração, tamanho, identidade do arquivo, limites e autorização.
3. Análise: Gemini analisa referência e gameplay; para material falado SupoClip pode sugerir segmentos.
4. Plano: JSON com segmentos, zooms, velocidade, legenda, layout, critérios de aceitação.
5. Revisão: aprovação explícita antes de despachar jobs.
6. Executor: SupoClip para fluxo de cortes/legendas ou FFmpeg para edição baseada em plano; OpenMontage apenas após testes.
7. QA: ffprobe, integridade MP4, duração, dimensões, áudio, legendas, arquivo não vazio.
8. Entrega: status e links ao painel; não publicar sem aprovação.

## Interface entre orquestrador e executor
Contrato proposto: POST /jobs com job_id, asset_id, approved, profile_id, edit_plan e URLs ou identificadores de mídia autorizados. Retornar job_id e status; GET /jobs/{id} para progresso; callback assinado opcional. Implementação pendente. Não enviar arquivos ou chaves em logs.

## Infraestrutura
- Linux fly-core: manter n8n e orquestração; CPU antiga não deve executar renderização pesada.
- PC com GPU: candidato a host do executor SupoClip/FFmpeg, sujeito a Docker/driver/VRAM, rede e testes.
- Acesso remoto de execução ao PC NÃO está conectado ao assistente; instalar localmente ainda é necessário.

## Situação verificada em 17/10/2026
- Workflow n8n 'ViceScope Cortes | Análise visual e revisão v1' tem análise Gemini e nó de preparação de pacote de renderização.
- Renderização automática ainda NÃO está ligada ao n8n.
- Tentativa de criar workflow independente do agente de vídeo falhou por indisponibilidade da integração n8n; não afirmar que foi criado.
- SupoClip não foi instalado nem testado no ambiente.
- SupoClip padrão pede AssemblyAI e um provedor LLM; documentação cita Whisper/Ollama locais. Confirmar desempenho/custo/qualidade no hardware.
- SupoClip é centrado em transcrição; testar separadamente gameplay sem fala.
- Nenhum teste ponta a ponta comprovou geração automática do MP4.

## Critérios para considerar MVP pronto
- [ ] Serviço SupoClip sobe com health check
- [ ] Credenciais e modo gratuito/local configurados e testados
- [ ] API SupoClip autenticada acessível ao n8n
- [ ] Fluxo agente editor criado sem afetar workflow ativo
- [ ] Envio de job aprovado retorna identificador real
- [ ] Um vídeo falado gera corte e legenda
- [ ] Um gameplay BF6 gera corte com referência visual ou fallback validado
- [ ] QA verifica vídeo final
- [ ] Painel mostra status e permite download
- [ ] Falhas e limites de cota tratados sem cobrança inesperada

## Estimativa, não medição
MVP: aproximadamente 40-50% de avanço estrutural, com grande incerteza até teste ponta a ponta.
Prazo alvo condicionado: terça-feira 20/10/2026 para primeiro teste técnico, quinta-feira 22/10/2026 para MVP experimental, APENAS se houver acesso ao executor, dependências instaláveis e correção dos erros encontrados. Não é promessa de entrega autônoma ou trabalho em segundo plano.

## Prioridade
P0: acesso/instalação do executor + teste API.
P1: integrar n8n -> executor e QA.
P2: integração OpenMontage e edição avançada baseada em referência.
P3: melhorias de memória e multiagentes para desenvolvimento.

## Fontes
https://github.com/FujiwaraChoki/supoclip
https://github.com/FujiwaraChoki/supoclip/blob/main/docs/api-reference.md
https://github.com/FujiwaraChoki/supoclip/blob/main/docs/configuration.md
