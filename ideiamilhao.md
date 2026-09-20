# IDEIA MILHÃO — G1 DE IDEIAS
### Site/App tipo Globo.com e UOL.com.br mas com IDEIAS no lugar de notícias
**Dono:** Fábio Rosestolato | **Agente:** Fabricio do Android | **Data:** 7 set 2026 | **Versão:** 1.0
**Crédito:** Desenvolvido por: Fábio Rosestolato

---

## 1. VISÃO GERAL
Transformar os **736 prints** (471MB) salvos em `/storage/emulated/0/Pictures/Screenshots` em um portal de ideias navegável, igual `globo.com`/`uol.com.br`, mas onde cada "notícia" é uma **IDEIA** curada por você.

Não é banco de notícias. É banco de **IDEIAS** com crédito, data e links originais. Cada print que você salvou vira um card clicável.

---

## 2. ESTRUTURA INSPIRADA NO GLOBO/UOL (analisado 07/09/2026)

**Globo.com:** Header logo + menu (g1, ge, gshow, globoplay) + barra de editorias + MANCHETE gigante + 3 colunas secundárias + widgets + footer enorme
**UOL.com.br:** Barra superior de produtos + menu lateral com 20+ editorias + manchete + grid 2 colunas + colunistas

**Nosso G1 DE IDEIAS:**
```
┌─────────────────────────────────────────────────┐
│ HEADER: [ G1 DE IDEIAS ]  [Todas][Instagram][Twitter][GitHub][LLM][Brasil][Gringa] │
├─────────────────────────────────────────────────┤
│ MANCHETE DO DIA (ideia mais forte)              │
├──────────────────┬──────────────────┬───────────┤
│ Card 1           │ Card 2           │ Sidebar   │
│ Card 3           │ Card 4           │ Mais      │
│ Card 5           │ Card 6           │ copiadas  │
└──────────────────┴──────────────────┴───────────┘
│ FOOTER: Sobre | Contato | GitHub | Instagram    │
└─────────────────────────────────────────────────┘
```

Filtros extras: `[Hoje] [Semana] [Mais votadas] [Busca]`

---

## 3. FONTES E EDITORIAS
**Fontes principais (vira editoria):**
- **Instagram** (@vinisousabr, @etc)
- **Twitter/X** (@hacker, etc)
- **GitHub** (repositórios)
- **LLM** (prompts, jailbreaks, roteadores)
- **Geografia:** Brasil / Gringa (EUA, Europa)

**Regra de Ouro MULTI-CATEGORIA:**
Uma ideia NUNCA fica só numa categoria. Se o `@fulano` no **Instagram** indica um repositório do **GitHub**, essa ideia aparece em **Instagram E GitHub** ao mesmo tempo.
> Exemplo: `categorias: ["instagram","github","brasil"]` -> aparece nos dois filtros (igual UOL que põe mesma notícia em Tecnologia e Economia)

---

## 4. CARD NA HOME (igual manchete do Globo)
Cada card tem:
- **Título grande CLICÁVEL** -> leva pra página separada `/ideias/20260907-133102.html`
- **Linha de crédito obrigatória:** `@fonte • Plataforma • por @coletor • 7 set 2026 13:31 • Brasil/Gringa`
- **Tags:** `#github #instagram` (mostra multi-categoria)
- **Resumo:** 2 linhas do texto extraído via OCR
- **Links:** `[Ver original]` `[Ver no GitHub]` `[Copiar ideia]`

**Exemplo real (extraído hoje 07/09):**
```
┌──────────────────────────────────────────────┐
│ 🔥 Repositório que clona site inteiro       │ ← título link
│ @vinisousabr • Instagram • por @fabio       │
│ 7 set 2026 13:31 • Brasil • #Instagram #GitHub│
│ "Strix: tool grátis que ataca seu app como  │
│  hacker real, 45k stars no GitHub"          │
│ [instagram.com/p/xyz] [github.com/strix]    │
└──────────────────────────────────────────────┘
```

---

## 5. PÁGINA DE DETALHE (ao clicar no título)
**URL:** `/root/g1-ideias/ideias/20260907-133102.html` (ou `/sdcard/Download/00_AMBIENTE_TERMUX/ideias/...`)
**Conteúdo:**
- Título completo
- Crédito completo: `@fulano` + `Instagram` + `coletado por @fabio` + `7 set 2026 13:31:05`
- Texto OCR completo (extraído com tesseract 5.5.0 por+eng)
- Imagem do print original
- Links clicáveis (original + GitHub se tiver)
- Botão Voltar + Compartilhar

---

## 6. FLUXO TÉCNICO (100% offline no celular)

