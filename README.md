# Coach Billy Game Model

Interactive Streamlit app that presents Coach Darren Billy’s soccer game model and coaching philosophy portfolio for the Canada Soccer B Diploma.

## Features
- Interactive 11v11 tactical board with phase toggles
- Professional field visualization with zones and markings
- Player markers, profile cards, and role expectations
- Ball path and player-movement visualizations
- Step-by-step “Player & Ball Movement” progression board
- Structured game model content (philosophy, style, systems, tactics, behaviours)

## Quick Start

```bash
# (Optional) create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Validation

```bash
# Basic syntax validation
python -m py_compile app.py player_profiles.py

# Run tests
python -m unittest discover -v
```

## Project Structure

```text
coach-billy-game-model/
├── app.py
├── player_profiles.py
├── requirements.txt
├── tests/
│   └── test_player_profiles.py
└── README.md
```

## Author

Coach Darren Billy (Pickering FC)  
*Canada Soccer B Diploma Portfolio Project*
