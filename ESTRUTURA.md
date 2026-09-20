# G1 DE IDEIAS - ESTRUTURA DO SITE (2026-09-07)
Dono: Fábio Rosestolato | Agente: Fabricio | Inspiração: globo.com + uol.com.br

## CONCEITO
Site de IDEIAS no formato portal de notícias. Mesma estrutura do Globo/UOL mas cada "notícia" é uma IDEIA extraída dos prints.
Fontes: Twitter/X, Instagram, GitHub, LLM + geografia Brasil/Gringa

## ESTRUTURA INSPIRADA GLOBO/UOL (analisado hoje 07/09/2026)
Globo.com: Header com logo + menu (g1, ge, gshow, globoplay) + barra editorias + MANCHETE grande + 3 colunas secundárias + widgets (economia, esporte, agenda) + footer gigante
UOL.com.br: Barra superior produtos + menu lateral gigante (Notícias, Política, Carros, Economia...) + MANCHETE + grid 2 colunas + colunistas + footer

Nosso: Header + barra editorias (filtros) + MANCHETE (ideia do dia) + GRID de cards + sidebar "Mais lidas" + footer

## HEADER
Logo: G1 DE IDEIAS | Menu: [Todas] [Instagram] [Twitter] [GitHub] [LLM] [Brasil] [Gringa]
Sub-filtros: [Hoje] [Semana] [Mais votadas] [Busca]

## CARD (na home, igual Globo)
- Título grande (CLICÁVEL -> página separada /ideia/123.html)
- Linha crédito: @fulano • Instagram • por @fabio • 7 set 2026 16:31 • Brasil
- Tags: #github #clona-site #instagram (mostra que está em 2 categorias)
- Resumo 2 linhas do texto OCR
- Links: [Ver original] [Ver no GitHub] [Copiar ideia]
- Exemplo:
```
┌─────────────────────────────────────────┐
│ 🔥 Repositório que clona site inteiro  │ <- título link
│ @vinisousabr • Instagram • por fabio   │
│ 7 set 2026 • Brasil • #Instagram #GitHub│
│ "Strix: tool grátis que ataca seu app" │
│ [instagram.com/p/xyz] [github.com/abc] │
└─────────────────────────────────────────┘
```

## PÁGINA DETALHE (ao clicar título)
URL: /root/g1-ideias/ideias/20260907-133102.html
Conteúdo: título + crédito completo (@ + login coletor + data/horário exato) + texto OCR completo + imagem print original + links clicáveis + botão voltar

## MULTI-CATEGORIA (regra ouro)
Uma ideia pode ter N categorias. Se @fulano no Instagram indica repo github, salva:
categorias: ["instagram","github","brasil"]
-> aparece quando filtra Instagram E quando filtra GitHub (igual UOL que mesma notícia está em "Tecnologia" e "Economia")

## JSON SCHEMA (ideias.json)
{
  "id": "20260907-133102",
  "titulo": "Repositório que clona site inteiro",
  "texto": "Strix monta time de agentes...",
  "fonte_arroba": "@vinisousabr",
  "plataforma": "instagram",
  "coletor_login": "fabio",
  "data": "2026-09-07",
  "hora": "13:31",
  "categorias": ["instagram","github","brasil"],
  "link_original": "https://instagram.com/p/...",
  "link_github": "https://github.com/...",
  "imagem": "/Pictures/Screenshots/Screenshot_20260907-133102.Instagram.png"
}

## PASTAS
Prints: /storage/emulated/0/Pictures/Screenshots
Vault: /root/quiz-financas/vault
Site: /root/g1-ideias/ (ideias.json, ideias.html, ideias/ subpasta)
