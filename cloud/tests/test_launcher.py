import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("launcher", Path(__file__).parents[1] / "run.py")
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class ConfigurationTests(unittest.TestCase):
    def test_partial_state_is_not_ready(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            for content in ('{', '{}', '{"hubs": []}', '{"hubs": [{"state": null}]}'):
                (folder / 'state-26_0_2.json').write_text(content)
                self.assertIsNone(launcher.valid_state(folder))

    def test_existing_configuration_preserves_custom_preferences(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            state = {"hubs": [{"state": {"tabs": {"tabs": [{"type": 0}]}}}]}
            state_path = folder / 'state-26_0_2.json'
            state_path.write_text(json.dumps(state))
            prefs_path = folder / 'prefs.json'
            prefs_path.write_text(json.dumps({"theme": "dark", "liveMode": "nt4"}))
            launcher.prepare_advantagescope(folder)
            prefs = json.loads(prefs_path.read_text())
            self.assertEqual(prefs['theme'], 'dark')
            self.assertEqual(prefs['liveMode'], 'rlog')
            self.assertEqual(prefs['rlogPort'], 5800)
            self.assertEqual(prefs['robotAddress'], '127.0.0.1')
            self.assertEqual(json.loads(state_path.read_text()), state)


if __name__ == '__main__':
    unittest.main()
