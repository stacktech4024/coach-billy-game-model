# Coach Billy Game Model

This repository contains an interactive, web-based soccer game model and coaching philosophy portfolio for Coach Darren Billy's Canada Soccer B Diploma.

## Features
- Visual interactive 1-4-4-2 formation diagram (select players by standard soccer number)
- Separate detailed positional profile for each player (1-11)
- Summary of Coach Billy's game model, philosophy, style of play, and coaching principles
- Modular, extensible code ready for additional analytics, numpy integrations, and advanced soccer visualization

## Quick Start

### Local (Recommended)
```bash
# Install dependencies (prefer venv)
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

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
