---
id: 20260519-174507
created: 2026-05-19
type: permanent
title: Python Scripting for iOS (iSH & Shortcuts)
references:
  - [[Perplexity Chat Export 2026-05-19_17-45-07]]
links:
  - [[Faust CLI Project]]
tags: [python, ios, ish, shortcuts, scripting]
---

## Summary
Exploration of running Python scripts on iOS using iSH (Alpine Linux emulator) and Apple Shortcuts integration. Covers package installation, SSH tunneling, automation workflows, and limitations of iOS for development work.

## Key Points
- iSH provides Alpine Linux environment on iOS with package manager (apk) for Python, pip, and common tools
- Apple Shortcuts can trigger iSH scripts via URL schemes and share sheet integration
- SSH tunneling via ngrok or similar allows remote access to iSH services
- Limitations include no background execution, restricted file system access, and no native daemon support
- Recommended workflow: develop on desktop, sync via git, test/run on iSH for mobile scenarios
- Shortcuts automation can trigger Python scripts on location, time, or app events

## Details

### iSH Setup
Install from App Store, then `apk add python3 py3-pip git openssh`. Python 3.11+ available. Virtual environments work normally. Storage limited to app sandbox but can access Files app via share extensions.

### Shortcuts Integration
Create shortcut that runs shell command in iSH via `ish://run?cmd=python3%20script.py`. Can pass input from share sheet, photos, or clipboard. Output can be displayed, saved, or shared.

### Limitations
iOS kills background processes aggressively. iSH stops when app is backgrounded. No cron, systemd, or persistent services. Network access requires app to be foreground. Workaround: use Shortcuts automation to trigger on specific events.

### Recommended Workflow
Primary development on macOS/Linux. Use git for version control. Sync to iOS via iCloud/Working Copy. Use iSH for testing, quick edits, and mobile-specific tasks. Combine with Shortcuts for automation triggers.

## References
- iSH Shell: ish.app
- Apple Shortcuts Documentation: support.apple.com/shortcuts
- Working Copy (Git for iOS): workingcopy.app

## Related
- [[Faust CLI Project]] — Python CLI tool that could be adapted for iOS workflow
- [[Dual-Boot Linux Setup]] — Alternative development environment
- [[Faust-CLI-Project]]
- [[Django-Template-Conversion-Guide]]
- [[Scrambled-Notes-to-APA-Essay-Converter]]
