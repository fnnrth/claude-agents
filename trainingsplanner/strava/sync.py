#!/usr/bin/env python3
"""
Strava → Markdown Sync für den Ultramarathon-Trainingsagenten.

Hinweis: Funktioniert aktuell nur mit Strava-Premium-Accounts.

Setup (einmalig):
  1. Jeder Athlet erstellt seine eigene kostenlose Strava-App:
     https://www.strava.com/settings/api
     → Application Name: beliebig (z.B. "Training Agent")
     → Website: http://localhost
     → Authorization Callback Domain: localhost
  2. Credentials in strava/.env eintragen (siehe .env.example), pro Athlet
     <NAME>_CLIENT_ID + <NAME>_CLIENT_SECRET. <name> entspricht dem Profil
     athletes/<name>.md.
  3. Auth je Athlet (aus dem Ordner trainingsplanner heraus):
       .venv/bin/python strava/sync.py --setup-<name>

Regulärer Sync:
  .venv/bin/python strava/sync.py
"""

import json
import os
import sys
import webbrowser
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

import requests

# ── Pfade ─────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(BASE_DIR, "strava", ".env")
REDIRECT_URI = "http://localhost:8282/callback"
SCOPE = "activity:read_all"
AUTH_TIMEOUT = 300  # Sekunden, die der Callback-Server auf Strava wartet
HTTP_TIMEOUT = 30

def athlete_cfg(name):
    p = name.upper()
    return {
        "output": os.path.join(BASE_DIR, "strava", f"{name}_activities.md"),
        "client_id_key": f"{p}_CLIENT_ID",
        "client_secret_key": f"{p}_CLIENT_SECRET",
        "token_key": f"{p}_REFRESH_TOKEN",
        "id_key": f"{p}_ATHLETE_ID",
    }

def athlete_names(env):
    return sorted(k[: -len("_CLIENT_ID")].lower() for k in env if k.endswith("_CLIENT_ID"))

# ── .env Helfer ───────────────────────────────────────────────────────────────

def load_env():
    env = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    env[k.strip()] = v.strip()
    return env

def save_env(env):
    # Kommentare und Reihenfolge der bestehenden .env bleiben erhalten; nur Werte werden ersetzt
    lines, seen = [], set()
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                k, sep, _ = line.partition("=")
                k = k.strip()
                if sep and not line.lstrip().startswith("#") and k in env:
                    line = f"{k}={env[k]}\n"
                    seen.add(k)
                lines.append(line)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    lines += [f"{k}={v}\n" for k, v in env.items() if k not in seen]
    with open(ENV_FILE, "w") as f:
        f.writelines(lines)

# ── OAuth ─────────────────────────────────────────────────────────────────────

_auth_code = None

class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        _auth_code = parse_qs(urlparse(self.path).query).get("code", [None])[0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"<h2>Autorisierung erfolgreich! Diesen Tab schliessen.</h2>")

    def log_message(self, *_):
        pass

def _get_auth_code(client_id):
    global _auth_code
    _auth_code = None
    url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={client_id}&response_type=code"
        f"&redirect_uri={REDIRECT_URI}&scope={SCOPE}&approval_prompt=force"
    )
    print("  Browser wird geöffnet — bitte Strava-Zugriff bestätigen.")
    print(f"  Falls sich kein Browser öffnet, diese URL aufrufen:\n  {url}")
    webbrowser.open(url)
    server = HTTPServer(("localhost", 8282), _CallbackHandler)
    server.timeout = AUTH_TIMEOUT
    server.handle_timeout = lambda: sys.exit(
        f"Fehler: nach {AUTH_TIMEOUT} s kein Callback von Strava erhalten. Setup erneut starten."
    )
    with server:
        server.handle_request()
    return _auth_code

def _exchange_code(client_id, client_secret, code):
    r = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": client_id, "client_secret": client_secret,
        "code": code, "grant_type": "authorization_code",
    }, timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    return r.json()

def _refresh(client_id, client_secret, refresh_tok):
    r = requests.post("https://www.strava.com/oauth/token", data={
        "client_id": client_id, "client_secret": client_secret,
        "refresh_token": refresh_tok, "grant_type": "refresh_token",
    }, timeout=HTTP_TIMEOUT)
    r.raise_for_status()
    return r.json()

# ── Strava API ────────────────────────────────────────────────────────────────

