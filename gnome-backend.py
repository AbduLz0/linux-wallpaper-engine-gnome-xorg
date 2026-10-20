#!/usr/bin/env python3
"""Adapt linux-wallpaperengine screen output to GNOME X11 windows.

Usage: gnome-backend.py BACKEND [linux-wallpaperengine arguments...]
Requires wmctrl, xprop, and xrandr on PATH. Does not change the Workshop browser.
"""
import ctypes
import os
import re
import signal
import subprocess
import sys
import time


def renderer_lifetime():
    # The browser uses SIGKILL on Stop. Linux must also terminate its renderer
    # children when this supervisor disappears (SIGKILL cannot be trapped).
    parent = os.getppid()
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(1, signal.SIGTERM, 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'prctl(PR_SET_PDEATHSIG) failed')
    if parent == 1 or os.getppid() != parent:
        os._exit(1)


def monitors():
    output = subprocess.check_output(['xrandr', '--query'], text=True)
    found = {}
    for line in output.splitlines():
        match = re.match(r'(\S+) connected (?:primary )?(\d+)x(\d+)\+(\d+)\+(\d+)', line)
        if match:
            name, w, h, x, y = match.groups()
            found[name] = (x, y, w, h)
    return found


def pin(window, geometry):
    # GNOME constrains fullscreen-sized normal windows to their original monitor.
    # Desktop type permits exact placement and keeps them beneath normal apps.
    subprocess.run(['xprop', '-id', window, '-f', '_NET_WM_WINDOW_TYPE', '32a',
                    '-set', '_NET_WM_WINDOW_TYPE', '_NET_WM_WINDOW_TYPE_DESKTOP'], check=True)
    for args in [
        ['-b', 'remove,above'],
        ['-b', 'remove,maximized_vert,maximized_horz'],
        ['-b', 'add,below,sticky'],
        ['-b', 'add,skip_taskbar,skip_pager'],
        ['-t', '-1'],
        ['-e', '0,' + ','.join(geometry)],
    ]:
        subprocess.run(['wmctrl', '-i', '-r', window, *args], check=True)


def main():
    if len(sys.argv) < 2:
        raise ValueError('Expected backend executable')
    backend, *original = sys.argv[1:]
    screens, args = [], []
    i = 0
    while i < len(original):
        if original[i] == '--screen-root':
            if i + 1 >= len(original):
                raise ValueError('--screen-root requires a monitor name')
            screens.append(original[i + 1])
            i += 2
        else:
            args.append(original[i])
            i += 1
    if not screens:
        os.execv(backend, [backend, *original])
    available = monitors()
    for name in screens:
        if name not in available:
            raise ValueError(f'Monitor {name!r} is not active')
    children = []
    def terminate(signum, frame):
        raise SystemExit(128 + signum)
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)
    try:
        for name in dict.fromkeys(screens):
            geometry = available[name]
            child = subprocess.Popen(
                [backend, '--window', 'x'.join(geometry), *args],
                preexec_fn=renderer_lifetime)
            children.append(child)
            deadline = time.monotonic() + 60
            while True:
                if child.poll() is not None:
                    raise RuntimeError(f'Renderer for {name} exited ({child.returncode})')
                lines = subprocess.check_output(['wmctrl', '-lp'], text=True).splitlines()
                window = next((line.split()[0] for line in lines
                               if len(line.split()) >= 3 and line.split()[2] == str(child.pid)), None)
                if window:
                    pin(window, geometry)
                    print(f'Wallpaper positioned on {name}: {geometry}', flush=True)
                    break
                if time.monotonic() >= deadline:
                    raise RuntimeError(f'No player window appeared for {name} within 60 seconds')
                time.sleep(0.2)
        while all(child.poll() is None for child in children):
            time.sleep(0.5)
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


if __name__ == '__main__':
    try:
        main()
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as exc:
        print(f'GNOME wallpaper: {exc}', file=sys.stderr)
        sys.exit(1)
