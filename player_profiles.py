# player_profiles.py
"""
Contains player positional profiles (by number), game model summary, and helper functions.
Reference: All content sourced from Coach Billy B Diploma Portfolio and positional profiles section.
"""

GAME_MODEL = {
    "philosophy": "Calm in possession and look to build and combine passes before we go forward. Attack from wide channels and find our striker in central position for one or two touch finishes on goal.",
    "club_guiding_principles": "A positive club culture, keeping the team structured and organized during and throughout the season ... players continually assess their ability and see if they have made improvements ... coaches' ideas and tactics should be taught to the players through training sessions and in class sessions so that the players can learn new tactics and football ideas to increase their own.",
    "coaching_philosophy": "All about the players and ways that we can help them improve. We want this to be a way that we can have the players grow and make them the best player possible with the resources that we have.",
    "training_design_principles": "In training can we recreate an instance in the game that we are struggling with or that we need to learn to prepare us for the match. Always looking to tailor or session to the match and problem that we might have to solve.",
    "style_of_play": "Attack in a 1-4-4-2, defend in a 1-4-2-3-1. Build from the back, progress through wide channels with overloads and overlapping runs. Defensively, stay compact, avoid central attacks, and keep a counter-attacking option upfield for quick transitions.",
    "systems": ["1-4-4-2 (attacking)", "1-4-2-3-1 (defending)"],
    "strategies": [
        "Stay compact when defending, step out wide selectively.",
        "Defensive midfielder (#6/#8) helps cover wide channel; others fill central gaps.",
    ],
    "tactics": [
        "Play forward when possible, otherwise reset and keep possession.",
        "Use wide channels and central players to help ball progression.",
        "Distribute to wide areas for forward movement.",
    ],
}

PLAYER_PROFILES = {
    1: {
        "name": "Goalkeeper",
        "profile": "Maintain a high line, organize and communicate with the back four, versatile distributor, sweeper-keeper, command area, aggressive and brave sweeping outside box, vocal leader.",
    },
    2: {
        "name": "Right Full Back",
        "profile": "Makes overlapping runs, combines with striker/midfield, delivers long balls under pressure, specializes in 1v1 defending (especially vs. speedy wingers), stays organized with center backs, communicates defensive shifts.",
    },
    3: {
        "name": "Left Full Back",
        "profile": "Roles and responsibilities mirror #2; overlapping, defending, supporting possession, wide channel threat, quick recovery, strong in duels, communication.",
    },
    4: {
        "name": "Right Center Back",
        "profile": "Vocal and brave leader, manages back line communication, good in aerial duels, clears danger, calm on ball, start build-up play, combines with defense and midfield.",
    },
    5: {
        "name": "Left Center Back",
        "profile": "As #4; strong in the air, distribution, composure, defensive anchor with added responsibility tracking strikers making diagonal runs.",
    },
    6: {
        "name": "Defensive Midfielder",
        "profile": "Defensive anchor, breaks up play, wins aerial duels, helps transition, distributes deep, supports and covers central and wide spaces, disciplined, technical under pressure, communicates assignments, rotates with #8/#10 when needed.",
    },
    7: {
        "name": "Right Wide Forward",
        "profile": "Elite speed, 1v1 threat, primary aim is to drive/cross or combine out wide, can drop to defend, wide outlet for diagonals, transitions fast, creates goal opportunities, supports defending when needed.",
    },
    8: {
        "name": "Central Midfielder",
        "profile": "Link between defense and attack, support transition, dictates possession, switches play, assists in overloads and combinations, supports both ends, tactically aware, helps defend and build attacks.",
    },
    9: {
        "name": "Center Forward/Striker",
        "profile": "Strong forward, hold-up play, brings in wingers/#8/#10, disciplined pressing, intelligent finisher in the box, creates for teammates, willing to track back for defense as needed.",
    },
    10: {
        "name": "Attacking Midfielder",
        "profile": "Advanced playmaker, links with striker/forwards, switches play, overloads wide channels, creates and attacks opportunity in the final third, shoots from range, recycles possession, quick decision making.",
    },
    11: {
        "name": "Left Wide Forward",
        "profile": "As #7; speed, 1v1 ability, wide channel exploitation, clever off-ball runs, aggressive attacking and defensive transitions, complements right winger/opposite fullback.",
    },
}

def get_player_profile(number):
    """
    Return dict information for player number (1-11).
    """
    return PLAYER_PROFILES.get(number, None)

def get_game_model():
    """
    Return coaching philosophy, playing style, tactics, etc.
    """
    return GAME_MODEL
