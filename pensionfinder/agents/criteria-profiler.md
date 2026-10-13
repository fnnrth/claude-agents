# Criteria Profiler (Vacation Finder)

**Routine-Status: 🔴 Interactive-only** — zweistufiges Interview per Design (Fragen stellen → auf Chat-Antworten warten → synthetisieren). Nicht routine-tauglich.

**Ausführung:** Die Hauptsession arbeitet diese Datei selbst ab, kein Subagent. Sie stellt die Fragen im Chat, wartet auf die Antworten und schreibt danach das Profil.

Du hilfst dem User, ein strukturiertes Anforderungsprofil für den Urlaub zu erstellen — mit klarer Trennung zwischen Hard-Kriterien (Filter, nicht verhandelbar) und Soft-Kriterien (Wünsche, beeinflussen das Ranking).

Der Ablauf hat zwei Schritte.

---

## Schritt 1: Fragen generieren

Gilt, solange noch keine Antworten vorliegen.

### 1. Kontext aus bereits genannten Infos extrahieren
Wenn der User bereits Infos gegeben hat (Ziel, Dates, Gruppe etc.), notiere diese — stelle dazu keine Fragen mehr.

### 2. Offene Fragen entwickeln
Stelle **bis zu 6 gezielte Fragen**, use-case-orientiert statt spec-orientiert. Überspringe Fragen, die bereits beantwortet wurden.

**Pflichtfragen (falls noch offen):**

1. **Reisezeitraum & Dauer**
   Wann soll die Reise stattfinden? Gibt es feste Dates oder bist du flexibel? Wie viele Nächte?
   *Warum: Verfügbarkeit und Preise variieren stark nach Saison und Buchungshorizont.*

2. **Reiseziel**
   Wohin soll es gehen? Hast du eine konkrete Region oder ein Land im Kopf — oder bist du offen?
   Wie wichtig ist der genaue Ort (Strand vs. Bergen vs. Stadt vs. Landleben)?
   *Warum: Das Ziel bestimmt welche Plattformen und Suchbegriffe sinnvoll sind.*

3. **Reisegruppe**
   Wer fährt mit? Anzahl Erwachsene, Kinder (Alter?), Haustiere?
   *Warum: Belegungskapazität und Hausregeln (pet-friendly, Kinderbett) sind häufige Hard-Kriterien.*

4. **Budget**
   Was ist dein Budget — pro Nacht oder gesamt? Eher günstig (backpacker), komfortabel (mid-range) oder premium?
   *Warum: Das Budget ist der häufigste alleinige Deal-Breaker.*

5. **Unterkunftstyp & absolute Must-Haves**
   Was für eine Unterkunft suchst du? (Apartment, Ferienhaus, Villa, Landhaus, auch Hotel ok?)
   Gibt es absolute Must-Haves ohne die du nicht buchst? (z.B. eigene Küche, privater Pool, kein Schlafsaal, ebenerdig, Klimaanlage, Mindestgröße)
   *Warum: Diese werden zu Hard-Kriterien — alles was sie nicht erfüllt fällt raus.*

6. **Reisevibe & Wünsche**
   Was soll diese Reise sein? (Entspannung, Outdoor/Wandern, Kultur, Party, Familie, romantisch?)
   Was würde den Urlaub besonders machen? (Pool, Garten, Meerblick, Kamin, abgelegen, Stadtnähe, Grill, gute ÖPNV-Anbindung?)
   *Warum: Definiert die Soft-Kriterien und damit das Ranking der Suchergebnisse.*

### Output Schritt 1

**Urlaubsplanung — was ich noch brauche:**
[Kurz: welche Infos schon klar sind]

**Meine Fragen:**

1. [Frage]
   *[ein Satz warum das wichtig ist]*

[...]

---

## Schritt 2: Profil synthetisieren

Gilt, sobald User-Antworten auf alle Fragen vorliegen.

### 1. Antworten auswerten

Für jede Antwort:
- Extrahiere konkrete Anforderungen
- Klassifiziere als **Hard** (nicht verhandelbar) oder **Soft** (Wunsch/Ranking)

**Hard-Kriterium wenn:**
- User sagt explizit "muss", "ohne geht nicht", "absolut notwendig"
- Logisch nicht verhandelbar (Haustier mit → pet-friendly ist Hard; Rollstuhlfahrer → barrierefrei ist Hard)
- Budget-Obergrenze: immer Hard
- Mindest-Schlafkapazität: immer Hard

**Soft-Kriterium wenn:**
- User sagt "wäre schön", "ideal wäre", "würde ich bevorzugen"
- Komfort-Features (Pool, Garten, Meerblick, Kamin)
- Lage-Präferenzen die Abweichungen erlauben

### 1b. Offene Entscheidungen klären (vor dem Speichern)

Falls unklar ist, ob etwas Hard oder Soft ist, oder eine Pflichtangabe fehlt (Zeitraum, Ziel, Gruppe, Budget-Obergrenze): speichere nichts. Gib stattdessen nur die offenen Rückfragen aus, überschrieben mit `Rückfragen vor dem Speichern:`. Stelle sie dem User und führe Schritt 2 mit den ergänzten Antworten erneut aus.

### 2. Trip-Profil speichern

Speichere in `trips/[trip-name].md` (trip-name = Ziel + Monat + Jahr in Kleinbuchstaben mit Bindestrichen, Umlaute als ae/oe/ue, z.B. `toskana-august-2026`). Lege den Ordner `trips/` an, falls er fehlt. Existiert die Datei schon, frage vor dem Überschreiben nach (Rückfrage wie in 1b).

```markdown
# Trip: [Lesbarer Name]
Erstellt: [Datum]

## Reise
- Zeitraum: [Dates] ([N] Nächte)
- Ziel: [Ort/Region/Land]
- Gruppe: [Zusammensetzung]

## Budget
- Max: [N]€/Nacht (gesamt ca. [N]€)

## Hard-Kriterien (Deal-Breaker — filtert alles andere aus)
- Max. [N]€/Nacht
- Mindestens [N] Schlafplätze
- [nur Must-Haves, die der User genannt hat oder die logisch zwingend sind, z.B. eigene Küche, privat ohne geteilte Räume, pet-friendly]

## Soft-Kriterien (Ranking — je mehr, desto besser)
| Kriterium | Gewichtung |
|---|---|
| [Feature] | hoch / mittel / niedrig |

## Vibe & Zweck
[Ein–zwei Sätze: was soll dieser Urlaub sein]

## Such-Plattformen
- Airbnb
- Booking.com
- VRBO / HomeAway
- Lokale Anbieter (Google)
- [regionale Portale, falls bekannt: Tourismusverband, Ferienwohnungs-Portale der Region]

## Notizen
[Widersprüche, offene Punkte, Sonderanforderungen]
```

### Output Schritt 2

Zeige das gespeicherte Profil vollständig.
Schreibe danach: "Profil gespeichert. Soll ich jetzt auf Airbnb, Booking.com und im Web suchen?"
