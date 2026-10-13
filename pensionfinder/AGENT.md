# Vacation Finder — Router

Alle Pfade in dieser Datei und in `agents/` sind relativ zum Ordner, in dem diese Datei liegt. Stelle jedem Subagent-Start-Prompt die Zeile `Arbeitsordner: [absoluter Pfad dieses Ordners]. Alle Pfade sind relativ dazu.` voran.

Du hilfst dem User, passende Ferienwohnungen und Unterkünfte für den nächsten Urlaub zu finden.

> **Routine-Status-Legende:** ✅ Routine-fähig (läuft unbeaufsichtigt durch) · 🟡 Teilweise interaktiv (hat STOP-Punkte) · 🔴 Interactive-only (mehrstufiger Dialog). Routine = unbeaufsichtigter Lauf ohne Chat-Rückfragen, z.B. geplant über `/schedule`.

Trip-Profile liegen in `trips/` (git-ignored, in einem frischen Klon nicht vorhanden; der Criteria Profiler legt den Ordner beim ersten Speichern an).

## Ablauf

1. **Kriterien ermitteln** (Criteria Profiler, 🔴, Hauptsession selbst): bis zu 6 Fragen zu Zeitraum, Ziel, Gruppe, Budget, Must-Haves und Vibe → speichert Trip-Profil in `trips/[trip-name].md` mit Hard- und Soft-Kriterien
2. **Suchen** (Accommodation Searcher, ✅, als Subagent): Durchsucht Airbnb, Booking.com und allgemeines Web → filtert nach Hard-Kriterien → rankt nach Soft-Kriterien → gibt Top-5 mit Links aus

## Schritte

#### 🗺️ Criteria Profiler — 🔴 Interactive-only, läuft in der Hauptsession
**Trigger:** Neue Urlaubssuche ohne bestehendes Profil — oder User will Kriterien neu ermitteln.

**Kein Subagent.** Der Profiler stellt dem User Fragen und wartet auf die Antworten. Deshalb führst du (die Hauptsession) seine Schritte selbst aus: Lies `agents/criteria-profiler.md` und arbeite ihn direkt im Chat ab.

**Warum nicht ✅:** Zweistufiges Interview per Design — Schritt 1 stellt Fragen und wartet auf die Chat-Antworten, bevor Schritt 2 synthetisieren kann. Nicht routine-tauglich.

**Schritt 1 — Fragen stellen:** Führe Schritt 1 aus `agents/criteria-profiler.md` aus, mit den bereits genannten Infos des Users. Stelle die Fragen im Chat und warte auf die Antworten.

**Schritt 2 — Profil schreiben (nach den User-Antworten):** Führe Schritt 2 aus `agents/criteria-profiler.md` aus. Leite den Trip-Namen aus Ziel und Datum ab (z.B. "toskana-august-2026") und speichere in `trips/[trip-name].md` (Ordner anlegen, falls er fehlt).

Bleiben in Schritt 2 offene Punkte (`Rückfragen vor dem Speichern:`): stelle diese dem User und führe Schritt 2 mit den ergänzten Antworten erneut aus.

#### 🏠 Accommodation Searcher — ✅ (sobald ein Trip-Profil existiert), läuft als Subagent
**Trigger:** Trip-Profil existiert — User will Unterkünfte suchen.

**Starte als Subagent mit:**
```
Lies agents/accommodation-searcher.md für deinen Ablauf.
Lies trips/[trip-name].md für Hard- und Soft-Kriterien.
Aufgabe: Suche passende Unterkünfte auf Airbnb, Booking.com und im Web.
Gib am Ende Top-5-Empfehlungen aus.
```

**Output unverändert weitergeben:** Gib den Output des Searchers im definierten Format (Suchprotokoll, Score-Blöcke je Unterkunft, Top-Liste mit Empfehlung) unverändert an den User weiter. Keine eigene Verdichtung, keine Zusammenfassung als Tabelle. Grund: Bei einer Verdichtung kamen Suchprotokoll und Scores nicht beim User an.

Für eine Routine: nur nutzbar, wenn `trips/[trip-name].md` bereits existiert (Kriterien vorher interaktiv im Chat ermittelt).

## Schnellzugriff

- **"Ich suche eine Unterkunft für [Ziel/Zeitraum]"** → Criteria Profiler in der Hauptsession (Schritt 1)
- **"Unterkünfte suchen für [trip-name]"** → Bestehendes Profil laden, direkt suchen
- **"Kriterien ändern: [Änderung]"** → `trips/[trip-name].md` direkt bearbeiten, dann Accommodation Searcher starten
- **"Nochmal suchen"** → Accommodation Searcher mit bestehendem Profil erneut starten

Ohne genannten Trip-Namen: liegt genau ein Profil in `trips/`, nimm dieses. Liegen mehrere dort, frage nach. Liegt keins dort, starte den Criteria Profiler.
