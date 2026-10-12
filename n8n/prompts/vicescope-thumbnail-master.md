# ViceScope — Guia de imagem e thumbnail Master 1.0

## Objetivo

Criar capas com acabamento editorial profissional, leitura imediata no celular e forte curiosidade, sem copiar concorrentes, frames vazados ou composições oficiais.

## Ordem de mídia

1. Imagem oficial direta da galeria Rockstar, com URL e identidade confirmadas.
2. Imagem de imprensa licenciada ou permitida, com origem registrada.
3. Conceito original gerado, marcado internamente como não oficial e não gameplay.

## Direção visual

- 1280x720, composição 16:9.
- Um foco principal; no máximo dois personagens.
- Personagem no terço direito ou esquerdo, não sempre central.
- Espaço negativo limpo para headline de 2 a 4 palavras.
- Luz coerente com o ambiente, textura de pele natural e pequenas imperfeições.
- Paleta Vice City pode usar teal, laranja, rosa e vermelho, mas sem neon exagerado.
- Veículos precisam ter rodas, suspensão, guidão, reflexos e perspectiva fisicamente coerentes.
- Texto e logotipo são adicionados depois no editor; não pedir ao gerador para desenhá-los.

## Rejeição anti-IA

Rejeitar qualquer resultado com:

- pele plástica, excesso de suavização ou HDR;
- dedos, olhos, dentes, joias ou anatomia incoerentes;
- texto aleatório, marca falsa ou interface inventada;
- moto/carro impossível ou reflexos incorretos;
- fundo sem lógica espacial;
- composição simétrica genérica de pôster;
- brilho neon/bloom que apaga detalhes;
- semelhança excessiva com frame oficial ou vazado.

## Escolha de personagem

- Lucia: pauta diretamente sobre Lucia, personagem/história ou atualização ampla oficial relevante.
- Jason: pauta diretamente sobre Jason, veículos, tecnologia e sistemas de gameplay.
- Dupla: trailer, relação narrativa, lançamento ou anúncio oficial amplo.
- Outro personagem: somente quando for parte real da notícia.
- Nunca usar Lucia ou apelo sexual em pauta sem relação factual.

## Prompt-base seguro

```text
Original 16:9 editorial thumbnail background for a verified GTA VI news story.
Lead subject: [CHARACTER OR STORY SUBJECT].
Scene: [VERIFIED OR NEUTRAL CONTEXT].
Professional AAA crime-game promotional polish, original composition, natural skin texture,
coherent camera lens, lighting, shadows, reflections and perspective, credible vehicle geometry,
one strong focal subject, maximum two, clean negative space for a short headline,
readable silhouette at mobile size.
No embedded text, no logo, no nudity, no sex act, no fetish pose, no fake gameplay UI,
no copied screenshot, no leaked frame, no plastic skin, no anatomy errors, no excessive neon.
Internal label: CONCEPT VISUAL — NOT GAMEPLAY.
```

## Variação Lucia praia

Usar somente quando Lucia tiver relação com a pauta. Se a imagem oficial de biquíni vermelho não estiver confirmada por arquivo direto da Rockstar, criar conceito original com roupa vermelha de praia não explícita. Não sexualizar pose, enquadramento ou headline.

## Metadados obrigatórios para conceito

```json
{
  "assetType": "generated_concept",
  "official": false,
  "gameplay": false,
  "humanApproved": false,
  "disclosure": "CONCEPT VISUAL — NOT GAMEPLAY"
}
```
