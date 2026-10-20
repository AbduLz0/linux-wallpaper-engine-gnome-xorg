# Animated wallpapers for Linux

**Browse the Steam Workshop. Pick a wallpaper. Make your desktop yours.**

Bring Wallpaper Engine community wallpapers to GNOME, with support for two monitors and desktop icons that stay visible and clickable.

## Get started

**You’ll need:** Zorin OS 18 or Ubuntu 24.04, a GNOME **X11** session, an Intel/AMD 64-bit computer, and a copy of Wallpaper Engine on Steam.

```bash
git clone https://github.com/AbduLz0/linux-wallpaper-engine-gnome-xorg.git
cd linux-wallpaper-engine-gnome-xorg
./run.sh
```

The installer sets up the browser, wallpaper engine, dependencies, and desktop integration. Follow the prompts for your system password, Steam sign-in, and Wallpaper Engine installation.

The first setup downloads and builds the engine, so allow some time and several GB of free space. It uses **Flatpak Steam**, which it installs if needed.

## Pick your wallpaper

1. Open **Linux Wallpaper Engine** from your applications menu.
2. Browse **Workshop** and download a wallpaper you like.
3. Select your displays and click **Apply**.

Want your normal background back? Click **Stop**.

## A few things to know

- **X11 only** — Wayland isn’t supported by this setup.
- Wallpaper compatibility varies; some community wallpapers may not render correctly.
- Playback on both monitors, desktop icons, and Stop have been verified on Zorin 18.1. The installer has passed automated and runtime checks; a full fresh-machine install is still awaiting verification.

Need help? See the [setup & troubleshooting guide](docs/SETUP.md) or [report an issue](https://github.com/AbduLz0/linux-wallpaper-engine-gnome-xorg/issues).

## Built on community work

This fork connects and improves [Gabriel Dias’s GNOME launcher](https://github.com/berelels/linux-wallpaper-engine-gnome-xorg), [Almamu’s rendering engine](https://github.com/Almamu/linux-wallpaperengine), and [jagrat7’s Workshop browser](https://github.com/jagrat7/linux-wallpaper-engine).

[MIT license](LICENSE) · An unofficial community project.
