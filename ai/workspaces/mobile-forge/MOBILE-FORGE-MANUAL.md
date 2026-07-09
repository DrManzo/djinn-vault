# MobileForge — Mobile Development Department Manual

**Workspace:** `djinn/workspaces/mobile-forge/`  
**Department Head:** Javier (DrManzo)  
**Status:** Active — Messaging App Development  
**Created:** 2026-06-10  

---

## What This Department Does

MobileForge is Djinn's dedicated mobile development workspace. It owns the full lifecycle of mobile application projects — from architecture and IDE setup to cross-platform deployment on both the Google Play Store and Apple App Store. The current active project is a **messaging application** built with Flutter, targeting Android and iOS simultaneously.

This manual is the canonical reference for every agent operating inside MobileForge. Read this first. Then read your individual agent brief.

---

## Department File Ownership

```
djinn/workspaces/mobile-forge/
├── MOBILE-FORGE-MANUAL.md          ← You are here (read-only for agents)
├── TEAM.md                         ← Agent roster and routing
├── CHANGELOG.md                    ← All work recorded here (append only)
├── WORK-LOG.md                     ← Session-by-session activity log
├── projects/
│   └── messaging-app/
│       ├── PROJECT.md              ← Current project state
│       ├── ARCHITECTURE.md         ← System design decisions
│       ├── TASKS.md                ← Active task queue
│       └── sessions/               ← Per-session summaries
├── agents/
│   ├── VSCODE.md                   ← VS Code agent brief
│   ├── ANDROID-STUDIO.md           ← Android Studio agent brief
│   ├── FLUTTER.md                  ← Flutter agent brief
│   ├── COMMS.md                    ← Communications specialist brief
│   ├── IOS.md                      ← Apple/iOS deployment agent brief
│   ├── ANDROID.md                  ← Android deployment agent brief
│   ├── STORE.md                    ← Store submission agent brief
│   └── SCRIBE.md                   ← Code comments & changelog agent brief
└── references/
    ├── flutter-messaging-patterns.md
    ├── fcm-setup.md
    ├── apns-setup.md
    └── store-submission-checklist.md
```

---

## Agent Roster Summary

| Agent Code | Name | Specialty | Priority |
|---|---|---|---|
| `VSCODE` | VS Code Specialist | IDE config, extensions, workspace settings | High |
| `ANDROID-STUDIO` | Android Studio Specialist | Gradle, AVD, ADB, Android-native debug | High |
| `FLUTTER` | Flutter Architect | Dart, cross-platform UI, state management | Critical |
| `COMMS` | Communications Engineer | WebSocket, FCM, APNS, real-time messaging | Critical |
| `IOS` | Apple Platform Specialist | Xcode, provisioning, TestFlight, App Store | High |
| `ANDROID` | Android Platform Specialist | Play Console, signing, ProGuard, AAB | High |
| `STORE` | Store Deployment Agent | App Store + Play Store submission, metadata | Medium |
| `SCRIBE` | Code Scribe | Comment injection, changelog, work log | Always-on |

See `agents/` directory for full briefs.

---

## Routing Rules

- **IDE config issues** → `VSCODE` first, escalate to `ANDROID-STUDIO` if Android-native
- **UI / widget layer** → `FLUTTER`
- **Real-time messaging, push, sockets** → `COMMS`
- **iOS build failures, provisioning errors** → `IOS`
- **Android build failures, signing, ADB** → `ANDROID-STUDIO` or `ANDROID`
- **Store submissions, metadata, screenshots** → `STORE`
- **Comment missing, work not recorded** → `SCRIBE` (runs after every session)

---

## Session Protocol

Every development session in MobileForge follows this protocol:

1. **Open** `projects/messaging-app/TASKS.md` — pick the top item
2. **Work** using the appropriate specialist agent
3. **Comment** all new code as you write (SCRIBE monitors this)
4. **Close** by appending a session summary to `projects/messaging-app/sessions/YYYY-MM-DD.md`
5. **SCRIBE** records the session to `WORK-LOG.md` and `CHANGELOG.md`
6. **Commit** with meaningful message: `git commit -m "feat(mobile): <what changed>"`

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | Flutter (Dart) |
| IDE Primary | VS Code + Flutter extension |
| IDE Android | Android Studio (Gradle, AVD, ADB) |
| IDE iOS | Xcode (via macOS / CI) |
| State Management | Riverpod or BLoC (TBD per ARCHITECTURE.md) |
| Real-time Comms | WebSocket + Firebase Cloud Messaging (FCM) |
| Push (iOS) | Apple Push Notification Service (APNs) |
| Push (Android) | Firebase Cloud Messaging (FCM) |
| Backend API | TBD (REST or gRPC) |
| Android Store | Google Play Console |
| Apple Store | App Store Connect + TestFlight |

---

## Non-Negotiables

1. **Every function has a comment.** No undocumented code ships.
2. **Every session is logged.** SCRIBE writes it — no exceptions.
3. **Platform parity.** Feature exists on Android AND iOS or it doesn't ship.
4. **Signed builds only.** No debug APK/IPA leaves this workspace.
5. **CHANGELOG.md is truth.** If it's not in the changelog, it didn't happen.

---

*MobileForge — part of the Djinn system*  
*Javier's personal AI operating system*
