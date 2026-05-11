"""Player profiles and tactical model datasets for the Coach Billy game model app.

Tactical positioning is grounded in real 4-4-2 / 4-2-3-1 movement logic:
- Attacking Organization: Wide overloads, overlapping fullbacks, striker hold-up
- Defensive Organization: Compact 4-2-3-1 block, press triggers, cover shadows
- Attacking Transition: Fast-break channels, second-striker support, box arrivals
- Defensive Transition: Counter-press, recovery lanes, pivot screen

Pitch coordinate system: x = 0 (our goal) → 100 (opposition goal), y = 0 (bottom) → 64 (top).
"""

from copy import deepcopy
import re

PITCH_BOUNDS = {"length": 100, "width": 64}

PLAYER_NUMBER_PATTERN = re.compile(r"#(\d+)")

GAME_MODEL = {
    "who_we_are": {
        "club_philosophy": "Calm in possession and look to build and combine passes before we go forward. Attack from wide channels and find our striker in central position for one or two touch finishes on goal.",
        "club_guiding_principles": "A positive club culture, keeping the team structured and organized during and throughout the season. Players continually assess their ability and growth while coaches teach tactical ideas through field and classroom sessions.",
        "coaching_philosophy": "Player-first coaching that focuses on growth, confidence, and development by maximizing available resources.",
    },
    "how_do_we_coach": {
        "training_design_principles": "Recreate match moments that the team struggles with, then tailor sessions to solve those exact match problems.",
        "preferred_practice_methodologies": "Build smart players with strong game understanding by combining guided repetition, decision-making constraints, and reflective debriefs.",
        "preferred_coaching_approaches": "Train long-ball triggers, supporting structure around first and second balls, and clear attacking organization when direct play is chosen.",
    },
    "how_we_want_to_play": {
        "style_of_play": "Attack in a 1-4-4-2 and defend in a 1-4-2-3-1. Build from the back, progress through wide channels using overloads and overlapping runs, and remain compact without the ball.",
        "moments_of_the_game": [
            "Attacking Organization (In Possession)",
            "Defensive Organization (Out of Possession)",
            "Attacking Transition",
            "Defensive Transition",
        ],
        "pitch_geography": "Use central channels to switch play and activate wide channels for progression and crossing entries into zone 4.",
        "systems": ["1-4-4-2 (Attacking)", "1-4-2-3-1 (Defending)"],
        "strategies": [
            "Stay compact while defending and step wide selectively.",
            "When a midfielder shifts wide to support a fullback, the opposite midfielder protects central zone 3.",
            "Create wide overloads with fullback + winger + midfielder to access quality crossing moments.",
        ],
        "tactics": [
            "Play forward when possible; reset and circulate when blocked.",
            "Progress through wide channels rather than forcing central traffic.",
            "Use central players to transfer the ball side-to-side before penetrating.",
        ],
    },
    "future_canadian_player": {
        "skill_sets_player_behaviours": [
            "Technically secure under pressure.",
            "Tactically adaptable across moments of the game.",
            "Communicative and accountable in role execution.",
            "Physically capable of repeated transitions.",
            "Resilient decision-making after mistakes.",
        ]
    },
}

