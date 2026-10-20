#!/usr/bin/env python3
"""Restore saved browser monitor selections through the GNOME adapter at login."""
import json
import os
from pathlib import Path
import subprocess
import sys
from integration_config import backend_path, config_home


def restore_args(renderer, screen, options, settings, adapter):
    background = options.get('backgroundId')
    if not isinstance(background, str) or not Path(background).is_dir():
        return None
    args = [sys.executable, str(adapter), str(renderer), '--screen-root', screen, '--bg', background]
    for key, flag, default in [('fps', '--fps', 30), ('volume', '--volume', 0), ('scaling', '--scaling', 'fill')]:
        value = options.get(key, settings.get('defaultScaling' if key == 'scaling' else key, default))
        if value is not None: args.extend([flag, str(value)])
    for key, flag in [('silent', '--silent'), ('disableMouse', '--disable-mouse'), ('disableParallax', '--disable-parallax'), ('disableParticles', '--disable-particles'), ('noAutomute', '--noautomute'), ('noAudioProcessing', '--no-audio-processing'), ('noFullscreenPause', '--no-fullscreen-pause')]:
        if options.get(key, settings.get(key, False)): args.append(flag)
    assets = settings.get('assetsDir')
    if assets: args.extend(['--assets-dir', assets])
    return args


def main():
    root = config_home() / 'Linux Wallpaper Engine'
    try:
        settings = json.loads((root / 'settings.json').read_text())
        state = json.loads((root / 'active-wallpapers.json').read_text())
    except (OSError, ValueError): return
    if not settings.get('restoreLastWallpaper', True): return
    renderer = backend_path()
    # Prevent the browser and the login entry from starting duplicate renderers.
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit(): continue
        try:
            if proc.stat().st_uid == os.getuid() and (proc / 'exe').resolve() == renderer:
                return
        except OSError: continue
    logdir = config_home() / 'wallpaper-engine'
    logdir.mkdir(parents=True, exist_ok=True)
    with (logdir / 'restore.log').open('a') as output:
        for screen, options in state.get('activeWallpapers', {}).items():
            args = restore_args(renderer, screen, options, settings, Path(__file__).resolve().with_name('gnome-backend.py'))
            if args:
                subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=output, stderr=output, start_new_session=True)


if __name__ == '__main__':
    main()
