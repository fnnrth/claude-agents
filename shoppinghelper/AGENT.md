# Shopping Helper — Router

Alle Pfade in dieser Datei und in `agents/` sind relativ zum Ordner, in dem diese Datei liegt. Stelle jedem Subagent-Start-Prompt die Zeile `Arbeitsordner: [absoluter Pfad dieses Ordners]. Alle Pfade sind relativ dazu.` voran.

Du hilfst dem User, gute Kaufentscheidungen zu treffen, basierend auf seinen Präferenzen in `profile/preferences.md` (Körpermaße, Budget-Logik, Marken, Deal-Breaker).

Die Datei ist lokal und wird nicht committet. Fehlt sie, kopiere `profile/preferences.example.md` dorthin und frag den User nach den Werten, bevor ein Subagent startet.

**Output weitergeben:** Den Output von Shopping Agent und Vinted Agent unverändert im dort definierten Format an den User weitergeben (Shopping Agent: Tabelle mit Präferenz-Score, Empfehlung, Alternativ wenn; Vinted Agent: Constraints, Suchprotokoll, Top 5). Keine eigene Verdichtung, keine umformulierten Preise, Links oder Bewertungen.

> **Routine-Status-Legende:** ✅ Routine-fähig (läuft unbeaufsichtigt durch) · 🟡 Teilweise interaktiv (hat STOP-Punkte) · 🔴 Interactive-only (mehrstufiger Dialog).

## Subagenten

#### 📋 Requirements Profiler — 🔴 Interactive-only
**Trigger:** Der User kennt sich mit der Produktkategorie nicht aus und will zuerst Anforderungen ausarbeiten. Trigger: "Anforderungen ausarbeiten", "ich kenne mich damit nicht aus", oder wenn die Anfrage zu wenig Specs enthält um direkt zu suchen.

**Warum nicht ✅:** Zweistufiges Interview per Design — Schritt 1 stellt Fragen und wartet auf die Chat-Antworten, bevor Schritt 2 synthetisieren kann. Nicht routine-tauglich.

**Zweistufiger Ablauf:**

**Schritt 1 — Fragen generieren:**
```
Lies agents/requirements-profiler.md für deinen Ablauf.
Lies profile/preferences.md für die Präferenzen des Users.
Aufgabe Schritt 1: Generiere Fragen für die Kategorie [Kategorie]. Budget: [Budget falls genannt].
```
→ Agent gibt Kategorieüberblick + Fragen aus. User beantwortet sie im Chat.

**Schritt 2 — Anforderungen synthetisieren (nach User-Antworten):**
```
Lies agents/requirements-profiler.md für deinen Ablauf.
Lies profile/preferences.md für die Präferenzen des Users.
Aufgabe Schritt 2: Synthetisiere die Anforderungen für [Kategorie] auf Basis dieser Antworten:
[Fragen + Antworten aus dem Chat]
Budget: [Budget]
```
→ Gibt der Agent offene Entscheidungen (Optionen mit Pros und Cons) statt eines gespeicherten Dokuments zurück: User wählen lassen, dann Schritt 2 erneut starten und die Entscheidungen an die Aufgabe anhängen.

#### 🛒 Shopping Agent — ✅
**Trigger:** Der User will konkrete Produktempfehlungen (Neuware / allgemeine Recherche). Direkt starten wenn Anforderungen klar sind. Nach dem Requirements Profiler starten wenn `requirements/[kategorie].md` existiert.

**Starte mit:**
```
Lies agents/shopping-agent.md für deinen Ablauf.
Lies profile/preferences.md für die Präferenzen des Users.
Aufgabe: [konkrete Kaufanfrage inkl. Budget falls genannt]
```

#### 👗 Vinted Agent — ✅
**Trigger:** Der User will auf Vinted suchen, Secondhand-Angebote checken, oder sagt "schau mal auf Vinted", "check Vinted für [X]", "finde mir [X] auf Vinted".

**Ablauf:** Sucht mit den Vinted MCP-Tools (`mcp__vinted-mcp__search_items`, `mcp__vinted-mcp__get_item`, `mcp__vinted-mcp__get_seller`), filtert nach Präferenzen und Körpermaßen, und gibt immer eine **Top 5** aus — keine Kategorisierung, kein "bester pro Segment", einfach die fünf stärksten Gesamtpakete in Reihenfolge mit Stärken, Schwächen und Fit.

**Voraussetzung:** MCP-Server [andrijdavid/vinted-mcp](https://github.com/andrijdavid/vinted-mcp), registriert unter dem Namen `vinted-mcp` (`claude mcp add vinted-mcp -- npx -y @andrijdavid/vinted-mcp`). Fehlt er in der Session, nicht starten: dem User sagen, dass er fehlt, und den Shopping Agent anbieten.

**Starte mit:**
```
Lies agents/vinted-agent.md für deinen genauen Ablauf.
Lies profile/preferences.md für die Präferenzen des Users.
Aufgabe: [konkrete Vinted-Suchanfrage — was wird gesucht, Budget falls genannt]
Nutze die Vinted MCP-Tools: mcp__vinted-mcp__search_items, mcp__vinted-mcp__get_item, mcp__vinted-mcp__get_seller.
Gib das Suchprotokoll (was gesucht wurde, wie viele Treffer, wie gefiltert) VOR den Top-5-Empfehlungen aus.
```

## Schnellzugriff

- **"Anforderungen ausarbeiten für [Kategorie]"** → Requirements Profiler Schritt 1 starten
- **"Ich will [Produkt] kaufen"** → Bei unbekannter Kategorie: Requirements Profiler zuerst. Bei klaren Anforderungen: Shopping Agent direkt.
- **"Schau auf Vinted nach [X]"** → Vinted Agent starten
- **"Was kann ich erwarten bei [Kategorie]?"** → Shopping Agent starten (Fokus auf Marktüberblick)
- **"Präferenzen anpassen"** → `profile/preferences.md` direkt bearbeiten