def fetch_activities(access_token, days=120):
    after = int((datetime.now(timezone.utc) - timedelta(days=days)).timestamp())
    activities, page = [], 1
    while True:
        r = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"after": after, "per_page": 100, "page": page},
            timeout=HTTP_TIMEOUT,
        )
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        activities.extend(batch)
        page += 1
    return activities

# ── Formatierung ──────────────────────────────────────────────────────────────

RUN_TYPES  = {"Run", "TrailRun", "Hike", "Walk", "VirtualRun"}
BIKE_TYPES = {"Ride", "MountainBikeRide", "VirtualRide", "GravelRide"}
ENDURANCE_TYPES = RUN_TYPES | BIKE_TYPES

def _pace(speed_ms, is_bike=False):
    if not speed_ms:
        return "—"
    if is_bike:
        kmh = speed_ms * 3.6
        return f"{kmh:.1f} km/h"
    s = 1000 / speed_ms
    return f"{int(s // 60)}:{int(s % 60):02d}"

def _dur(seconds):
    h, m = int(seconds // 3600), int((seconds % 3600) // 60)
    return f"{h}h{m:02d}" if h else f"{m}min"

def _week_num(dt, now):
    return (now - dt).days // 7

def _weekly_avg(activities, types, field="distance", scale=1/1000):
    now = datetime.now(timezone.utc)
    weekly = {}
    for a in activities:
        if a.get("sport_type", a.get("type")) not in types:
            continue
        dt = datetime.fromisoformat(a["start_date"].replace("Z", "+00:00"))
        w = _week_num(dt, now)
        if w < 8:
            weekly[w] = weekly.get(w, 0) + a.get(field, 0) * scale
    return round(sum(weekly.values()) / 8, 1)  # Wochen ohne Aktivität zählen als 0

def compute_stats(activities):
    runs  = [a for a in activities if a.get("sport_type", a.get("type")) in RUN_TYPES]
    bikes = [a for a in activities if a.get("sport_type", a.get("type")) in BIKE_TYPES]

    longest_run  = round(max((a.get("distance", 0) for a in runs),  default=0) / 1000, 1)
    longest_ride = round(max((a.get("distance", 0) for a in bikes), default=0) / 1000, 1)

    hrs = [a["average_heartrate"] for a in runs if a.get("average_heartrate")]
    avg_hr = round(sum(hrs) / len(hrs)) if hrs else None

    return {
        "run_avg_weekly_km":   _weekly_avg(activities, RUN_TYPES),
        "run_avg_weekly_vert": int(_weekly_avg(activities, RUN_TYPES, "total_elevation_gain", 1)),
        "run_longest_km":      longest_run,
        "run_count":           len(runs),
        "bike_avg_weekly_km":  _weekly_avg(activities, BIKE_TYPES),
        "bike_avg_weekly_vert":int(_weekly_avg(activities, BIKE_TYPES, "total_elevation_gain", 1)),
        "bike_longest_km":     longest_ride,
        "bike_count":          len(bikes),
        "avg_hr":              avg_hr,
    }

def write_markdown(name, activities, stats, path):
    all_act = sorted(
        [a for a in activities if a.get("sport_type", a.get("type")) in ENDURANCE_TYPES],
        key=lambda a: a["start_date"], reverse=True,
    )
    now = datetime.now()
    lines = [
        f"# Strava Aktivitäten — {name.capitalize()}",
        f"\n> Letzter Sync: {now.strftime('%d.%m.%Y %H:%M')} | Zeitraum: letzte 120 Tage\n",
        "## Fitness-Zusammenfassung (letzte 8 Wochen)\n",
        "### Laufen / Trail",
        "| Metrik | Wert |",
        "|---|---|",
        f"| Ø Wöchentliche km | **{stats['run_avg_weekly_km']} km** |",
        f"| Ø Wöchentliche Höhenmeter | **{stats['run_avg_weekly_vert']} m** |",
        f"| Längster Lauf (4 Monate) | **{stats['run_longest_km']} km** |",
        f"| Ø Herzfrequenz | {stats['avg_hr'] if stats['avg_hr'] else '—'} bpm |",
        f"| Anzahl Läufe gesamt | {stats['run_count']} |",
        "",
        "### Radfahren",
        "| Metrik | Wert |",
        "|---|---|",
        f"| Ø Wöchentliche km | **{stats['bike_avg_weekly_km']} km** |",
        f"| Ø Wöchentliche Höhenmeter | **{stats['bike_avg_weekly_vert']} m** |",
        f"| Längste Ausfahrt (4 Monate) | **{stats['bike_longest_km']} km** |",
        f"| Anzahl Ausfahrten gesamt | {stats['bike_count']} |",
        "",
        "## Aktivitäten\n",
        "| Datum | Name | Typ | km | Hm+ | Zeit | Pace/Speed | HR |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for a in all_act[:80]:
        dt = datetime.fromisoformat(a["start_date"].replace("Z", "+00:00"))
        sport = a.get("sport_type", a.get("type", "—"))
        is_bike = sport in BIKE_TYPES
        lines.append(
            f"| {dt.strftime('%d.%m.%y')} "
            f"| {a.get('name', '—')[:38]} "
            f"| {sport} "
            f"| {a.get('distance', 0)/1000:.1f} "
            f"| {int(a.get('total_elevation_gain', 0))} "
            f"| {_dur(a.get('moving_time', 0))} "
            f"| {_pace(a.get('average_speed'), is_bike)} "
            f"| {int(a['average_heartrate']) if a.get('average_heartrate') else '—'} |"
        )
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"  → {os.path.basename(path)} ({len(all_act)} Aktivitäten)")

# ── Setup & Sync ──────────────────────────────────────────────────────────────

def _athlete_credentials(name, env):
    cfg = athlete_cfg(name)
    cid = env.get(cfg["client_id_key"])
    csec = env.get(cfg["client_secret_key"])
    if not cid or not csec:
        print(f"Fehler: {cfg['client_id_key']} / {cfg['client_secret_key']} fehlen in strava/.env")
        sys.exit(1)
    return cid, csec

def setup_athlete(name, env):
    cid, csec = _athlete_credentials(name, env)
    print(f"\nSetup für {name.capitalize()}:")
    code = _get_auth_code(cid)
    if not code:
        print("Fehler: kein Auth-Code erhalten.")
        sys.exit(1)
    tokens = _exchange_code(cid, csec, code)
    cfg = athlete_cfg(name)
    env[cfg["token_key"]] = tokens["refresh_token"]
    env[cfg["id_key"]] = str(tokens.get("athlete", {}).get("id", ""))
    save_env(env)
    print(f"  ✓ {name.capitalize()} verbunden (ID: {env[cfg['id_key']]})")

def sync_athlete(name, env):
    cid, csec = _athlete_credentials(name, env)
    cfg = athlete_cfg(name)
    rtok = env.get(cfg["token_key"])
    if not rtok:
        print(f"  {name.capitalize()}: kein Token — Setup ausführen: {sys.executable} {sys.argv[0]} --setup-{name}")
        return None
    print(f"  {name.capitalize()}: Sync läuft...")
    try:
        tokens = _refresh(cid, csec, rtok)
    except requests.HTTPError as e:
        print(f"Fehler: Strava lehnt den Refresh-Token von {name.capitalize()} ab "
              f"(HTTP {e.response.status_code}). Token ungültig oder widerrufen.")
        print(f"  Neu verbinden: {sys.executable} {sys.argv[0]} --setup-{name}")
        sys.exit(1)
    env[cfg["token_key"]] = tokens["refresh_token"]
    save_env(env)  # Strava rotiert den Refresh-Token; sofort sichern, falls ein späterer Schritt scheitert
    activities = fetch_activities(tokens["access_token"])
    stats = compute_stats(activities)
    write_markdown(name, activities, stats, cfg["output"])
    return stats

def main():
    env = load_env()
    for arg in sys.argv[1:]:
        if arg.startswith("--setup-"):
            setup_athlete(arg[len("--setup-"):].lower(), env)
            return
    names = athlete_names(env)
    if not names:
        print("Fehler: strava/.env nicht konfiguriert. Siehe strava/.env.example")
        sys.exit(1)
    print("Strava Sync —", datetime.now().strftime("%d.%m.%Y %H:%M"))
    missing = []
    for name in names:
        try:
            if sync_athlete(name, env) is None:
                missing.append(name)
        except requests.RequestException as e:
            print(f"Fehler: Strava nicht erreichbar ({type(e).__name__}). Netzwerk prüfen und erneut starten.")
            sys.exit(1)
    save_env(env)
    if missing:
        print(f"✗ Nicht synchronisiert: {', '.join(missing)}")
        sys.exit(1)
    print("✓ Fertig.")

if __name__ == "__main__":
    main()