PLAYER_PROFILES = {
    1: {
        "name": "Aiden Clarke",
        "position_title": "Goalkeeper",
        "role_summary": "Sweeper-keeper and defensive organizer.",
        "bio_role": "Maintains a high line, organizes the back four, commands the area, and starts attacks with calm distribution under pressure.",
        "key_skills": ["Shot stopping", "Aerial command", "Distribution range", "Communication"],
        "tactical_expectations": [
            "Support high defensive line as cover.",
            "Trigger quick restarts when opposition is unbalanced.",
            "Direct build-up toward weak-side winger when central lane is blocked.",
        ],
    },
    2: {
        "name": "Noah Bennett",
        "position_title": "Right Full Back",
        "role_summary": "Aggressive wide support in attack, controlled duelist in defense.",
        "bio_role": "Overlaps in possession, combines with winger and striker, and remains disciplined in one-v-one defending and line management.",
        "key_skills": ["1v1 defending", "Timing overlaps", "Recovery runs", "Crossing"],
        "tactical_expectations": [
            "Create outside lane overloads with #7 and #10.",
            "Press wide on trigger with cover from #6.",
            "Recover quickly into back four when possession is lost.",
        ],
    },
    3: {
        "name": "Ethan Doyle",
        "position_title": "Left Full Back",
        "role_summary": "Balanced fullback with transition speed.",
        "bio_role": "Mirrors right back responsibilities with overlapping support, duel strength, and quick defensive recovery.",
        "key_skills": ["Defensive footwork", "Wide progression", "Press resistance", "Communication"],
        "tactical_expectations": [
            "Provide width in attacking shape.",
            "Step into midfield when winger drives inside.",
            "Drop early against direct transition threats.",
        ],
    },
    4: {
        "name": "Liam Foster",
        "position_title": "Right Center Back",
        "role_summary": "Back-line leader and first build-up outlet.",
        "bio_role": "Leads defensive communication, dominates aerial duels, and starts progression with composed passing options.",
        "key_skills": ["Aerial duels", "Line control", "Passing composure", "Defensive reading"],
        "tactical_expectations": [
            "Protect central corridor during transition.",
            "Connect through #6 or fullback depending on press shape.",
            "Compress space behind midfield line.",
        ],
    },
    5: {
        "name": "Mason Grant",
        "position_title": "Left Center Back",
        "role_summary": "Defensive anchor with distribution quality.",
        "bio_role": "Supports line leadership, tracks diagonal runs, and anchors defensive balance while helping secure progression.",
        "key_skills": ["Positioning", "Defensive timing", "Diagonal passing", "Physical duels"],
        "tactical_expectations": [
            "Mark striker movements between fullback and center back.",
            "Offer safe-side support during circulation.",
            "Delay and channel attacks wide if isolated.",
        ],
    },
    6: {
        "name": "Lucas Reid",
        "position_title": "Defensive Midfielder",
        "role_summary": "Midfield screen and transition connector.",
        "bio_role": "Protects center backs, breaks up play, supports distribution, and rotates with #8/#10 while preserving defensive structure.",
        "key_skills": ["Ball recovery", "Scanning", "Press resistance", "Switch passing"],
        "tactical_expectations": [
            "Protect central channel when fullback steps wide.",
            "Receive under pressure and switch quickly.",
            "Lead counter-press in immediate loss moments.",
        ],
    },
    7: {
        "name": "Owen Scott",
        "position_title": "Right Wide Midfielder",
        "role_summary": "Direct 1v1 threat and transition runner.",
        "bio_role": "Uses pace to isolate defenders, attack depth, and support both crossing and recovery actions depending on game state.",
        "key_skills": ["Explosive dribbling", "Final-third decisions", "Pressing recovery", "Diagonal runs"],
        "tactical_expectations": [
            "Pin fullback to open overlap lane for #2.",
            "Attack weak-side far post on opposite-wing delivery.",
            "Track runner when defending in mid-block.",
        ],
    },
    8: {
        "name": "Jacob Mills",
        "position_title": "Left Central Midfielder",
        "role_summary": "Two-way link between build-up and final third.",
        "bio_role": "Dictates tempo, supports transitions, and contributes in both overload creation and recovery structure.",
        "key_skills": ["Tempo control", "Combination play", "Defensive support", "Spatial awareness"],
        "tactical_expectations": [
            "Join overload on active flank.",
            "Balance opposite half-space when #10 drifts.",
            "Arrive late at top of box for second balls.",
        ],
    },
    9: {
        "name": "Cole Turner",
        "position_title": "Center Forward (Target)",
        "role_summary": "Hold-up striker and primary box finisher.",
        "bio_role": "Links attacks through hold-up play, leads pressing triggers, and provides technical finishing in congested areas.",
        "key_skills": ["Hold-up play", "Box finishing", "Press triggers", "Layoff passing"],
        "tactical_expectations": [
            "Set first pressing direction toward touchline.",
            "Occupy center backs to free #10 and wingers.",
            "Stay connected to box occupancy in final-third attacks.",
        ],
    },
    10: {
        "name": "Ryan Patel",
        "position_title": "Second Striker / Shadow Forward",
        "role_summary": "Creative link and overload organizer.",
        "bio_role": "Connects midfield to front line, switches point of attack, and creates final-third entries via combinations and shooting threat.",
        "key_skills": ["Chance creation", "Final pass", "Positional rotation", "Long-range threat"],
        "tactical_expectations": [
            "Find pockets behind opposition midfield.",
            "Link with #7/#2 to break wide line.",
            "Counter-press immediately after central turnovers.",
        ],
    },
    11: {
        "name": "Kai Morgan",
        "position_title": "Left Wide Midfielder",
        "role_summary": "Wide penetrator and dual-phase transition outlet.",
        "bio_role": "Attacks isolated defenders, combines on the flank, and recovers to support defensive overloads when required.",
        "key_skills": ["1v1 attacking", "Wide crossing", "Tracking back", "Transition acceleration"],
        "tactical_expectations": [
            "Attack space behind fullback on switch.",
            "Support #3 in 2v1 defending moments.",
            "Arrive centrally when opposite wing creates crossing chance.",
        ],
    },
}

