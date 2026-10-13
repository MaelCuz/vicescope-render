# ViceScope e OpenCut

## Implementado

O workflow `.github/workflows/render.yml` gera o artefato
`ViceScope-OpenCut-Media-<run_number>`, contendo `ViceScope-OpenCut-Media.zip`.
O pacote tem imagens oficiais separadas, voz WAV estéreo a 48 kHz,
roteiro e um manifesto com tempos sugeridos e hashes SHA-256.

O exportador valida duração e formato do áudio, decodificação das imagens
e integridade do ZIP. Ele não gera legendas com tempos inventados:
a transcrição do OpenCut pode gerar as legendas, que precisam de revisão.

O roteiro é o mesmo input utilizado para gerar a voz. O padrão atual é
uma demonstração do formato, não uma notícia pronta para publicar.

## Uso no site público

Extraia o ZIP e importe áudio e imagens no OpenCut. Monte as faixas
separadas usando os tempos do manifesto. O JSON é um plano de montagem
ViceScope, **não** um projeto nativo importável pelo OpenCut.

A inspeção do código de OpenCut-app/opencut-classic encontrou projetos
no IndexedDB e mídia em OPFS, dentro do navegador. Os gerenciadores
ProjectManager e MediaManager são APIs internas do aplicativo, não
endpoints HTTP para o n8n.

## Ainda falta para automação completa

- Conectar a saída editorial validada do n8n ao disparo autenticado do
  workflow de renderização. Isso não está conectado neste incremento.
- Separar teste técnico de produção editorial: continuar respeitando
  renderAllowed e revisão factual no fluxo de notícias.
- Implementar e testar um importador em uma instalação própria do
  OpenCut, com versão fixada. Ele deve carregar mídias, criar faixas
  usando as APIs internas e salvar um projeto novo.
- Validar no navegador a reabertura, edição e exportação desse projeto.
- Só depois avaliar automação da exportação no navegador.

O pacote atual não controla o site público, não monta automaticamente
a timeline e não publica vídeos. Não alterar diretamente o IndexedDB
do usuário nem anunciar uma integração concluída antes dos testes acima.
