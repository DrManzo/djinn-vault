# Why Voxtype? The State of Voice Typing on Linux

Voice typing has been a standard feature on Windows and macOS for years. So why has Linux been left behind?

## The Wayland Problem

When Linux desktops transitioned from X11 to Wayland, they gained better security and performance—but lost critical functionality that voice typing tools depend on:

- **Global hotkeys** - X11 let any app listen for keypresses system-wide. Wayland blocks this for security, leaving no standard way to trigger "push to talk."
- **Input simulation** - Tools like xdotool could type text into any window on X11. Wayland forbids this entirely.

Most developers hit these walls and gave up.

## The Speech Recognition Gap

Until recently, offline speech recognition meant choosing between:

- **Cloud APIs** - Good accuracy, but privacy-invasive and requires internet
- **CMU Sphinx / Kaldi** - Open source, but painful to set up and mediocre accuracy

This changed in late 2022 when OpenAI released **Whisper**—a speech recognition model that's free, runs locally, and rivals commercial cloud services in accuracy.

## The Fragmentation Tax

Linux audio has been a moving target: ALSA, PulseAudio, now PipeWire. Different distributions, different desktops, different compositors. Building something that "just works" requires handling all of these combinations.

## How Voxtype Solves This

Voxtype combines several technologies in a way that works across all modern Linux systems:

| Challenge | Solution |
|-----------|----------|
| Global hotkeys on Wayland | **evdev** - reads keyboard events directly from the kernel, bypassing the compositor entirely |
| Input simulation on Wayland | **ydotool** - uses the kernel's uinput interface to simulate typing, with clipboard fallback |
| Speech recognition | **whisper.cpp** - optimized C++ port of Whisper that runs fast on CPU |
| Audio capture | **cpal** - cross-platform audio that works with PipeWire, PulseAudio, and ALSA |

The result: hold a key, speak, release, and your words appear at the cursor. No cloud services, no compositor-specific hacks, no complex setup.

## Why Now?

The pieces have existed independently for a while, but wiring them together correctly is non-obvious. Subtle issues—like blocking I/O in input polling—can silently break everything. Voxtype handles these edge cases so you don't have to.

Linux desktop users deserve the same voice typing experience that Windows and Mac users take for granted. Voxtype delivers it.