1. **Captura:** Print no celular -> salva em `/storage/emulated/0/Pictures/Screenshots` (736 arquivos, 471MB, verificado 07/09/2026 - /DCIM/Screenshots NÃO existe)
2. **OCR:** `tesseract 5.5.0 por+eng --psm 6` roda no **moto g84 5G** (8 núcleos, 7.3GB RAM) - 1 a 2 seg por foto, offline, sem IA cara
3. **Limpeza + Classificação:** Script Python classifica por keywords -> define `categorias` e `plataforma` (ex: tem "github.com" -> github, tem "Strix" -> instagram+github)
4. **Salva:** 
   - Vault Obsidian: `/root/quiz-financas/vault/20260907-133102.md`
   - JSON: `/root/g1-ideias/ideias.json` + `/sdcard/Download/00_AMBIENTE_TERMUX/g1-ideias/ideias.json`
   - HTML: `/root/g1-ideias/ideias.html` (landing) + `/ideias/*.html` (detalhes)
5. **Publica:** HTML neo-brutalista + APK WebView (via /root/build-apk.sh)

**Teste real 07/09:** Extraímos 10 últimas fotos (4 Instagram Strix + 6 YouTube hacker cego/DeepSeek) com OCR 80-90% de precisão.

---

## 7. JSON SCHEMA (ideias.json)
```json
{
  "id": "20260907-133102",
  "titulo": "Repositório que clona site inteiro",
  "texto_completo": "Strix monta time de agentes que fingem ser hackers reais...",
  "resumo": "Tool grátis que ataca seu app como hacker",
  "fonte_arroba": "@vinisousabr",
  "plataforma": "instagram",
  "coletor_login": "fabio",
  "data": "2026-09-07",
  "hora": "13:31:05",
  "categorias": ["instagram", "github", "brasil"],
  "link_original": "https://instagram.com/p/xyz",
  "link_github": "https://github.com/strix-ai/strix",
  "imagem": "/Pictures/Screenshots/Screenshot_20260907-133102.Instagram.png",
  "perfil_escrita": "provocador"
}
```

---

## 8. PASTAS OFICIAIS (à prova de Termux fechar)
- **Prints:** `/storage/emulated/0/Pictures/Screenshots` (=/sdcard/Pictures/Screenshots)
- **Projeto G1:** `/root/g1-ideias/` (ideias.json, ESTRUTURA.md, ideias.html, pasta ideias/)
- **Vault:** `/root/quiz-financas/vault/`
- **Backup/Ambiente:** `/sdcard/Download/00_AMBIENTE_TERMUX/ideiamilhao.md` (este arquivo) + `/sdcard/Download/00_AMBIENTE_TERMUX/g1-ideias/`
- **Quiz antigo:** `/root/quiz-financas/` (arquivado, banco_questoes.json zerado)
- **Quiz public:** `/root/quiz-financas/public/`

---

## 9. REDE (verificado 07/09/2026 16:50)
- **Android:** moto g84 5G, Android 15, wlan 192.168.0.122, tailscale 100.106.249.31
- **Linux:** linux-principal 192.168.0.146, SSH `fabiorjvr@` via `/root/.ssh/id_linux`, Ubuntu 6.14
- **Windows:** wilgo@100.68.58.50 (tailscale) montado em `/home/fabiorjvr/PC-WINDOWS`
- **ADB:** 127.0.0.1:5555 OFF (precisa USB), wrapper `/root/adb_self.sh` + keepalive 25s

---

## 10. PERFIS DE ESCRITA (diferencial)
Mesma ideia pode ter 3 versões de escrita (escolhe no filtro):
- **Técnico:** "Strix: Agentes de IA com pentest automatizado via API Claude/Gemini, 45k stars"
- **Provocador:** "Alguém criou um hacker de IA grátis e ele é melhor que você"
- **Didático:** "Como testar segurança do seu app em 5 minutos sem pagar nada"

---

## 11. PRÓXIMOS PASSOS
1. Rodar OCR em lote nos 736 prints -> gerar ideias.json completo
2. Gerar `ideias.html` com header + filtros + manchete + grid (neo-brutalista)
3. Gerar páginas de detalhe `/ideias/*.html`
4. Testar no Chrome + gerar APK via `bash /root/build-apk.sh`
5. Publicar em `/sdcard/Download/00_AMBIENTE_TERMUX/APLICATIVOS_CRIADOS/`

---

**Backup memória:** `MEMORY.md` (2051 chars) + `USER.md` (1281 chars) + SQLite `/root/.local/share/opencode/opencode.db` (ses_f8348ba9...)
**Para recuperar após queda:** abrir Termux e falar "olhe sua memoria"
