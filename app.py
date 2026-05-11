import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from player_profiles import get_game_model, get_player_profile

st.set_page_config(
    page_title="Coach Billy Game Model",
    layout="wide"
)

game_model = get_game_model()

st.title("Coach Billy Game Model (Canada Soccer B Diploma)")
st.markdown("""
#### Club Philosophy
- **Philosophy:**  
{philosophy}
- **Guiding Principles:**  
{club_guiding_principles}

#### Coaching Philosophy
{coaching_philosophy}

#### Training Design / Methodology
{training_design_principles}

#### Style of Play
- **Typical Formation (Attacking):** {systems[0]}  
- **Defensive Shape:** {systems[1]}
- **Style:** {style_of_play}

#### Strategies
- {strategy0}
- {strategy1}

#### Tactics
- {tactic0}
- {tactic1}
- {tactic2}
""".format(
    philosophy=game_model['philosophy'],
    club_guiding_principles=game_model['club_guiding_principles'],
    coaching_philosophy=game_model['coaching_philosophy'],
    training_design_principles=game_model['training_design_principles'],
    systems=game_model['systems'],
    style_of_play=game_model['style_of_play'],
    strategy0=game_model['strategies'][0],
    strategy1=game_model['strategies'][1],
    tactic0=game_model['tactics'][0],
    tactic1=game_model['tactics'][1],
    tactic2=game_model['tactics'][2],
))

st.divider()
st.header("Interactive Formation Diagram")

# Draw the soccer pitch & formation
fig, ax = plt.subplots(figsize=(9, 6))
# Draw pitch outline
ax.plot([0, 0, 100, 100, 0], [0, 64, 64, 0, 0], color="black")
ax.set_aspect('equal')
ax.axis('off')

# Define default 1-4-4-2 positions: (x, y, number)
formation = [
    (5, 32, 1),        # Goalkeeper
    (20, 53, 2),       # Right Full Back
    (20, 11, 3),       # Left Full Back
    (16, 37, 4),       # Right Center Back
    (16, 27, 5),       # Left Center Back
    (35, 44, 6),       # Defensive Mid (right)
    (35, 20, 8),       # Central Mid (left)
    (52, 54, 7),       # Right Wide Forward
    (52, 10, 11),      # Left Wide Forward
    (70, 36, 10),      # Attacking Midfielder
    (85, 32, 9),       # Center Forward
]
# Place buttons for each player
selected_player = None
for x, y, num in formation:
    if st.sidebar.button(f"Select #{num} - {get_player_profile(num)['name']}"):
        selected_player = num
    # Draw player on field
    circle = plt.Circle((x, y), 2.2, color='dodgerblue' if selected_player==num else 'grey', zorder=6)
    ax.add_patch(circle)
    ax.text(x, y, str(num), color="white", weight="bold", ha="center", va="center", fontsize=12)

st.pyplot(fig)

# Detail panel
if selected_player:
    profile = get_player_profile(selected_player)
    st.subheader(f"#{selected_player}: {profile['name']}")
    st.markdown(f"**Role:** {profile['profile']}")
else:
    st.info("Select a player position in the sidebar to see their role and bio.")
