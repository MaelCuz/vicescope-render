# ViceScope

Pipeline automatizado para pesquisar, revisar e renderizar vídeos curtos em inglês sobre GTA VI, com aprovação humana e custo adicional zero.

## Componentes

- `n8n/`: Radar e Mestre Editorial.
- `infra/freellmapi/`: gateway privado para provedores de IA com cotas gratuitas.
- `vicescope-render/`: geração de narração e vídeo.
- `.github/workflows/render.yml`: renderização no GitHub Actions.
- `AGENTS.md`: regras para agentes de desenvolvimento.

## Documentação

- [Operação dos workflows](n8n/README.md)
- [FreeLLMAPI no ViceScope](docs/freellmapi-vicescope.md)
- [Repositório upstream do FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi)

Publicação automática permanece desativada.
