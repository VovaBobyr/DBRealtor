# DBRealtor Wiki

Knowledge base for the DBRealtor monorepo. Open this folder as your Obsidian vault.

## Structure

```
wiki/
├── architecture/
│   ├── overview.md      system diagram + data flow
│   ├── scraper.md       DBRealtor scraper internals
│   └── web.md           DBRealtorWeb portal internals
├── decisions/           ADRs (see DBRealtor/docs/decisions.md for current ADRs)
├── runbooks/
│   ├── deploy-scraper.md
│   └── deploy-web.md
├── prompts/
│   ├── kickoff-scraper.md   paste to start a scraper session with Claude
│   └── kickoff-web.md       paste to start a web portal session with Claude
└── daily/
    └── template.md      copy + rename to YYYY-MM-DD.md for daily notes
```

## How to use with Claude

1. Start each Claude Code session by pasting the relevant kickoff prompt from `prompts/`
2. Claude reads `CLAUDE.md` (root) automatically — it points here for deeper context
3. Add daily notes in `daily/` to capture decisions and context across sessions
4. Update `architecture/` pages when significant changes happen
