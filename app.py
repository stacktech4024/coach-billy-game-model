import streamlit as st
try:
    import plotly.graph_objects as go
except ModuleNotFoundError:
    st.error(
        """Missing dependency: plotly

Install dependency with:
pip install plotly==5.24.1"""
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
ANIMATION_FRAME_DURATION_MS = 900
ANIMATION_TRANSITION_DURATION_MS = 250
ANIMATION_PAUSE_DURATION_MS = 0
MOMENTS_FALLBACK_MARGIN_X = 10
MOMENTS_FALLBACK_WIDTH_X = 80
MOMENTS_FALLBACK_CENTER_Y = 50

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


def _add_field_geography_overlays(fig):
    """Add B Diploma field geography overlays (zones and channels) with labels."""
    _add_zone_overlays(fig)
    channel_height = 64 / 5
    for idx in range(1, 5):
        fig.add_shape(
            type="line",
            x0=0,
            y0=idx * channel_height,
            x1=100,
            y1=idx * channel_height,
            line=dict(color="rgba(255,255,255,0.35)", width=1, dash="dash"),
        )
    for idx, label in enumerate(["Channel 1", "Channel 2", "Channel 3", "Channel 4", "Channel 5"]):
        fig.add_annotation(
            x=3,
            y=(idx * channel_height) + (channel_height / 2),
            text=label,
            showarrow=False,
            font=dict(color="white", size=9),
            xanchor="left",
            bgcolor="rgba(0,0,0,0.25)",
        )


def _build_pitch_geography_figure():
    """Build a dedicated pitch geography figure showing both zones and channels."""
    fig = go.Figure()
    fig.update_layout(shapes=_pitch_shapes())
    _add_field_geography_overlays(fig)
    fig.update_layout(
        xaxis=dict(range=[-1, 101], visible=False),
        yaxis=dict(range=[-1, 65], visible=False, scaleanchor="x", scaleratio=1),
        plot_bgcolor="#1f2f2b",
        paper_bgcolor="#0f172a",
        margin=dict(l=6, r=6, t=6, b=6),
    )
    return fig


def _build_moments_flow_figure():
    """Build an interactive flow diagram showing moments-of-the-game connectivity."""
    moments = get_game_model()["how_we_want_to_play"]["moments_of_the_game"]
    points = [(15, 50), (50, 85), (85, 50), (50, 15)]
    if len(moments) != 4:
        # Fallback for non-4 lists: spread nodes horizontally from left margin to right margin.
        points = [
            (
                MOMENTS_FALLBACK_MARGIN_X + (idx * (MOMENTS_FALLBACK_WIDTH_X / max(len(moments) - 1, 1))),
                MOMENTS_FALLBACK_CENTER_Y,
            )
            for idx in range(len(moments))
        ]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[pt[0] for pt in points],
            y=[pt[1] for pt in points],
            mode="markers+text",
            text=moments,
            textposition="middle center",
            marker=dict(size=42, color="#1d4ed8", line=dict(color="white", width=2)),
            hovertemplate="%{text}<extra>Moment</extra>",
            showlegend=False,
        )
    )
    for idx in range(len(points)):
        start = points[idx]
        end = points[(idx + 1) % len(points)]
        fig.add_annotation(
            x=end[0],
            y=end[1],
            ax=start[0],
            ay=start[1],
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="#93c5fd",
            text="",
        )
    fig.update_layout(
        xaxis=dict(range=[0, 100], visible=False),
        yaxis=dict(range=[0, 100], visible=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=6, r=6, t=6, b=6),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
    )
    return fig


def _build_tactical_figure(phase_key, selected_player=None, step_index=None, selected_player_position=None):
    """Create an 11v11 tactical board for a phase with optional focus player and step index."""
    phase = get_phase_config(phase_key)
    profiles = get_player_profiles()
    our_positions = {num: tuple(position) for num, position in phase["our_positions"].items()}
    if selected_player in our_positions and selected_player_position is not None:
        our_positions[selected_player] = tuple(selected_player_position)

    fig = go.Figure()
    fig.update_layout(shapes=_pitch_shapes())

    our_numbers = sorted(our_positions.keys())
    our_x = [our_positions[num][0] for num in our_numbers]
    our_y = [our_positions[num][1] for num in our_numbers]

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

    if selected_player in our_positions:
        x, y = our_positions[selected_player]
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


def _build_content_sunburst(title, section_data):
    """Build an interactive sunburst chart for one game-model content section."""
    ids = [title]
    labels = [title]
    parents = [""]
    customdata = [title]

    for key, value in section_data.items():
        key_id = f"{title}:{key}"
        ids.append(key_id)
        labels.append(key.replace("_", " ").title())
        parents.append(title)
        customdata.append(key.replace("_", " ").title())

        if isinstance(value, list):
            for idx, item in enumerate(value, start=1):
                ids.append(f"{key_id}:{idx}")
                labels.append(f"{key.replace('_', ' ').title()} {idx}")
                parents.append(key_id)
                customdata.append(item)
        else:
            ids.append(f"{key_id}:detail")
            labels.append("Value")
            parents.append(key_id)
            customdata.append(value)

    fig = go.Figure(
        go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            branchvalues="total",
            customdata=customdata,
            hovertemplate="%{customdata}<extra></extra>",
            insidetextorientation="radial",
        )
    )
    fig.update_layout(
        margin=dict(l=6, r=6, t=10, b=6),
        paper_bgcolor="#0f172a",
        font=dict(color="white"),
    )
    return fig