# ---------------------------------------------------------------------------
# FORMATION BLUEPRINTS
# Realistic 4-4-2 and 4-2-3-1 positions on a 100x64 pitch.
# x: 0 = our goal end, 100 = opposition goal end
# y: 0 = bottom touchline, 64 = top touchline
# Centre of pitch y = 32
# ---------------------------------------------------------------------------

BASE_FORMATIONS = {
    # 4-4-2 attacking shape: GK + back four + flat four midfield + two strikers
    # Fullbacks at ~x22, centre-backs at ~x18 staggered
    # Midfield line at x38-42, wingers pinned wide (y=8/y=56)
    # Two strikers offset: target (#9) slightly deeper, shadow (#10) ahead
    "1-4-4-2": {
        1:  (6,  32),   # GK
        4:  (20, 39),   # RCB
        5:  (20, 25),   # LCB
        2:  (24, 54),   # RB (tucked, ready to overlap)
        3:  (24, 10),   # LB
        7:  (42, 56),   # RM (wide, pinning opp LB)
        8:  (40, 22),   # LCM
        6:  (38, 36),   # DM/RCM (slight right of centre)
        11: (42, 8),    # LM (wide, pinning opp RB)
        9:  (72, 38),   # CF/Target striker (slightly right, hold-up)
        10: (68, 26),   # SS/Shadow (left of #9, between lines)
    },
    # 4-2-3-1 defending shape: compact mid-block
    # Double pivot sits at x34-36, back four at x20-22
    # Three in the 10-line at x46-50, lone striker pressing high at x62
    "1-4-2-3-1": {
        1:  (6,  32),   # GK
        4:  (20, 39),   # RCB
        5:  (20, 25),   # LCB
        2:  (22, 52),   # RB
        3:  (22, 12),   # LB
        6:  (34, 39),   # RDM (right pivot)
        8:  (34, 25),   # LDM (left pivot)
        7:  (48, 52),   # RAM (right of 10-line)
        10: (48, 32),   # CAM (central 10)
        11: (48, 12),   # LAM (left of 10-line)
        9:  (62, 32),   # CF pressing high, setting direction
    },
}

def mirror_positions(position_map):
    """Mirror normalized player coordinates horizontally across the pitch (opposition team)."""
    return {num: (100 - x, y) for num, (x, y) in position_map.items()}

