import streamlit as st
import plotly.graph_objects as go

from player_profiles import (
    PITCH_BOUNDS,
    get_game_model,
    get_phase_config,
    get_phase_keys,
    get_player_profile,
    get_player_profiles,
)

st.set_page_config(page_title="Coach Billy Game Model", layout="wide")

COLORS = {
    "pitch_base": "#2e7d32",
    "pitch_stripe_dark": "#2f8f3a",
    "pitch_stripe_light": "#3ca34a",
    "line": "#f5f5f5",
    "our_team": "#00c2ff",
    "our_glow": "rgba(0,194,255,0.25)",
    "opp_team": "#ff6b6b",
    "ball": "#f8f9fa",
    "zone": "rgba(255, 255, 255, 0.08)",
}

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.3rem;}
    [data-testid="stMetricValue"] {font-size: 1.1rem;}
    .info-card {
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 12px;
        padding: 14px;
        background: linear-gradient(145deg, rgba(30,40,60,0.9), rgba(20,26,40,0.9));
        box-shadow: 0 4px 14px rgba(0,0,0,0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _pitch_shapes():
    """Build the base pitch drawing as Plotly shape definitions."""
    length = PITCH_BOUNDS["length"]
    width = PITCH_BOUNDS["width"]
    center_x = length / 2
    center_y = width / 2
    center_circle_radius = 8
    penalty_area_depth = 16
    goal_area_depth = 5
    penalty_spot_distance = 11
    penalty_area_y0 = 14
    penalty_area_y1 = 50
    goal_area_y0 = 24
    goal_area_y1 = 40

    shapes = [
        dict(type="rect", x0=0, y0=0, x1=length, y1=width, fillcolor=COLORS["pitch_base"], line=dict(width=0))
    ]

    stripe_count = 10
    stripe_w = length / stripe_count
    for idx in range(stripe_count):
        shapes.append(
            dict(
                type="rect",
                x0=idx * stripe_w,
                y0=0,
                x1=(idx + 1) * stripe_w,
                y1=width,
                fillcolor=COLORS["pitch_stripe_light"] if idx % 2 == 0 else COLORS["pitch_stripe_dark"],
                line=dict(width=0),
                layer="below",
            )
        )

    line_style = dict(color=COLORS["line"], width=2)
    shapes.extend(
        [
            dict(type="rect", x0=0, y0=0, x1=length, y1=width, line=line_style, fillcolor="rgba(0,0,0,0)"),
            dict(type="line", x0=center_x, y0=0, x1=center_x, y1=width, line=line_style),
            dict(
                type="circle",
                x0=center_x - center_circle_radius,
                y0=center_y - center_circle_radius,
                x1=center_x + center_circle_radius,
                y1=center_y + center_circle_radius,
                line=line_style,
            ),
            dict(
                type="circle",
                x0=center_x - 1,
                y0=center_y - 1,
                x1=center_x + 1,
                y1=center_y + 1,
                line=dict(color=COLORS["line"], width=2),
                fillcolor=COLORS["line"],
            ),
            dict(type="rect", x0=0, y0=penalty_area_y0, x1=penalty_area_depth, y1=penalty_area_y1, line=line_style, fillcolor="rgba(0,0,0,0)"),
            dict(type="rect", x0=length - penalty_area_depth, y0=penalty_area_y0, x1=length, y1=penalty_area_y1, line=line_style, fillcolor="rgba(0,0,0,0)"),
            dict(type="rect", x0=0, y0=goal_area_y0, x1=goal_area_depth, y1=goal_area_y1, line=line_style, fillcolor="rgba(0,0,0,0)"),
            dict(type="rect", x0=length - goal_area_depth, y0=goal_area_y0, x1=length, y1=goal_area_y1, line=line_style, fillcolor="rgba(0,0,0,0)"),
            dict(
                type="circle",
                x0=penalty_spot_distance - 0.5,
                y0=center_y - 0.5,
                x1=penalty_spot_distance + 0.5,
                y1=center_y + 0.5,
                line=dict(color=COLORS["line"], width=2),
                fillcolor=COLORS["line"],
            ),
            dict(
                type="circle",
                x0=length - penalty_spot_distance - 0.5,
                y0=center_y - 0.5,
                x1=length - penalty_spot_distance + 0.5,
                y1=center_y + 0.5,
                line=dict(color=COLORS["line"], width=2),
                fillcolor=COLORS["line"],
            ),
            dict(type="rect", x0=-1, y0=28, x1=0, y1=36, line=line_style, fillcolor="rgba(0,0,0,0)"),
            dict(type="rect", x0=length, y0=28, x1=length + 1, y1=36, line=line_style, fillcolor="rgba(0,0,0,0)"),
        ]
    )
    return shapes


def _add_zone_overlays(fig):
    """Add four labeled pitch geography zones onto an existing Plotly figure."""
    for start in [0, 25, 50, 75]:
        fig.add_shape(
            type="rect",
            x0=start,
            y0=0,
            x1=start + 25,
            y1=64,
            fillcolor=COLORS["zone"],
            line=dict(width=0),
        )
    for start, label in zip([0, 25, 50, 75], ["Zone 1", "Zone 2", "Zone 3", "Zone 4"]):
        fig.add_annotation(x=start + 12.5, y=62, text=label, showarrow=False, font=dict(color="white", size=10))


def _build_tactical_figure(phase_key, selected_player=None, step_index=None):
    """Create an 11v11 tactical board for a phase with optional focus player and step index."""
    phase = get_phase_config(phase_key)
    profiles = get_player_profiles()

    fig = go.Figure()
    fig.update_layout(shapes=_pitch_shapes())

    our_numbers = sorted(phase["our_positions"].keys())
    our_x = [phase["our_positions"][num][0] for num in our_numbers]
    our_y = [phase["our_positions"][num][1] for num in our_numbers]

    marker_sizes = [20 if selected_player == num else 15 for num in our_numbers]
    fig.add_trace(
        go.Scatter(
            x=our_x,
            y=our_y,
            mode="markers+text",
            text=[str(n) for n in our_numbers],
            textposition="middle center",
            textfont=dict(color="white", size=11),
            marker=dict(color=COLORS["our_team"], size=marker_sizes, line=dict(color="white", width=1.5)),
            customdata=[
                [
                    f"#{num}",
                    profiles[num]["name"],
                    profiles[num]["position_title"],
                    profiles[num]["role_summary"],
                ]
                for num in our_numbers
            ],
            hovertemplate="<b>%{customdata[0]} %{customdata[1]}</b><br>%{customdata[2]}<br>%{customdata[3]}<extra>Coach Billy XI</extra>",
            name="Coach Billy XI",
        )
    )

    if selected_player in phase["our_positions"]:
        x, y = phase["our_positions"][selected_player]
        fig.add_trace(
            go.Scatter(
                x=[x],
                y=[y],
                mode="markers",
                marker=dict(size=33, color=COLORS["our_glow"], line=dict(width=0)),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    opp_numbers = sorted(phase["opposition_positions"].keys())
    fig.add_trace(
        go.Scatter(
            x=[phase["opposition_positions"][num][0] for num in opp_numbers],
            y=[phase["opposition_positions"][num][1] for num in opp_numbers],
            mode="markers+text",
            text=[str(n) for n in opp_numbers],
            textposition="middle center",
            textfont=dict(color="white", size=11),
            marker=dict(color=COLORS["opp_team"], size=15, line=dict(color="white", width=1.5)),
            hovertemplate="<b>Opposition #%{text}</b><extra>Opposition XI</extra>",
            name="Opposition XI",
        )
    )

    ball_path = phase["ball_path"]
    if step_index is None:
        step_index = len(ball_path) - 1
    step_index = max(0, min(step_index, len(ball_path) - 1))
    visible_ball_path = ball_path[: step_index + 1]

    fig.add_trace(
        go.Scatter(
            x=[pt[0] for pt in visible_ball_path],
            y=[pt[1] for pt in visible_ball_path],
            mode="lines+markers",
            line=dict(color="#ffd166", width=3, dash="dot"),
            marker=dict(size=6, color="#ffd166"),
            hoverinfo="skip",
            name="Ball path",
        )
    )

    bx, by = visible_ball_path[-1]
    fig.add_trace(
        go.Scatter(
            x=[bx],
            y=[by],
            mode="text",
            text=["⚽"],
            textfont=dict(size=24),
            hovertemplate="Ball location<extra></extra>",
            name="Ball",
            showlegend=False,
        )
    )

    arrow_palette = {"our": "#66e3ff", "opp": "#ff9b9b"}
    arrows_to_show = phase["movement_arrows"]
    if step_index is not None and len(arrows_to_show) > 1:
        arrows_to_show = arrows_to_show[: min(step_index + 1, len(arrows_to_show))]

    for arrow in arrows_to_show:
        fig.add_annotation(
            x=arrow["end"][0],
            y=arrow["end"][1],
            ax=arrow["start"][0],
            ay=arrow["start"][1],
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=arrow_palette[arrow["team"]],
            text=arrow["label"],
            font=dict(color="white", size=10),
            bgcolor="rgba(0,0,0,0.3)",
        )

    fig.update_layout(
        xaxis=dict(range=[-1, 101], visible=False),
        yaxis=dict(range=[-1, 65], visible=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor="#1f2f2b",
        paper_bgcolor="#0f172a",
        margin=dict(l=6, r=6, t=6, b=6),
        legend=dict(orientation="h", y=1.03, x=0),
    )
    return fig


def _render_player_card(player_number):
    """Render the selected player's profile card, skill set list, and tactical expectations."""
    profile = get_player_profile(player_number)
    if not profile:
        return

    st.markdown(
        f"""
        <div class="info-card">
            <h4 style="margin:0 0 6px 0;">#{player_number} • {profile['name']}</h4>
            <p style="margin:0; opacity:0.9;"><strong>{profile['position_title']}</strong> — {profile['role_summary']}</p>
            <p style="margin-top:10px; opacity:0.92;">{profile['bio_role']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        st.markdown("**Key Skill Sets**")
        for item in profile["key_skills"]:
            st.markdown(f"- {item}")
    with right:
        st.markdown("**Tactical Expectations**")
        for item in profile["tactical_expectations"]:
            st.markdown(f"- {item}")


def _render_game_model_page(selected_player):
    """Render full game-model content and positional spotlight for the selected player."""
    gm = get_game_model()

    st.title("Coach Billy Game Model")
    st.caption("Canada Soccer B Diploma tactical model with phase-based visuals and interactive positional detail.")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Who We Are")
        st.markdown(f"**Club Philosophy:** {gm['who_we_are']['club_philosophy']}")
        st.markdown(f"**Club Guiding Principles:** {gm['who_we_are']['club_guiding_principles']}")
        st.markdown(f"**Coaching Philosophy:** {gm['who_we_are']['coaching_philosophy']}")

        st.subheader("How Do We Coach?")
        st.markdown(f"**Training Design Principles:** {gm['how_do_we_coach']['training_design_principles']}")
        st.markdown(f"**Preferred Practice Methodologies:** {gm['how_do_we_coach']['preferred_practice_methodologies']}")
        st.markdown(f"**Preferred Coaching Approaches:** {gm['how_do_we_coach']['preferred_coaching_approaches']}")

    with col_b:
        st.subheader("How We Want to Play")
        st.markdown(f"**Style of Play:** {gm['how_we_want_to_play']['style_of_play']}")
        st.markdown("**Moments of the Game:**")
        for moment in gm["how_we_want_to_play"]["moments_of_the_game"]:
            st.markdown(f"- {moment}")
        st.markdown(f"**Pitch Geography:** {gm['how_we_want_to_play']['pitch_geography']}")
        st.markdown("**Systems:**")
        for system in gm["how_we_want_to_play"]["systems"]:
            st.markdown(f"- {system}")
        st.markdown("**Strategies:**")
        for strategy in gm["how_we_want_to_play"]["strategies"]:
            st.markdown(f"- {strategy}")
        st.markdown("**Tactics:**")
        for tactic in gm["how_we_want_to_play"]["tactics"]:
            st.markdown(f"- {tactic}")

    st.subheader("Pitch Geography")
    zone_fig = go.Figure()
    zone_fig.update_layout(shapes=_pitch_shapes())
    _add_zone_overlays(zone_fig)
    zone_fig.update_layout(
        xaxis=dict(range=[-1, 101], visible=False),
        yaxis=dict(range=[-1, 65], visible=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor="#1f2f2b",
        paper_bgcolor="#0f172a",
        margin=dict(l=6, r=6, t=6, b=6),
    )
    st.plotly_chart(zone_fig, use_container_width=True, config={"displayModeBar": False})

    st.subheader("Future Canadian Player: Skill Sets / Behaviours")
    st.markdown("\n".join([f"- {item}" for item in gm["future_canadian_player"]["skill_sets_player_behaviours"]]))

    st.subheader("Positional Profile Spotlight")
    _render_player_card(selected_player)


def _render_tactical_board_page(selected_player):
    """Render tabbed tactical boards for each game phase using a shared player focus."""
    st.title("Dynamic Tactical Board")
    st.caption("11v11 phase views with differentiated teams, tactical movement arrows, and ball-flow visualization.")

    phase_keys = get_phase_keys()
    tabs = st.tabs([get_phase_config(key)["title"] for key in phase_keys])

    for tab, phase_key in zip(tabs, phase_keys):
        with tab:
            phase = get_phase_config(phase_key)
            st.markdown(f"**System:** {phase['our_system']}  ")
            st.markdown(f"{phase['description']}")
            fig = _build_tactical_figure(phase_key, selected_player=selected_player)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            _render_player_card(selected_player)


def _render_movement_board_page(selected_player):
    """Render stepwise player-and-ball movement progression for a selected phase."""
    st.title("Player & Ball Movement")
    st.caption("Stepwise tactical progression showing team movement, pressing reactions, and ball advancement.")

    phase_options = {get_phase_config(key)["title"]: key for key in get_phase_keys()}
    selected_phase_title = st.selectbox("Select phase", list(phase_options.keys()))
    phase_key = phase_options[selected_phase_title]
    phase = get_phase_config(phase_key)

    max_step = len(phase["ball_path"]) - 1
    step = st.slider("Stepwise progression", min_value=0, max_value=max_step, value=0)

    fig = _build_tactical_figure(phase_key, selected_player=selected_player, step_index=step)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    if step == 0:
        st.info("Step 1: Initial phase shape and first pass/press trigger.")
    elif step == max_step:
        st.success("Final step: completion of the tactical sequence for this phase.")
    else:
        st.warning("Intermediate step: shape adaptation and support movement in progress.")

    _render_player_card(selected_player)


all_profiles = get_player_profiles()
player_options = sorted(all_profiles.keys())

with st.sidebar:
    st.header("Navigation")
    selected_page = st.radio(
        "Go to",
        ["Game Model", "Dynamic Tactical Board", "Player & Ball Movement"],
    )
    selected_player = st.selectbox(
        "Player focus",
        options=player_options,
        format_func=lambda number: f"#{number} - {all_profiles[number]['position_title']} ({all_profiles[number]['name']})",
    )

if selected_page == "Game Model":
    _render_game_model_page(selected_player)
elif selected_page == "Dynamic Tactical Board":
    _render_tactical_board_page(selected_player)
else:
    _render_movement_board_page(selected_player)