def _build_player_animation_figure(phase_key, selected_player):
    """Build animated tactical frames showing ball progression and selected player movement."""
    phase = get_phase_config(phase_key)
    default_position = phase["our_positions"].get(selected_player)
    if default_position is None:
        return _build_tactical_figure(phase_key, selected_player=selected_player, step_index=0)

    player_positions = get_player_movement_positions(phase_key, selected_player)
    if not player_positions:
        player_positions = [default_position] * len(phase["ball_path"])

    base_fig = _build_tactical_figure(
        phase_key,
        selected_player=selected_player,
        step_index=0,
        selected_player_position=player_positions[0],
    )
    frames = []
    for step in range(len(phase["ball_path"])):
        frame_fig = _build_tactical_figure(
            phase_key,
            selected_player=selected_player,
            step_index=step,
            selected_player_position=player_positions[step],
        )
        frames.append(go.Frame(data=frame_fig.data, layout=frame_fig.layout, name=str(step)))

    base_fig.frames = frames
    base_fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=0.01,
                y=1.12,
                buttons=[
                    dict(
                        label="▶ Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": ANIMATION_FRAME_DURATION_MS, "redraw": True},
                                "fromcurrent": True,
                                "transition": {"duration": ANIMATION_TRANSITION_DURATION_MS},
                            },
                        ],
                    ),
                    dict(
                        label="⏸ Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": ANIMATION_PAUSE_DURATION_MS, "redraw": False}, "mode": "immediate"}],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                active=0,
                currentvalue={"prefix": "Step: "},
                steps=[
                    dict(label=str(step + 1), method="animate", args=[[str(step)], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}])
                    for step in range(len(phase["ball_path"]))
                ],
            )
        ],
    )
    return base_fig


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
    zone_fig = _build_pitch_geography_figure()
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


def _render_attacking_defending_page(selected_player):
    """Render two labeled tactical pitches side-by-side for attacking and defensive organization."""
    st.title("Attacking vs Defending Organization")
    st.caption("Two distinct tactical pitches with labeled organization, ball flow, and directional movement arrows.")

    left, right = st.columns(2)
    with left:
        st.subheader("Attacking Organization")
        st.plotly_chart(
            _build_tactical_figure("attacking_organization", selected_player=selected_player),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with right:
        st.subheader("Defensive Organization")
        st.plotly_chart(
            _build_tactical_figure("defensive_organization", selected_player=selected_player),
            use_container_width=True,
            config={"displayModeBar": False},
        )
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


def _render_player_role_animation_page(selected_player):
    """Render animated role walkthrough linked to ball movement for a selected player."""
    st.title("Animated Player Role Walkthrough")
    st.caption("Select a phase and run an animation showing how the chosen player and ball move together.")

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
    """Render interactive game-model philosophy diagrams with tactical linkage visuals."""
    gm = get_game_model()
    st.title("Interactive Philosophy Diagrams")
    st.caption("Interactive diagrams for Who We Are, How Do We Coach, and How We Want to Play.")

    tab_a, tab_b, tab_c = st.tabs(["Who We Are", "How Do We Coach", "How We Want to Play"])
    with tab_a:
        st.plotly_chart(_build_content_sunburst("Who We Are", gm["who_we_are"]), use_container_width=True, config={"displayModeBar": False})
    with tab_b:
        st.plotly_chart(_build_content_sunburst("How Do We Coach", gm["how_do_we_coach"]), use_container_width=True, config={"displayModeBar": False})
    with tab_c:
        st.plotly_chart(
            _build_content_sunburst("How We Want to Play", gm["how_we_want_to_play"]),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    st.subheader("Moments of the Game Connection")
    st.plotly_chart(_build_moments_flow_figure(), use_container_width=True, config={"displayModeBar": False})

    st.subheader("Field Geography (Zones + Channels)")
    st.plotly_chart(_build_pitch_geography_figure(), use_container_width=True, config={"displayModeBar": False})

    st.subheader("Tactical Shape Link")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Attacking Organization Shape**")
        st.plotly_chart(_build_tactical_figure("attacking_organization", selected_player=selected_player), use_container_width=True, config={"displayModeBar": False})
    with c2:
        st.markdown("**Defensive Organization Shape**")
        st.plotly_chart(_build_tactical_figure("defensive_organization", selected_player=selected_player), use_container_width=True, config={"displayModeBar": False})


all_profiles = get_player_profiles()
player_options = sorted(all_profiles.keys())

with st.sidebar:
    st.header("Navigation")
    selected_page = st.radio(
        "Go to",
        [
            "Game Model",
            "Dynamic Tactical Board",
            "Player & Ball Movement",
            "Attacking vs Defending Organization",
            "Animated Player Role Walkthrough",
            "Interactive Philosophy Diagrams",
        ],
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
elif selected_page == "Player & Ball Movement":
    _render_movement_board_page(selected_player)
elif selected_page == "Attacking vs Defending Organization":
    _render_attacking_defending_page(selected_player)
elif selected_page == "Animated Player Role Walkthrough":
    _render_player_role_animation_page(selected_player)
elif selected_page == "Interactive Philosophy Diagrams":
    _render_philosophy_diagrams_page(selected_player)
else:
    st.error("Unknown page selected in navigation.")
