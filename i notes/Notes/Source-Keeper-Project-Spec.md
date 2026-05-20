---
subject: Business/M-Systems
tags: [source-keeper, tool-development, csharp, wpf, note-taking, research-tool]
created: 2026-05-19
source: 2026-05-18_20-19-28_Perplexity
---

# Source Keeper — Project Spec

## Summary
Source Keeper is a lightweight Windows desktop utility that captures selected text and images from anywhere on screen with a single hotkey (Ctrl+Alt+S), automatically grabs the source URL, and saves everything to a user-chosen file with timestamp and metadata. Built in C# with WPF/XAML, it prioritizes source fidelity, local-first storage, and plain text/markdown output.

## Key Points
- Global hotkey trigger: Ctrl+Alt+S works anywhere on Windows
- Captures text selections and images from any application
- Auto-detects current browser URL via Ctrl+L → Ctrl+C keystroke simulation
- Opens native Windows Save As dialog for user-controlled file/folder selection
- Output format: plain .txt (v0), upgradeable to markdown without code changes
- No GUI beyond the save dialog — keyboard-driven, minimal interface
- C# + WPF/XAML tech stack for tight Windows integration
- Clipboard backup/restore to avoid trashing user's clipboard
- Block format: separator, timestamp, URL, content — appended to existing files
- Local-first, cloud-sync compatible (Dropbox/Git ready)

## Details
The build follows a 5-phase roadmap: (1) Architecture & core logic — hotkey handler, clipboard capture, file structure; (2) Snippet organization — collections as folders with index files; (3) URL & metadata handling — source fidelity as the core promise; (4) MVP build — Python backend or C# executable, system tray or CLI trigger; (5) Testing & refinement across browsers and apps. The URL capture strategy uses a keystroke hack (Ctrl+L to focus address bar, Ctrl+C to copy) since no universal Windows API provides current tab URL. Image handling saves as .png with optional metadata log entry. The philosophy is deliberately anti-lock-in: plain files, user-controlled organization, portable output.

## References
- Windows global hotkey registration via RegisterHotKey P/Invoke
- System.Windows.Forms.Clipboard for clipboard operations
- Microsoft.Win32.SaveFileDialog for file selection
- SendKeys.SendWait for keystroke simulation

## Related
- [[Meanas-and-M-Systems-Business-Vision]]
- [[CiteAssist-and-GhostCite-Project]]
- [[Faust-Project-Setup-Architecture]]
- [[Faust-CLI-Project]]
- [[Scrambled-Notes-to-APA-Essay-Converter]]
