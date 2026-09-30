import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch, call

spec = importlib.util.spec_from_file_location("launcher", Path(__file__).parents[1] / "run.py")
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class ConfigurationTests(unittest.TestCase):
    def test_2d_layout_selects_requested_field_and_pose_without_duplicates(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            old_tab = {"type": 3, "title": "3D FTCodeSim", "controller": {"game": "DECODE"}}
            state = {"hubs": [{"state": {"tabs": {"selected": 0, "tabs": [old_tab]}}}],
                     "satellites": [{"keep": True}]}
            path = folder / 'state-26_0_2.json'
            path.write_text(json.dumps(state))
            launcher.configure_2d_layout(folder)
            launcher.configure_2d_layout(folder)
            result = json.loads(path.read_text())
            tabs = result['hubs'][0]['state']['tabs']
            self.assertEqual(len(tabs['tabs']), 2)
            self.assertEqual(tabs['tabs'][0], old_tab)
            selected = tabs['tabs'][tabs['selected']]
            self.assertEqual(selected['type'], 2)
            self.assertEqual(selected['controller']['field'], 'FTC:2026-2027 Field')
            self.assertEqual(selected['controller']['sources'][0]['logKey'],
                             'RealOutputs/Mecanum/position ftc coords (m)')
            self.assertEqual(result['satellites'], state['satellites'])

    def test_detects_only_rlog_listener(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            tcp = folder / 'tcp'
            tcp.write_text('header\n0: 00000000:16A8 00000000:0000 01\n')
            self.assertFalse(launcher.rlog_listening(folder))
            tcp.write_text('header\n0: 00000000:1F90 00000000:0000 0A\n')
            self.assertFalse(launcher.rlog_listening(folder))
            (folder / 'tcp6').write_text('header\n0: 00000000:16A8 00000000:0000 0A\n')
            self.assertTrue(launcher.rlog_listening(folder))

    def test_waits_for_init_before_sending_keys(self):
        stop = Mock()
        stop.wait.side_effect = [False, True]
        with patch.object(launcher.shutil, 'which', return_value='/usr/bin/xdotool'), \
             patch.object(launcher, 'rlog_listening', return_value=False), \
             patch.object(launcher, 'desktop_command') as command:
            launcher.connect_advantagescope(stop)
            command.assert_not_called()

    def test_connects_once_and_restores_focus(self):
        stop = Mock()
        stop.wait.return_value = False
        stop.is_set.return_value = False
        with patch.object(launcher.shutil, 'which', return_value='/usr/bin/xdotool'), \
             patch.object(launcher, 'rlog_listening', return_value=True), \
             patch.object(launcher, 'scope_windows', side_effect=[
                 [('0x20', 'Untitled - AdvantageScope')],
                 [('0x20', '127.0.0.1 (Searching) - AdvantageScope')]]), \
             patch.object(launcher, 'desktop_command', return_value='16') as command:
            launcher.connect_advantagescope(stop)
            self.assertEqual(command.call_args_list, [
                call('xdotool', 'getactivewindow'),
                call('xdotool', 'windowactivate', '--sync', '0x20'),
                call('xdotool', 'key', '--clearmodifiers', 'ctrl+shift+k'),
                call('xdotool', 'windowactivate', '16')])

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
            with patch.object(launcher, 'ensure_field_asset'):
                launcher.prepare_advantagescope(folder)
            prefs = json.loads(prefs_path.read_text())
            self.assertEqual(prefs['theme'], 'dark')
            self.assertEqual(prefs['liveMode'], 'rlog')
            self.assertEqual(prefs['rlogPort'], 5800)
            self.assertEqual(prefs['robotAddress'], '127.0.0.1')
            self.assertEqual(json.loads(state_path.read_text()), state)


if __name__ == '__main__':
    unittest.main()
