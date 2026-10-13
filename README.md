# Claude Agents

Three sets of Claude Code subagents, each in its own folder with its own router (`AGENT.md`), README and setup steps. The prompts and the agents' output are in German.

| Folder | What it does |
|---|---|
| [`trainingsplanner/`](trainingsplanner/) | Coaches one or more athletes towards a trail ultra, with training plans built from Strava data |
| [`shoppinghelper/`](shoppinghelper/) | Turns a purchase idea into a ranked product list checked against a personal profile |
| [`pensionfinder/`](pensionfinder/) | Finds holiday rentals on Booking.com, Airbnb and the open web and returns a Top 5 |

## Usage

Start Claude Code in the repository root. The root [`CLAUDE.md`](CLAUDE.md) routes each request to the matching `AGENT.md`. Each folder also works on its own; see its README for setup.

Personal data (athlete profiles, shopping preferences, trip profiles) stays local. Each folder's `.gitignore` excludes it and ships an `*.example.md` template instead.

## License

[MIT](LICENSE)
