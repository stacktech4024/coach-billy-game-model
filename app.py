import streamlit as st

try:
    import plotly.graph_objects as go
except ModuleNotFoundError:
    st.error(
        """Missing dependency: plotly\n\nInstall with:\n\n    pip install plotly==5.24.1"""
    )
    st.stop()

from player_profiles import (
    PITCH_BOUNDS,
    get_game_model,
    get_phase_config,
    get_phase_keys,
    get_player_movement_positions,
    get_player_profile,
    get_player_profiles,
)

st.set_page_config(page_title="Coach Billy Game Model", layout="wide")

# ---------------------------------------------------------------------------
# DESIGN TOKENS
# ---------------------------------------------------------------------------
COLORS = {
    # Pitch surface — deep, rich grass green with subtle stripe contrast
    "pitch_base":         "#1a6b2e",
    "pitch_stripe_dark":  "#1a6b2e",
    "pitch_stripe_light": "#1f7d35",
    # Lines — bright white for visibility
    "line":               "#ffffff",
    "line_thin":          "rgba(255,255,255,0.85)",
    # Teams
    "our_team":           "#00c2ff",
    "opp_team":           "#ff5555",
    "highlight":          "#facc15",
    # Ball path
    "ball_path":          "#ffd166",
    # Movement arrows
    "arrow_our":          "#66e8ff",
    "arrow_opp":          "#ff9b9b",
    # UI
    "bg_dark":            "#0b1120",
    "bg_panel":           "#111827",
    "card_border":        "rgba(255,255,255,0.12)",
}

ANIMATION_FRAME_DURATION_MS      = 900
ANIMATION_TRANSITION_DURATION_MS = 250
ANIMATION_PAUSE_DURATION_MS      = 0