OPPOSITION_FORMATIONS = {
    "1-4-4-2":   mirror_positions(BASE_FORMATIONS["1-4-4-2"]),
    "1-4-2-3-1": mirror_positions(BASE_FORMATIONS["1-4-2-3-1"]),
}

# ---------------------------------------------------------------------------
# PHASE CONFIGURATIONS
# Each phase defines:
#   ball_path   — ordered list of (x,y) ball positions across 5-6 steps
#   movement_arrows — who moves where, with jersey label & team colour key
#
# Arrow label format "#N description" triggers per-player movement tracking.
# 'our' arrows = blue; 'opp' arrows = red
# ---------------------------------------------------------------------------

PHASES = {
    # -----------------------------------------------------------------------
    # PHASE 1: ATTACKING ORGANIZATION (4-4-2 in possession)
    # Scenario: Build from GK → CB → DM → switch to RB overlap
    #           #7 pins opp LB wide, #2 overlaps, #9 holds, #10 runs behind
    # -----------------------------------------------------------------------
    "attacking_organization": {
        "title": "Attacking Organization (In Possession)",
        "our_system": "1-4-4-2",
        "description": (
            "GK plays to RCB (#4) under low press. #4 feeds DM (#6) who circulates "
            "to RM (#7). #7 holds wide to pin opposition LB. RB (#2) overlaps into "
            "the channel. #9 occupies both CBs centrally; #10 makes a run off the "
            "shoulder of the last defender into the right half-space."
        ),
        # Step 0: GK has ball | Step 1: RCB | Step 2: DM | Step 3: RM wide
        # Step 4: RB overlap into channel | Step 5: Cross / cutback into box
        "ball_path": [
            (6,  32),   # GK — starting position
            (20, 39),   # RCB (#4) receives
            (38, 36),   # DM (#6) receives, faces forward
            (42, 56),   # RM (#7) receives wide on right
            (58, 58),   # RB (#2) receives overlapping in channel
            (78, 50),   # Ball played into box / cutback zone
        ],
        "movement_arrows": [
            # RB overlaps when RM has ball
            {"team": "our",  "start": (24, 54), "end": (58, 60),  "label": "#2 overlap run"},
            # RM holds width then checks inside after laying off to RB
            {"team": "our",  "start": (42, 56), "end": (55, 48),  "label": "#7 inside channel"},
            # #10 (shadow striker) makes run off last defender's shoulder into right half-space
            {"team": "our",  "start": (68, 26), "end": (80, 36),  "label": "#10 run in behind"},
            # #9 (target) holds position centrally, occupies both CBs
            {"team": "our",  "start": (72, 38), "end": (76, 32),  "label": "#9 near post run"},
            # LM (#11) drifts central to arrive late at far post
            {"team": "our",  "start": (42, 8),  "end": (74, 22),  "label": "#11 far post run"},
            # DM (#6) supports behind the ball, provides recycle option
            {"team": "our",  "start": (38, 36), "end": (50, 40),  "label": "#6 support line"},
            # LB (#3) tucks inside to maintain back-four shape as #2 advances
            {"team": "our",  "start": (24, 10), "end": (36, 18),  "label": "#3 tuck inside"},
            # Opposition CB presses RB channel
            {"team": "opp",  "start": (78, 50), "end": (68, 56),  "label": "Opp LB track"},
            # Opposition DM drops to cover half-space
            {"team": "opp",  "start": (62, 32), "end": (72, 40),  "label": "Opp DM cover"},
        ],
    },

    # -----------------------------------------------------------------------
    # PHASE 2: DEFENSIVE ORGANIZATION (4-2-3-1 out of possession)
    # Scenario: Opposition building right. #9 sets press direction left.
    #           Double pivot screens central corridor. Right side compresses.
    #           Back four holds shape 10m behind pivot.
    # -----------------------------------------------------------------------
    "defensive_organization": {
        "title": "Defensive Organization (Out of Possession)",
        "our_system": "1-4-2-3-1",
        "description": (
            "Opposition builds from their right. #9 press-triggers, forcing play "
            "back or wide. RAM (#7) presses opp LB. RDM (#6) shifts to cover "
            "the central lane. LDM (#8) holds pivot shape. Back four steps up "
            "as a unit to compress. #10 covers the central 10-space."
        ),
        # Ball starts with opp RCB, builds wide, tries to play inside
        "ball_path": [
            (80, 39),   # Opp RCB in possession (their build)
            (74, 50),   # Opp plays to RB (wide right)
            (66, 54),   # Opp RB drives inside channel
            (58, 46),   # Opp attempts to play into striker
            (52, 38),   # Ball recovered / recycled back
        ],
        "movement_arrows": [
            # #9 sets press direction — body shape forces play backward/wide
            {"team": "our",  "start": (62, 32), "end": (72, 36),  "label": "#9 press trigger"},
            # RAM (#7) presses opp RB in wide right channel
            {"team": "our",  "start": (48, 52), "end": (60, 54),  "label": "#7 press wide"},
            # RDM (#6) shifts right to block central passing lane
            {"team": "our",  "start": (34, 39), "end": (44, 44),  "label": "#6 channel block"},
            # LDM (#8) holds central pivot, prevents switch
            {"team": "our",  "start": (34, 25), "end": (36, 32),  "label": "#8 pivot hold"},
            # RB (#2) steps narrow — doesn't chase wide ball yet
            {"team": "our",  "start": (22, 52), "end": (28, 46),  "label": "#2 step narrow"},
            # RCB (#4) steps up to compress space behind pivot
            {"team": "our",  "start": (20, 39), "end": (26, 42),  "label": "#4 line step"},
            # CAM (#10) drops to screen 10-space centrally
            {"team": "our",  "start": (48, 32), "end": (44, 36),  "label": "#10 screen"},
            # LM (#11) tucks inside to reduce central gap
            {"team": "our",  "start": (48, 12), "end": (42, 20),  "label": "#11 tuck block"},
            # Opposition wide player tries to play inside
            {"team": "opp",  "start": (74, 50), "end": (66, 42),  "label": "Opp inside ball"},
            # Opposition striker checks deep to receive
            {"team": "opp",  "start": (72, 32), "end": (64, 36),  "label": "Opp CF checks"},
        ],
    },

    # -----------------------------------------------------------------------
    # PHASE 3: ATTACKING TRANSITION (Win ball in midfield — fast break)
    # Scenario: #6 wins ball centrally. #9 spins immediately on the shoulder.
    #           #10 carries from midfield. #7 and #11 sprint wide channels.
    #           #2 and #3 push forward but delayed (maintain shape).
    # -----------------------------------------------------------------------
    "attacking_transition": {
        "title": "Attacking Transition (Regain → Attack)",
        "our_system": "1-4-4-2",
        "description": (
            "DM (#6) wins the ball centrally in zone 2-3 border. #9 spins "
            "immediately to offer direct vertical option. #10 carries forward "
            "into zone 3. RM (#7) sprints the right channel, LM (#11) sprints "
            "the left. #6 plays first-time to #9 or carries to #10."
        ),
        # Ball won centrally, quick vertical play, wide runners stretch defence
        "ball_path": [
            (38, 36),   # #6 wins ball — midfield regain
            (50, 34),   # #10 carries or receives centrally
            (62, 42),   # Ball played wide right to #7
            (74, 52),   # #7 drives channel — cuts inside
            (82, 40),   # #9 receives cutback / through-ball
            (90, 32),   # Shooting / finishing position
        ],
        "movement_arrows": [
            # #9 immediately spins off last defender's shoulder
            {"team": "our",  "start": (72, 38), "end": (76, 30),  "label": "#9 spin & run"},
            # #10 carries from midfield into attacking zone
            {"team": "our",  "start": (68, 26), "end": (80, 32),  "label": "#10 carry forward"},
            # RM (#7) sprints right channel at full pace
            {"team": "our",  "start": (42, 56), "end": (78, 58),  "label": "#7 channel sprint"},
            # LM (#11) sprints left channel as second option
            {"team": "our",  "start": (42, 8),  "end": (75, 10),  "label": "#11 left sprint"},
            # RB (#2) pushes forward but delayed — second wave
            {"team": "our",  "start": (24, 54), "end": (50, 56),  "label": "#2 delayed support"},
            # DM (#6) plays ball then supports behind — doesn't overcommit
            {"team": "our",  "start": (38, 36), "end": (50, 38),  "label": "#6 second support"},
            # LCM (#8) shifts right to cover #6's space vacated
            {"team": "our",  "start": (40, 22), "end": (40, 34),  "label": "#8 cover pivot"},
            # Opposition recovery runs
            {"team": "opp",  "start": (62, 28), "end": (76, 36),  "label": "Opp CB track #9"},
            {"team": "opp",  "start": (74, 50), "end": (80, 56),  "label": "Opp LB track #7"},
        ],
    },

    # -----------------------------------------------------------------------
    # PHASE 4: DEFENSIVE TRANSITION (Lose ball in attack — counter-press)
    # Scenario: Ball lost in opp half. Immediate counter-press from #9, #10,
    #           #7. Wide mids recover. Double pivot drops behind ball line.
    #           Back four resets behind the pivot rapidly.
    # -----------------------------------------------------------------------
    "defensive_transition": {
        "title": "Defensive Transition (Loss → Recover)",
        "our_system": "1-4-2-3-1",
        "description": (
            "Ball lost in opposition zone 3. #9 immediately counter-presses "
            "the ball-carrier. #10 presses nearest passing option. #7 and #11 "
            "recover at pace to block the wide outlets. Double pivot (#6, #8) "
            "drops behind the ball line. Back four resets compact and deep."
        ),
        # Ball lost in their half — opposition looks to break quickly
        "ball_path": [
            (72, 36),   # Ball lost — opp gains possession in zone 3
            (64, 32),   # Opp carries under pressure
            (56, 28),   # Opp plays it centrally, evades first press
            (50, 32),   # Opp in central midfield — approaching our pivot
            (44, 36),   # Ball approaches our defensive structure
        ],
        "movement_arrows": [
            # #9 counter-presses ball-carrier immediately — don't let them turn
            {"team": "our",  "start": (62, 32), "end": (68, 34),  "label": "#9 counter-press"},
            # #10 presses nearest opp passing option to the right
            {"team": "our",  "start": (48, 32), "end": (58, 30),  "label": "#10 press option"},
            # RM (#7) sprints back to block right wide outlet
            {"team": "our",  "start": (58, 56), "end": (48, 52),  "label": "#7 recover wide"},
            # LM (#11) sprints back to block left wide outlet
            {"team": "our",  "start": (58, 8),  "end": (48, 12),  "label": "#11 recover wide"},
            # RDM (#6) immediately drops behind ball line — pivot screen
            {"team": "our",  "start": (34, 39), "end": (38, 38),  "label": "#6 pivot drop"},
            # LDM (#8) holds left of pivot — no central gap
            {"team": "our",  "start": (34, 25), "end": (38, 28),  "label": "#8 pivot hold"},
            # RB (#2) recovers from advanced position rapidly
            {"team": "our",  "start": (52, 56), "end": (28, 52),  "label": "#2 recovery run"},
            # LB (#3) recovers inside, back four resets compact
            {"team": "our",  "start": (36, 10), "end": (24, 12),  "label": "#3 recovery"},
            # RCB (#4) steps up to halfway point of press, ready to compress
            {"team": "our",  "start": (20, 39), "end": (24, 38),  "label": "#4 line ready"},
            # Opp tries to escape through central pass
            {"team": "opp",  "start": (64, 32), "end": (54, 30),  "label": "Opp central escape"},
            # Opp wide player making run to receive
            {"team": "opp",  "start": (68, 50), "end": (60, 54),  "label": "Opp wide run"},
        ],
    },
}


