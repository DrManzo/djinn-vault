---
subject: technology/recording/parrot-os/youtube
tags:
  - business/technology/content-creation
  - cs/software-development
  - personal/privacy-security
created: 2026-05-23
source: Perplexity export
---

# Recording Challenges on Parrot OS for YouTube

## Summary
This note provides guidance on recording both screen and webcam content on Parrot OS for YouTube, including setup instructions using OBS Studio and tips on redacting sensitive information.

## Key Points
- Use **OBS Studio** for recording both screen and webcam.
- Hide or censor any real-world sensitive information to comply with best practices.
- Sanitize configs and logs before recording by replacing real domains/IPs with placeholders.
- Emphasize education and defensive/ethical hacking in your content.

## Details
To record challenges on Parrot OS and post them on YouTube, follow these steps:

### Recording Both Screen and Camera on Parrot OS

1. **OBS Studio (Recommended)**
   - Install OBS Studio via `sudo apt install obs-studio`.
   - Add a **Screen Capture** source for your desktop.
   - Add a **Video Capture Device** source for your webcam, resize and place it appropriately.

2. **SimpleScreenRecorder + Separate Webcam Tool**
   - Use SimpleScreenRecorder for screen capture.
   - Pair it with `guvcview` for the webcam feed, then combine in an editor if needed.

For easy YouTube workflow and live-style content, **OBS Studio** is recommended due to its flexibility.

### What You Should Hide or Censor

1. **Personal Identifiable Information (PII)**
   - Faces or real names of other people.
   - Email addresses, usernames that tie back to your real identity.
   - IP addresses and domains belonging to real organizations you don’t own/control.
   - Home network details.

2. **Real-World Account Details**
   - API keys, tokens, SSH keys, Wi-Fi passwords, VPN credentials.
   - Browser password manager pop-ups, saved logins, or 2FA codes.
   - Documents or windows with personal data (IDs, school papers, financial documents).

3. **Logs and Configurations**
   - Logs output containing user data, emails, or other people’s info if testing on multi-user systems.

### Protecting Yourself While Showing the Hack

1. **Use Lab Environments Only**
   - VMs, intentionally vulnerable machines (e.g., DVWA, Metasploitable), and networks you own or have explicit permission to test.
   
2. **Demo Accounts and Fake Data**
   - Use demo usernames, fake emails, no real passwords.

3. **Sanitize Configurations and Logs**
   - Replace real domains/IPs with placeholders (e.g., `10.10.10.10`, `example.com`).
   - Avoid showing `.ssh`, `.bash_history`, browser history, etc.

4. **Blurring Specific Parts in Editing**
   - Use Kdenlive, Shotcut, or OBS to blur specific regions.
   
### YouTube and "Hacking" Content

- Emphasize education and defensive/ethical hacking.
- Own or control the machines and networks in your demos.
- Have permission where needed.
- Use intentionally vulnerable targets in a lab environment.

Avoid step-by-step exploitation of live real-world services that are not your own, especially if it looks like you’re helping viewers break the law.

## References
- [OBS Studio Installation](https://www.youtube.com/watch?v=apVHwV66uu4)
- [SimpleScreenRecorder Usage](https://www.youtube.com/watch?v=mEaMhhyBhVQ)
- [Redaction Guidance](https://facit.ai/insights/best-practices-for-video-redaction)
- [YouTube Hacking Content Policies](https://danielmiessler.com/blog/youtubes-ban-of-hacking-videos-moves-us-closer-to-an-entertainment-only-world)

## Related
- [[Building-A-Professional-Content-Creation-Studio-A-Comprehensive]] — workflow-similarities