# ---------------------------------------------------------------------------
# GLOBAL CSS
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700&family=Barlow:wght@400;500&display=swap');

    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {COLORS["bg_dark"]};
        font-family: 'Barlow', sans-serif;
    }}
    .block-container {{ padding-top: 1.2rem; }}
    h1, h2, h3, h4 {{
        font-family: 'Barlow Condensed', sans-serif;
        letter-spacing: 0.03em;
    }}
    [data-testid="stMetricValue"] {{ font-size: 1.1rem; }}

    .info-card {{
        border: 1px solid {COLORS["card_border"]};
        border-radius: 10px;
        padding: 16px 18px;
        background: linear-gradient(135deg, rgba(17,24,39,0.95), rgba(10,15,28,0.95));
        box-shadow: 0 4px 20px rgba(0,0,0,0.35);
        margin-bottom: 12px;
    }}
    .phase-badge {{
        display: inline-block;
        background: rgba(0,194,255,0.15);
        border: 1px solid rgba(0,194,255,0.4);
        border-radius: 6px;
        padding: 3px 10px;
        font-size: 0.78rem;
        color: #00c2ff;
        font-family: 'Barlow Condensed', sans-serif;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# PITCH DRAWING — realistic stadium grass with stripes, markings, goals
# ---------------------------------------------------------------------------

def _pitch_shapes():
    """Build the base pitch as Plotly shape definitions.

    Pitch dimensions use PITCH_BOUNDS (100×64 normalized units).
    Standard proportions:
      Penalty area: 16.5m deep × 40.3m wide  →  ~16.5 × 40 units
      Goal area:     5.5m deep × 18.3m wide   →  ~5.5  × 18 units
      Centre circle radius: 9.15m             →  ~9 units
      Penalty spot: 11m from goal line        →  11 units
    """
    length = PITCH_BOUNDS["length"]
    width  = PITCH_BOUNDS["width"]
    cx     = length / 2
    cy     = width  / 2

    # FIFA proportional measurements (scaled to 100×64)
    pen_depth  = 16.5
    pen_y0     = (width - 40.3) / 2       # ~11.85
    pen_y1     = width - pen_y0           # ~52.15
    ga_depth   = 5.5
    ga_y0      = (width - 18.3) / 2       # ~22.85
    ga_y1      = width - ga_y0            # ~41.15
    cc_r       = 9.0                      # centre circle radius
    pen_spot   = 11.0
    corner_r   = 1.0

    line_style = dict(color=COLORS["line"], width=2)

    shapes = []

    # --- Grass base ---
    shapes.append(dict(
        type="rect", x0=0, y0=0, x1=length, y1=width,
        fillcolor=COLORS["pitch_base"], line=dict(width=0),
    ))

    # --- Alternating grass stripes (stadium mowing effect) ---
    stripe_count = 10
    stripe_w = length / stripe_count
    for idx in range(stripe_count):
        shapes.append(dict(
            type="rect",
            x0=idx * stripe_w, y0=0,
            x1=(idx + 1) * stripe_w, y1=width,
            fillcolor=COLORS["pitch_stripe_light"] if idx % 2 == 0 else COLORS["pitch_stripe_dark"],
            line=dict(width=0),
            layer="below",
        ))

    # --- Touchlines & halfway ---
    shapes.extend([
        # Outer boundary
        dict(type="rect", x0=0, y0=0, x1=length, y1=width,
             line=line_style, fillcolor="rgba(0,0,0,0)"),
        # Halfway line
        dict(type="line", x0=cx, y0=0, x1=cx, y1=width, line=line_style),
    ])

    # --- Centre circle ---
    shapes.append(dict(
        type="circle",
        x0=cx - cc_r, y0=cy - cc_r, x1=cx + cc_r, y1=cy + cc_r,
        line=line_style, fillcolor="rgba(0,0,0,0)",
    ))
    # Centre spot
    shapes.append(dict(
        type="circle",
        x0=cx - 0.6, y0=cy - 0.6, x1=cx + 0.6, y1=cy + 0.6,
        line=dict(color=COLORS["line"], width=1), fillcolor=COLORS["line"],
    ))

    # --- Penalty areas (both ends) ---
    for x0, x1 in [(0, pen_depth), (length - pen_depth, length)]:
        shapes.append(dict(
            type="rect", x0=x0, y0=pen_y0, x1=x1, y1=pen_y1,
            line=line_style, fillcolor="rgba(255,255,255,0.04)",
        ))

    # --- Goal areas (both ends) ---
    for x0, x1 in [(0, ga_depth), (length - ga_depth, length)]:
        shapes.append(dict(
            type="rect", x0=x0, y0=ga_y0, x1=x1, y1=ga_y1,
            line=line_style, fillcolor="rgba(0,0,0,0)",
        ))

    # --- Penalty spots ---
    for px in [pen_spot, length - pen_spot]:
        shapes.append(dict(
            type="circle",
            x0=px - 0.5, y0=cy - 0.5, x1=px + 0.5, y1=cy + 0.5,
            line=dict(color=COLORS["line"], width=1), fillcolor=COLORS["line"],
        ))

    # --- Penalty arcs (D arcs outside penalty areas) ---
    # Left penalty arc
    shapes.append(dict(
        type="circle",
        x0=pen_spot - cc_r, y0=cy - cc_r,
        x1=pen_spot + cc_r, y1=cy + cc_r,
        line=dict(color=COLORS["line_thin"], width=1.5, dash="solid"),
        fillcolor="rgba(0,0,0,0)",
    ))
    # Right penalty arc
    shapes.append(dict(
        type="circle",
        x0=(length - pen_spot) - cc_r, y0=cy - cc_r,
        x1=(length - pen_spot) + cc_r, y1=cy + cc_r,
        line=dict(color=COLORS["line_thin"], width=1.5, dash="solid"),
        fillcolor="rgba(0,0,0,0)",
    ))

    # --- Corner arcs (quarter-circles, radius 1) ---
    for (x0, x1, y0, y1) in [
        (0-corner_r, corner_r, 0-corner_r, corner_r),
        (0-corner_r, corner_r, width-corner_r, width+corner_r),
        (length-corner_r, length+corner_r, 0-corner_r, corner_r),
        (length-corner_r, length+corner_r, width-corner_r, width+corner_r),
    ]:
        shapes.append(dict(
            type="circle",
            x0=x0, y0=y0, x1=x1, y1=y1,
            line=dict(color=COLORS["line"], width=1.5),
            fillcolor="rgba(0,0,0,0)",
        ))

    # --- Goals (posts behind goal line) ---
    goal_post_depth = 2.5
    goal_y0 = cy - 3.7
    goal_y1 = cy + 3.7
    for gx0, gx1 in [(-goal_post_depth, 0), (length, length + goal_post_depth)]:
        shapes.append(dict(
            type="rect", x0=gx0, y0=goal_y0, x1=gx1, y1=goal_y1,
            line=dict(color=COLORS["line"], width=2),
            fillcolor="rgba(255,255,255,0.08)",
        ))

    return shapes


def _base_pitch_layout(show_legend=True):
    """Return common layout settings for all tactical figures."""
    return dict(
        xaxis=dict(range=[-4, 104], visible=False),
        yaxis=dict(range=[-3, 67], visible=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor=COLORS["pitch_base"],
        paper_bgcolor=COLORS["bg_panel"],
        margin=dict(l=6, r=6, t=6, b=6),
        legend=dict(orientation="h", y=1.04, x=0, font=dict(color="white")) if show_legend else dict(visible=False),
        hoverlabel=dict(
            bgcolor="rgba(10,15,28,0.92)",
            bordercolor="rgba(255,255,255,0.2)",
            font=dict(color="white", size=12),
        ),
    )


def _add_zone_overlays(fig):
    """Add four labeled pitch geography zones (vertical bands)."""
    zone_colors = [
        "rgba(255,255,255,0.04)",
        "rgba(255,255,255,0.02)",
        "rgba(255,255,255,0.04)",
        "rgba(255,255,255,0.07)",
    ]
    for idx, (start, label) in enumerate(zip([0, 25, 50, 75], ["Zone 1\nDefensive Third", "Zone 2", "Zone 3", "Zone 4\nAttacking Third"])):
        fig.add_shape(
            type="rect", x0=start, y0=0, x1=start + 25, y1=64,
            fillcolor=zone_colors[idx], line=dict(width=0),
        )
        fig.add_annotation(
            x=start + 12.5, y=62, text=label.split("\n")[0],
            showarrow=False, font=dict(color="rgba(255,255,255,0.5)", size=9),
        )


def _build_pitch_geography_figure():
    """Build a dedicated pitch geography figure showing zones and channels."""
    fig = go.Figure()
    fig.update_layout(shapes=_pitch_shapes())
    _add_zone_overlays(fig)
    # Horizontal channels
    channel_height = 64 / 5
    for idx in range(1, 5):
        fig.add_shape(
            type="line", x0=0, y0=idx * channel_height, x1=100, y1=idx * channel_height,
            line=dict(color="rgba(255,255,255,0.25)", width=1, dash="dash"),
        )
    for idx, label in enumerate(["Channel 1", "Channel 2", "Channel 3", "Channel 4", "Channel 5"]):
        fig.add_annotation(
            x=3, y=(idx * channel_height) + (channel_height / 2),
            text=label, showarrow=False,
            font=dict(color="rgba(255,255,255,0.6)", size=9),
            xanchor="left",
        )
    fig.update_layout(**_base_pitch_layout(show_legend=False))
    return fig


def _build_moments_flow_figure():
    """Build an interactive flow diagram showing moments-of-the-game connectivity."""
    moments = get_game_model()["how_we_want_to_play"]["moments_of_the_game"]
    points = [(15, 50), (50, 85), (85, 50), (50, 15)]
    if len(moments) != 4:
        points = [
            (10 + idx * (80 / max(len(moments) - 1, 1)), 50)
            for idx in range(len(moments))
        ]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[pt[0] for pt in points],
        y=[pt[1] for pt in points],
        mode="markers+text",
        text=moments,
        textposition="middle center",
        marker=dict(size=52, color="#1d4ed8", line=dict(color="#93c5fd", width=2)),
        hovertemplate="%{text}<extra>Moment</extra>",
        showlegend=False,
    ))
    for idx in range(len(points)):
        start, end = points[idx], points[(idx + 1) % len(points)]
        fig.add_annotation(
            x=end[0], y=end[1], ax=start[0], ay=start[1],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3, arrowsize=1.2, arrowwidth=2,
            arrowcolor="#93c5fd", text="",
        )
    fig.update_layout(
        xaxis=dict(range=[0, 100], visible=False),
        yaxis=dict(range=[0, 100], visible=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=6, r=6, t=6, b=6),
        plot_bgcolor=COLORS["bg_panel"],
        paper_bgcolor=COLORS["bg_panel"],
    )
    return fig


# ---------------------------------------------------------------------------
# TACTICAL FIGURE BUILDER
# ---------------------------------------------------------------------------

def _build_tactical_figure(
    phase_key,
    selected_player=None,
    step_index=None,
    selected_player_position=None,
    selected_player_path=None,
):
    """Create an 11v11 tactical board for a phase with optional focus player and step."""
    phase    = get_phase_config(phase_key)
    profiles = get_player_profiles()

    our_positions = {num: tuple(pos) for num, pos in phase["our_positions"].items()}
    if selected_player in our_positions and selected_player_position is not None:
        our_positions[selected_player] = tuple(selected_player_position)

    fig = go.Figure()
    fig.update_layout(shapes=_pitch_shapes())

    # --- Our team markers ---
    our_numbers = sorted(our_positions.keys())
    our_x = [our_positions[n][0] for n in our_numbers]
    our_y = [our_positions[n][1] for n in our_numbers]
    marker_sizes = [26 if selected_player == n else 20 for n in our_numbers]
    marker_colors = [
        COLORS["highlight"] if selected_player == n else COLORS["our_team"]
        for n in our_numbers
    ]

    fig.add_trace(go.Scatter(
        x=our_x, y=our_y,
        mode="markers+text",
        text=[str(n) for n in our_numbers],
        textposition="middle center",
        textfont=dict(color="#000000", size=10, family="Barlow Condensed"),
        marker=dict(
            color=marker_colors, size=marker_sizes,
            line=dict(color="white", width=2), symbol="circle",
        ),
        customdata=[
            [f"#{n}", profiles[n]["name"], profiles[n]["position_title"], profiles[n]["role_summary"]]
            for n in our_numbers
        ],
        hovertemplate="<b>%{customdata[0]} %{customdata[1]}</b><br>%{customdata[2]}<br>%{customdata[3]}<extra>Coach Billy XI</extra>",
        name="Coach Billy XI",
    ))

    # Position labels below each marker
    for n in our_numbers:
        x, y = our_positions[n]
        fig.add_annotation(
            x=x, y=y - 4.5,
            text=profiles[n]["position_title"].split("/")[0].strip(),
            showarrow=False,
            font=dict(color="rgba(255,255,255,0.7)", size=7.5, family="Barlow"),
            bgcolor="rgba(0,0,0,0)",
        )

    # Highlight ring for selected player
    if selected_player in our_positions:
        hx, hy = our_positions[selected_player]
        fig.add_trace(go.Scatter(
            x=[hx], y=[hy], mode="markers",
            marker=dict(size=40, color="rgba(0,0,0,0)",
                        line=dict(color=COLORS["highlight"], width=3), symbol="circle-open"),
            hoverinfo="skip", showlegend=False,
        ))

    # --- Opposition markers ---
    opp_numbers = sorted(phase["opposition_positions"].keys())
    fig.add_trace(go.Scatter(
        x=[phase["opposition_positions"][n][0] for n in opp_numbers],
        y=[phase["opposition_positions"][n][1] for n in opp_numbers],
        mode="markers+text",
        text=[str(n) for n in opp_numbers],
        textposition="middle center",
        textfont=dict(color="white", size=10, family="Barlow Condensed"),
        marker=dict(color=COLORS["opp_team"], size=18,
                    line=dict(color="white", width=1.5), symbol="square"),
        hovertemplate="<b>Opposition #%{text}</b><extra>Opposition XI</extra>",
        name="Opposition XI",
    ))

    # --- Ball path ---
    ball_path = phase["ball_path"]
    if step_index is None:
        step_index = len(ball_path) - 1
    step_index = max(0, min(step_index, len(ball_path) - 1))
    visible_path = ball_path[: step_index + 1]

    if len(visible_path) > 1:
        fig.add_trace(go.Scatter(
            x=[pt[0] for pt in visible_path[:-1]],
            y=[pt[1] for pt in visible_path[:-1]],
            mode="lines",
            line=dict(color=COLORS["ball_path"], width=2.5, dash="dot"),
            hoverinfo="skip", name="Ball path", showlegend=False,
        ))

    # Ball emoji at current position
    bx, by = visible_path[-1]
    fig.add_trace(go.Scatter(
        x=[bx], y=[by], mode="text",
        text=["⚽"], textfont=dict(size=22),
        hovertemplate="Ball<extra></extra>",
        name="Ball", showlegend=False,
    ))

    # --- Selected player path ---
    if selected_player_path and len(selected_player_path) > 1:
        fig.add_trace(go.Scatter(
            x=[pt[0] for pt in selected_player_path],
            y=[pt[1] for pt in selected_player_path],
            mode="lines+markers",
            line=dict(color=COLORS["highlight"], width=2.5),
            marker=dict(size=5, color=COLORS["highlight"]),
            hoverinfo="skip", name="Player path", showlegend=False,
        ))

    # --- Movement arrows ---
    arrows_to_show = phase["movement_arrows"]
    if step_index is not None and len(arrows_to_show) > 1:
        arrows_to_show = arrows_to_show[: min(step_index + 1, len(arrows_to_show))]

    for arrow in arrows_to_show:
        color = COLORS["arrow_our"] if arrow["team"] == "our" else COLORS["arrow_opp"]
        fig.add_annotation(
            x=arrow["end"][0], y=arrow["end"][1],
            ax=arrow["start"][0], ay=arrow["start"][1],
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=4, arrowsize=1, arrowwidth=2,
            arrowcolor=color,
            text=arrow["label"],
            font=dict(color="white", size=9, family="Barlow"),
            bgcolor="rgba(0,0,0,0.45)",
            borderpad=2,
        )

    fig.update_layout(**_base_pitch_layout())
    return fig


def _build_content_sunburst(title, section_data):
    """Build an interactive sunburst chart for one game-model content section."""
    ids, labels, parents, customdata = [title], [title], [""], [title]
    for key, value in section_data.items():
        key_id = f"{title}:{key}"
        ids.append(key_id)
        labels.append(key.replace("_", " ").title())
        parents.append(title)
        customdata.append(key.replace("_", " ").title())
        if isinstance(value, list):
            for idx, item in enumerate(value, 1):
                ids.append(f"{key_id}:{idx}")
                labels.append(f"{key.replace('_',' ').title()} {idx}")
                parents.append(key_id)
                customdata.append(item)
        else:
            ids.append(f"{key_id}:detail")
            labels.append(str(value)[:30])
            parents.append(key_id)
            customdata.append(value)

    fig = go.Figure(go.Sunburst(
        ids=ids, labels=labels, parents=parents,
        branchvalues="total", customdata=customdata,
        hovertemplate="%{customdata}<extra></extra>",
        insidetextorientation="radial",
        marker=dict(colorscale="Blues"),
    ))
    fig.update_layout(
        margin=dict(l=6, r=6, t=10, b=6),
        paper_bgcolor=COLORS["bg_panel"],
        font=dict(color="white"),
    )
    return fig


def _build_player_animation_figure(phase_key, selected_player):
    """Build animated tactical frames showing ball progression and selected player movement."""
    phase = get_phase_config(phase_key)
    default_pos = phase["our_positions"].get(selected_player)
    if default_pos is None:
        return _build_tactical_figure(phase_key, selected_player=selected_player, step_index=0)

    player_positions = get_player_movement_positions(phase_key, selected_player)
    if not player_positions:
        player_positions = [default_pos] * len(phase["ball_path"])

    base_fig = _build_tactical_figure(
        phase_key, selected_player=selected_player,
        step_index=0,
        selected_player_position=player_positions[0],
        selected_player_path=player_positions[:1],
    )
    frames = []
    for step in range(len(phase["ball_path"])):
        frame_fig = _build_tactical_figure(
            phase_key, selected_player=selected_player,
            step_index=step,
            selected_player_position=player_positions[step],
            selected_player_path=player_positions[:step + 1],
        )
        frames.append(go.Frame(data=frame_fig.data, layout=frame_fig.layout, name=str(step)))

    base_fig.frames = frames
    base_fig.update_layout(
        updatemenus=[dict(
            type="buttons", direction="left", x=0.01, y=1.12,
            buttons=[
                dict(
                    label="▶ Play", method="animate",
                    args=[None, {
                        "frame": {"duration": ANIMATION_FRAME_DURATION_MS, "redraw": True},
                        "fromcurrent": True,
                        "transition": {"duration": ANIMATION_TRANSITION_DURATION_MS},
                    }],
                ),
                dict(
                    label="⏸ Pause", method="animate",
                    args=[[None], {"frame": {"duration": ANIMATION_PAUSE_DURATION_MS, "redraw": False}, "mode": "immediate"}],
                ),
            ],
        )],
        sliders=[dict(
            active=0,
            currentvalue={"prefix": "Step: "},
            steps=[
                dict(
                    label=str(s + 1), method="animate",
                    args=[[str(s)], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                )
                for s in range(len(phase["ball_path"]))
            ],
        )],
    )
    return base_fig


# ---------------------------------------------------------------------------
# PLAYER CARD
# ---------------------------------------------------------------------------

def _render_player_card(player_number):
    """Render the selected player's profile card, skill set list, and tactical expectations."""
    profile = get_player_profile(player_number)
    if not profile:
        return

    st.markdown(
        f"""
        <div class="info-card">
          <div class="phase-badge">{profile['position_title']}</div>
          <h4 style="margin:0 0 4px 0;">#{player_number} · {profile['name']}</h4>
          <p style="margin:0 0 8px 0; opacity:0.85; font-size:0.92rem;">{profile['role_summary']}</p>
          <p style="margin:0; opacity:0.8; font-size:0.88rem; line-height:1.5;">{profile['bio_role']}</p>
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


# ---------------------------------------------------------------------------
# PAGE RENDERERS
# ---------------------------------------------------------------------------

def _render_game_model_page(selected_player):
    gm = get_game_model()
    st.title("Coach Billy — Game Model")
    st.caption("Canada Soccer B Diploma | Tactical philosophy and positional profile")

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Who We Are")
        st.markdown(f"**Club Philosophy:** {gm['who_we_are']['club_philosophy']}")
        st.markdown(f"**Guiding Principles:** {gm['who_we_are']['club_guiding_principles']}")
        st.markdown(f"**Coaching Philosophy:** {gm['who_we_are']['coaching_philosophy']}")
        st.subheader("How Do We Coach?")
        st.markdown(f"**Training Design:** {gm['how_do_we_coach']['training_design_principles']}")
        st.markdown(f"**Methodologies:** {gm['how_do_we_coach']['preferred_practice_methodologies']}")
        st.markdown(f"**Coaching Approaches:** {gm['how_do_we_coach']['preferred_coaching_approaches']}")

    with col_b:
        st.subheader("How We Want to Play")
        st.markdown(f"**Style of Play:** {gm['how_we_want_to_play']['style_of_play']}")
        st.markdown("**Moments of the Game:**")
        for moment in gm["how_we_want_to_play"]["moments_of_the_game"]:
            st.markdown(f"- {moment}")
        st.markdown(f"**Pitch Geography:** {gm['how_we_want_to_play']['pitch_geography']}")
        st.markdown("**Systems:** " + " · ".join(gm["how_we_want_to_play"]["systems"]))
        st.markdown("**Strategies:**")
        for s in gm["how_we_want_to_play"]["strategies"]:
            st.markdown(f"- {s}")
        st.markdown("**Tactics:**")
        for t in gm["how_we_want_to_play"]["tactics"]:
            st.markdown(f"- {t}")

    st.subheader("Pitch Geography")
    st.plotly_chart(_build_pitch_geography_figure(), use_container_width=True, config={"displayModeBar": False})

    st.subheader("Future Canadian Player — Skill Sets & Behaviours")
    for item in gm["future_canadian_player"]["skill_sets_player_behaviours"]:
        st.markdown(f"- {item}")

    st.subheader("Positional Profile Spotlight")
    _render_player_card(selected_player)


def _render_tactical_board_page(selected_player):
    st.title("Dynamic Tactical Board")
    st.caption("11v11 phase views — accurate 4-4-2 / 4-2-3-1 shapes with positional arrows and ball flow.")

    phase_keys = get_phase_keys()
    tabs = st.tabs([get_phase_config(key)["title"] for key in phase_keys])
    for tab, phase_key in zip(tabs, phase_keys):
        with tab:
            phase = get_phase_config(phase_key)
            st.markdown(
                f'<div class="phase-badge">{phase["our_system"]}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(phase["description"])
            st.plotly_chart(
                _build_tactical_figure(phase_key, selected_player=selected_player),
                use_container_width=True,
                config={"displayModeBar": False},
            )
            _render_player_card(selected_player)


def _render_attacking_defending_page(selected_player):
    st.title("Attacking vs Defending Organization")
    st.caption("Side-by-side tactical shapes — 4-4-2 in possession vs 4-2-3-1 out of possession.")

    left, right = st.columns(2)
    with left:
        st.markdown('<div class="phase-badge">Attacking Organization · 4-4-2</div>', unsafe_allow_html=True)
        st.plotly_chart(
            _build_tactical_figure("attacking_organization", selected_player=selected_player),
            use_container_width=True, config={"displayModeBar": False},
        )
    with right:
        st.markdown('<div class="phase-badge">Defensive Organization · 4-2-3-1</div>', unsafe_allow_html=True)
        st.plotly_chart(
            _build_tactical_figure("defensive_organization", selected_player=selected_player),
            use_container_width=True, config={"displayModeBar": False},
        )
    _render_player_card(selected_player)


def _render_movement_board_page(selected_player):
    st.title("Player & Ball Movement")
    st.caption("Step through each tactical phase — ball moves, arrows reveal, player paths update.")

    phase_options = {get_phase_config(key)["title"]: key for key in get_phase_keys()}
    selected_phase_title = st.selectbox("Select phase", list(phase_options.keys()))
    phase_key = phase_options[selected_phase_title]
    phase = get_phase_config(phase_key)
    max_step = len(phase["ball_path"]) - 1

    step = st.slider("Tactical progression step", min_value=0, max_value=max_step, value=0)

    player_positions = get_player_movement_positions(phase_key, selected_player)
    selected_player_position = player_positions[step] if player_positions and step < len(player_positions) else None
    selected_player_path = player_positions[:step + 1] if player_positions else None

    fig = _build_tactical_figure(
        phase_key,
        selected_player=selected_player,
        step_index=step,
        selected_player_position=selected_player_position,
        selected_player_path=selected_player_path,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    step_labels = {
        0: ("🔵 Step 1", "info", "Initial phase shape — starting positions before the play develops."),
        max_step: ("🟢 Final Step", "success", "Sequence complete — full tactical shape achieved."),
    }
    label, kind, msg = step_labels.get(step, ("🟡 In Progress", "warning", "Shape adapting — movement and support runs developing."))
    getattr(st, kind)(msg)

    _render_player_card(selected_player)


def _render_player_role_animation_page(selected_player):
    st.title("Animated Player Role Walkthrough")
    st.caption("Select a phase and animate how your chosen player and the ball move in sync.")

    phase_options = {get_phase_config(key)["title"]: key for key in get_phase_keys()}
    selected_phase_title = st.selectbox("Select phase for animation", list(phase_options.keys()))
    phase_key = phase_options[selected_phase_title]

    st.plotly_chart(
        _build_player_animation_figure(phase_key, selected_player),
        use_container_width=True,
        config={"displayModeBar": False},
    )
    _render_player_card(selected_player)


def _render_philosophy_diagrams_page(selected_player):
    gm = get_game_model()
    st.title("Interactive Philosophy Diagrams")
    st.caption("Visual breakdowns of game model philosophy — who we are, how we coach, how we play.")

    tab_a, tab_b, tab_c = st.tabs(["Who We Are", "How Do We Coach", "How We Want to Play"])
    with tab_a:
        st.plotly_chart(_build_content_sunburst("Who We Are", gm["who_we_are"]),
                        use_container_width=True, config={"displayModeBar": False})
    with tab_b:
        st.plotly_chart(_build_content_sunburst("How Do We Coach", gm["how_do_we_coach"]),
                        use_container_width=True, config={"displayModeBar": False})
    with tab_c:
        st.plotly_chart(_build_content_sunburst("How We Want to Play", gm["how_we_want_to_play"]),
                        use_container_width=True, config={"displayModeBar": False})

    st.subheader("Moments of the Game — Connection Flow")
    st.plotly_chart(_build_moments_flow_figure(), use_container_width=True, config={"displayModeBar": False})

    st.subheader("Field Geography (Zones + Channels)")
    st.plotly_chart(_build_pitch_geography_figure(), use_container_width=True, config={"displayModeBar": False})

    st.subheader("Tactical Shape Comparison")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Attacking Organization — 4-4-2**")
        st.plotly_chart(_build_tactical_figure("attacking_organization", selected_player=selected_player),
                        use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.markdown("**Defensive Organization — 4-2-3-1**")
        st.plotly_chart(_build_tactical_figure("defensive_organization", selected_player=selected_player),
                        use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# SIDEBAR & ROUTING
# ---------------------------------------------------------------------------

all_profiles = get_player_profiles()
player_options = sorted(all_profiles.keys())

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 10px 0 16px 0;">
          <div style="font-family:'Barlow Condensed',sans-serif; font-size:1.4rem;
                      font-weight:700; color:#00c2ff; letter-spacing:0.05em;">
            COACH BILLY
          </div>
          <div style="font-size:0.75rem; color:rgba(255,255,255,0.5); margin-top:2px;">
            Canada Soccer B Diploma · Game Model
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    selected_page = st.radio(
        "Navigation",
        [
            "Game Model",
            "Dynamic Tactical Board",
            "Player & Ball Movement",
            "Attacking vs Defending Organization",
            "Animated Player Role Walkthrough",
            "Interactive Philosophy Diagrams",
        ],
    )
    st.divider()
    selected_player = st.selectbox(
        "Player Focus",
        options=player_options,
        format_func=lambda n: f"#{n} — {all_profiles[n]['name']} ({all_profiles[n]['position_title'].split('/')[0].strip()})",
    )

PAGE_MAP = {
    "Game Model":                       _render_game_model_page,
    "Dynamic Tactical Board":           _render_tactical_board_page,
    "Player & Ball Movement":           _render_movement_board_page,
    "Attacking vs Defending Organization": _render_attacking_defending_page,
    "Animated Player Role Walkthrough": _render_player_role_animation_page,
    "Interactive Philosophy Diagrams":  _render_philosophy_diagrams_page,
}

renderer = PAGE_MAP.get(selected_page)
if renderer:
    renderer(selected_player)
else:
    st.error(f"Unknown page: '{selected_page}'")