# ---------------------------------------------------------------------------
# DATA ACCESS FUNCTIONS
# ---------------------------------------------------------------------------

def get_player_profile(number):
    """Return a single player profile by jersey number, or None if missing."""
    return PLAYER_PROFILES.get(number)


def get_player_profiles():
    """Return a deep copy of all player profiles to prevent accidental mutation."""
    return deepcopy(PLAYER_PROFILES)


def get_game_model():
    """Return a deep copy of the full game-model content structure."""
    return deepcopy(GAME_MODEL)


def get_phase_keys():
    """Return available phase keys used by tactical board views."""
    return list(PHASES.keys())


def get_phase_config(phase_key):
    """Return a phase config with derived team/opposition positions for the phase system.

    Raises ValueError for unknown phase keys.
    """
    if phase_key not in PHASES:
        raise ValueError(f"Unknown phase key: '{phase_key}'. Valid keys: {list(PHASES)}")
    phase = deepcopy(PHASES[phase_key])
    system = phase["our_system"]
    phase["our_positions"] = deepcopy(BASE_FORMATIONS[system])
    phase["opposition_positions"] = deepcopy(OPPOSITION_FORMATIONS[system])
    return phase


def get_player_movement_positions(phase_key, player_number):
    """Return a list of (x, y) coordinates per phase step for one player.

    Movement is driven by two layers:
    1. Tagged arrows: arrows whose label includes '#<number>' move that player
       to the arrow's end point at the corresponding step.
    2. Ball-proximity support: players without tagged arrows drift slightly
       toward the ball using position-specific support factors.
    """
    phase = get_phase_config(phase_key)
    current_position = phase["our_positions"].get(player_number)

    if current_position is None:
        return []

    steps = len(phase["ball_path"])

    # --- Build tagged movement map ---
    tagged_movements = {}
    for step_index, arrow in enumerate(phase["movement_arrows"]):
        if arrow["team"] != "our":
            continue
        numbers = [int(m) for m in PLAYER_NUMBER_PATTERN.findall(arrow["label"])]
        if player_number in numbers:
            tagged_movements[step_index] = tuple(arrow["end"])

    if tagged_movements:
        positions = []
        pos = current_position
        for step in range(steps):
            # Apply the latest tagged movement up to and including this step
            applicable = [ep for si, ep in sorted(tagged_movements.items()) if si <= step]
            if applicable:
                pos = applicable[-1]
            positions.append(pos)
        return positions

    # --- Ball-proximity support drift (positional role-aware factors) ---
    support_factors = {
        1:  0.02,   # GK — barely moves
        4:  0.06,   # RCB — shifts with line
        5:  0.06,   # LCB
        2:  0.10,   # RB — pushes forward
        3:  0.10,   # LB
        6:  0.09,   # DM — supports close
        8:  0.09,   # LCM
        7:  0.13,   # RM — runs hardest
        11: 0.13,   # LM
        9:  0.12,   # CF
        10: 0.12,   # SS
    }
    support_factor = support_factors.get(player_number, 0.10)
    pos = list(current_position)
    positions = []
    for step in range(steps):
        target_x, target_y = phase["ball_path"][step]
        pos[0] = pos[0] + ((target_x - pos[0]) * support_factor)
        pos[1] = pos[1] + ((target_y - pos[1]) * support_factor)
        positions.append((
            max(0, min(PITCH_BOUNDS["length"], pos[0])),
            max(0, min(PITCH_BOUNDS["width"],  pos[1])),
        ))
    return positions
