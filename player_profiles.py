"""Player profiles and tactical model datasets for the Coach Billy game model app."""

from copy import deepcopy
import re

PITCH_BOUNDS = {"length": 100, "width": 64}

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
        "position_title": "Right Wide Forward",
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
        "position_title": "Central Midfielder",
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
        "position_title": "Center Forward",
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
        "position_title": "Attacking Midfielder",
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
        "position_title": "Left Wide Forward",
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

BASE_FORMATIONS = {
    "1-4-4-2": {
        1: (8, 32),
        2: (23, 53),
        3: (23, 11),
        4: (18, 39),
        5: (18, 25),
        6: (36, 43),
        8: (36, 21),
        7: (53, 52),
        11: (53, 12),
        10: (70, 33),
        9: (86, 32),
    },
    "1-4-2-3-1": {
        1: (8, 32),
        2: (22, 51),
        3: (22, 13),
        4: (17, 38),
        5: (17, 26),
        6: (34, 39),
        8: (34, 25),
        7: (50, 50),
        10: (50, 32),
        11: (50, 14),
        9: (73, 32),
    },
}

PHASES = {
    "attacking_organization": {
        "title": "Attacking Organization (In Possession)",
        "our_system": "1-4-4-2",
        "description": "Build from the back, attract pressure centrally, then release into wide channels with overlapping support.",
        "ball_path": [(8, 32), (18, 39), (36, 43), (53, 52), (70, 40), (86, 32)],
        "movement_arrows": [
            {"team": "our", "start": (23, 53), "end": (40, 57), "label": "#2 overlap"},
            {"team": "our", "start": (53, 52), "end": (69, 56), "label": "#7 wide run"},
            {"team": "our", "start": (70, 33), "end": (78, 40), "label": "#10 support"},
            {"team": "opp", "start": (63, 32), "end": (57, 32), "label": "Press"},
        ],
    },
    "defensive_organization": {
        "title": "Defensive Organization (Out of Possession)",
        "our_system": "1-4-2-3-1",
        "description": "Stay compact in central channels, force opponents wide, and protect zone 3 with disciplined midfield coverage.",
        "ball_path": [(92, 32), (76, 40), (68, 50), (63, 55)],
        "movement_arrows": [
            {"team": "our", "start": (50, 32), "end": (58, 35), "label": "#10 screen"},
            {"team": "our", "start": (34, 39), "end": (40, 45), "label": "#6 shift"},
            {"team": "our", "start": (50, 50), "end": (58, 52), "label": "#7 press lane"},
            {"team": "opp", "start": (76, 40), "end": (70, 52), "label": "Wide build"},
        ],
    },
    "attacking_transition": {
        "title": "Attacking Transition",
        "our_system": "1-4-4-2",
        "description": "Regain and immediately attack depth with wide runners while maintaining one central support option.",
        "ball_path": [(34, 39), (50, 32), (69, 56), (86, 32)],
        "movement_arrows": [
            {"team": "our", "start": (53, 12), "end": (71, 16), "label": "#11 sprint"},
            {"team": "our", "start": (53, 52), "end": (72, 55), "label": "#7 sprint"},
            {"team": "our", "start": (70, 33), "end": (79, 34), "label": "#10 support"},
            {"team": "opp", "start": (63, 32), "end": (53, 32), "label": "Recovery run"},
        ],
    },
    "defensive_transition": {
        "title": "Defensive Transition",
        "our_system": "1-4-2-3-1",
        "description": "Counter-press around the loss, then recover shape quickly to deny central progression.",
        "ball_path": [(70, 33), (60, 33), (52, 32), (44, 34)],
        "movement_arrows": [
            {"team": "our", "start": (70, 33), "end": (62, 33), "label": "Immediate press"},
            {"team": "our", "start": (53, 52), "end": (48, 47), "label": "#7 recover"},
            {"team": "our", "start": (53, 12), "end": (48, 17), "label": "#11 recover"},
            {"team": "opp", "start": (52, 32), "end": (68, 30), "label": "Escape pass"},
        ],
    },
}


def mirror_positions(position_map):
    """Mirror normalized player coordinates horizontally across the pitch."""
    return {num: (100 - x, y) for num, (x, y) in position_map.items()}


OPPOSITION_FORMATIONS = {
    "1-4-4-2": mirror_positions(BASE_FORMATIONS["1-4-4-2"]),
    "1-4-2-3-1": mirror_positions(BASE_FORMATIONS["1-4-2-3-1"]),
}


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
    """Return a phase config with derived team/opposition positions for the phase system."""
    phase = deepcopy(PHASES[phase_key])
    system = phase["our_system"]
    phase["our_positions"] = deepcopy(BASE_FORMATIONS[system])
    phase["opposition_positions"] = deepcopy(OPPOSITION_FORMATIONS[system])
    return phase


def get_player_movement_positions(phase_key, player_number):
    """Return stepwise player coordinates for one phase keyed to the phase ball progression."""
    phase = get_phase_config(phase_key)
    current_position = phase["our_positions"].get(player_number)
    if current_position is None:
        return []

    steps = len(phase["ball_path"])
    positions = []
    for step in range(steps):
        # Movement arrows are ordered chronologically; apply all arrows whose index is <= current step.
        for movement_step_index, arrow in enumerate(phase["movement_arrows"]):
            if movement_step_index > step or arrow["team"] != "our":
                continue
            numbers = [int(match) for match in re.findall(r"#(\d+)", arrow["label"])]
            if player_number in numbers:
                current_position = tuple(arrow["end"])
        positions.append(current_position)
    return positions
