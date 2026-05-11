import unittest

from player_profiles import (
    BASE_FORMATIONS,
    GAME_MODEL,
    OPPOSITION_FORMATIONS,
    PHASES,
    PLAYER_PROFILES,
    get_game_model,
    get_phase_config,
    get_phase_keys,
    get_player_profile,
    get_player_profiles,
    mirror_positions,
)


class TestMirrorPositions(unittest.TestCase):
    def test_mirror_positions_flips_x_and_preserves_y(self):
        positions = {1: (10, 20), 2: (0, 64), 3: (100, 5)}

        mirrored = mirror_positions(positions)

        self.assertEqual(mirrored, {1: (90, 20), 2: (100, 64), 3: (0, 5)})

    def test_mirror_positions_does_not_mutate_input(self):
        positions = {1: (20, 10)}
        original = dict(positions)

        _ = mirror_positions(positions)

        self.assertEqual(positions, original)


class TestPlayerProfileAccess(unittest.TestCase):
    def test_get_player_profile_returns_expected_player(self):
        profile = get_player_profile(9)

        self.assertIsNotNone(profile)
        self.assertEqual(profile["name"], PLAYER_PROFILES[9]["name"])
        self.assertEqual(profile["position_title"], PLAYER_PROFILES[9]["position_title"])

    def test_get_player_profile_returns_none_for_missing_player(self):
        self.assertIsNone(get_player_profile(99))

    def test_get_player_profiles_returns_deep_copy(self):
        profiles_copy = get_player_profiles()

        profiles_copy[1]["name"] = "Changed Name"
        profiles_copy[1]["key_skills"].append("Injected Skill")

        self.assertNotEqual(profiles_copy[1]["name"], PLAYER_PROFILES[1]["name"])
        self.assertNotIn("Injected Skill", PLAYER_PROFILES[1]["key_skills"])


class TestGameModelAccess(unittest.TestCase):
    def test_get_game_model_returns_deep_copy(self):
        game_model_copy = get_game_model()

        game_model_copy["who_we_are"]["club_philosophy"] = "Changed"
        game_model_copy["how_we_want_to_play"]["systems"].append("3-5-2")

        self.assertNotEqual(
            game_model_copy["who_we_are"]["club_philosophy"],
            GAME_MODEL["who_we_are"]["club_philosophy"],
        )
        self.assertNotIn("3-5-2", GAME_MODEL["how_we_want_to_play"]["systems"])


class TestPhaseConfiguration(unittest.TestCase):
    def test_get_phase_keys_matches_phase_dictionary_order(self):
        self.assertEqual(get_phase_keys(), list(PHASES.keys()))

    def test_get_phase_config_returns_enriched_phase_data(self):
        phase_key = "attacking_organization"

        config = get_phase_config(phase_key)

        self.assertIn("our_positions", config)
        self.assertIn("opposition_positions", config)
        self.assertEqual(config["our_system"], PHASES[phase_key]["our_system"])
        self.assertEqual(config["our_positions"], BASE_FORMATIONS[config["our_system"]])
        self.assertEqual(config["opposition_positions"], OPPOSITION_FORMATIONS[config["our_system"]])

    def test_get_phase_config_returns_deep_copies(self):
        phase_key = "defensive_transition"
        config = get_phase_config(phase_key)

        config["ball_path"][0] = (999, 999)
        config["our_positions"][1] = (999, 999)
        config["opposition_positions"][1] = (999, 999)

        self.assertNotEqual(config["ball_path"], PHASES[phase_key]["ball_path"])
        self.assertNotEqual(config["our_positions"], BASE_FORMATIONS[config["our_system"]])
        self.assertNotEqual(config["opposition_positions"], OPPOSITION_FORMATIONS[config["our_system"]])

    def test_get_phase_config_raises_key_error_for_unknown_phase(self):
        with self.assertRaises(KeyError):
            get_phase_config("unknown_phase")


class TestOppositionFormationIntegrity(unittest.TestCase):
    def test_opposition_formations_are_mirrored_from_base_formations(self):
        for system_name, base_positions in BASE_FORMATIONS.items():
            expected = mirror_positions(base_positions)
            self.assertEqual(OPPOSITION_FORMATIONS[system_name], expected)


if __name__ == "__main__":
    unittest.main()
