import importlib.util
import json
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch, call

spec = importlib.util.spec_from_file_location("launcher", Path(__file__).parents[1] / "run.py")
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class ConfigurationTests(unittest.TestCase):
    @unittest.skipUnless(sys.platform == 'linux', 'Uses Linux /proc process discovery')
    def test_restart_releases_listener_and_preserves_other_workspace(self):
        script = ('import socket, time; '
                  's = socket.socket(); s.bind(("127.0.0.1", 0)); s.listen(); '
                  'print(s.getsockname()[1], flush=True); time.sleep(60)')
        command = ['java', '-c', script, 'org.junit.runner.JUnitCore', launcher.EXAMPLE]
        with tempfile.TemporaryDirectory() as other_workspace:
            processes = []
            try:
                for cwd in (launcher.ROOT / 'TeamCode', other_workspace):
                    processes.append(subprocess.Popen(
                        command, executable=sys.executable, cwd=cwd,
                        start_new_session=True, stdout=subprocess.PIPE, text=True))
                port = int(processes[0].stdout.readline())
                processes[1].stdout.readline()
                with socket.socket() as probe:
                    with self.assertRaises(OSError):
                        probe.bind(('127.0.0.1', port))
                launcher.restart_previous_simulation()
                processes[0].wait(timeout=2)
                self.assertIsNone(processes[1].poll())
                with socket.socket() as probe:
                    probe.bind(('127.0.0.1', port))
                launcher.restart_previous_simulation()  # No previous run is also safe.
            finally:
                for process in processes:
                    launcher.stop_group(process)
                    process.stdout.close()

    @unittest.skipUnless(sys.platform == 'linux', 'Uses POSIX process groups and SIGKILL')
    def test_restart_escalates_when_previous_simulation_ignores_term(self):
        with patch.object(launcher, 'previous_simulations', side_effect=[
                [123], [123], [123], [123], []]), \
             patch.object(launcher.os, 'getpgid', return_value=123), \
             patch.object(launcher.os, 'killpg') as kill, \
             patch.object(launcher.time, 'monotonic', side_effect=[0, 6, 6]):
            launcher.restart_previous_simulation()
        self.assertEqual(kill.call_args_list, [call(123, signal.SIGTERM), call(123, signal.SIGKILL)])

    def test_busy_unrelated_port_is_reported_without_killing_processes(self):
        with patch.object(launcher.socket, 'socket') as socket_factory, \
             patch.object(launcher.os, 'kill') as kill, \
             patch.object(launcher.os, 'killpg', create=True) as killpg:
            socket_factory.return_value.__enter__.return_value.bind.side_effect = OSError('busy')
            with self.assertRaisesRegex(RuntimeError, 'another process'):
                launcher.ensure_ports_available()
            kill.assert_not_called()
            killpg.assert_not_called()

    def test_autotune_port_conflict_is_reported(self):
        def bind(address):
            if address[1] == 10158:
                raise OSError('busy')
        with patch.object(launcher.socket, 'socket') as socket_factory:
            socket_factory.return_value.__enter__.return_value.bind.side_effect = bind
            with self.assertRaisesRegex(RuntimeError, 'Port 10158 is occupied'):
                launcher.ensure_ports_available()

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
