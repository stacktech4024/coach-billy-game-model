# Coach Billy Game Model

This repository contains an interactive, web-based soccer game model and coaching philosophy portfolio for Coach Darren Billy's Canada Soccer B Diploma.

## Features
- Advanced interactive 11v11 tactical board with phase toggles
- Professional soccer field visualization with full markings, grass-striping, and zone overlays
- Interactive player markers with jersey numbers, team colors, and focused player highlight/glow
- Integrated player info card with profile, tactical expectations, and key skill sets
- Ball path and movement-arrow visualizations for attacking/defending organizations and transitions
- Dedicated stepwise “Player & Ball Movement” board for frame-by-frame tactical progression
- Full game model content sections (philosophy, methodology, style, systems, strategies, tactics, behaviours)

## Quick Start

### Local (Recommended)
```bash
# Install dependencies (prefer venv)
pip install -r requirements.txt

# Run the app
streamlit run app.py
```
python3 -m streamlit run app.py
### Deployment
- **Streamlit Community Cloud:** One-click deploy from this repo for free public hosting.
- **Vercel or Other Cloud Providers:** Use a Dockerfile or adapters if you want advanced routing/pages.

## Project Structure
```
coach-billy-game-model/
├── app.py              # Main Streamlit app (entry point)
├── player_profiles.py  # Player profile and game model logic
├── requirements.txt    # Python dependencies
└── README.md
```

## Author
Coach Darren Billy (Pickering FC)

*Canada Soccer B Diploma Portfolio Project*
