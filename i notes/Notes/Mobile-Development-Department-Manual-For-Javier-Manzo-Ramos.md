---
subject: Djinn/Vault/MobileDevDepartment
tags:
  - business/mobile-development
  - business/department-management
  - cs/software-engineering
  - personal/embedded-specialist
created: 2026-06-14
source: Perplexity export
---

# Mobile Development Department Manual for Javier Manzo-Ramos

## Summary
This manual outlines the roles and responsibilities of a mobile development department, focusing on integrating Javier Manzo-Ramos as an embedded specialist in the messaging app project. The document provides structure and guidelines to ensure clear boundaries and effective collaboration.

## Key Points
- **Department Roster**: 7 agents plus a master orchestrator.
- **CommsEngineerAgent** is required for E2EE, WebSocket architecture, and push notifications.
- **CodeScribeAgent** ensures documentation and logging of changes.
- **MobileDevOrchestrator** routes tasks and manages the workflow.

## Details
The department follows a structured approach with specific agents dedicated to different tools and responsibilities. The CommsEngineerAgent is crucial for handling secure messaging features, while the CodeScribeAgent focuses on maintaining high-quality documentation. As an embedded specialist, Javier's role involves contributing to the messaging app development, ensuring compliance with best practices, and providing guidance on store readiness.

### Department Roster
| Agent | Domain | Key Tools |
| --- | --- | --- |
| **MobileDevOrchestrator** | Routes all tasks | LangGraph state machine |
| **VSCodeAgent** | IDE workspace, Flutter/Dart tooling | launch.json, extensions, flutter doctor |
| **AndroidStudioAgent** | Gradle, ADB, Logcat, emulators | Kotlin, Jetpack Compose, AVD |
| **FlutterAgent** | Cross-platform UI, state mgmt, chat widgets | Riverpod/BLoC, GoRouter, Platform Channels |
| **iOSAppStoreAgent** | Swift/Xcode, App Store Connect, TestFlight | Fastlane match, APNs, provisioning |
| **PlayStoreAgent** | AAB signing, Play Console, Firebase | Fastlane supply, Crashlytics, staged rollout |
| **CommsEngineerAgent** | WebSocket, E2EE, push notifications, offline sync | Signal Protocol, FCM + APNs, libsodium |
| **CodeScribeAgent** | Comment injection + DEVLOG.md logging | AST parser, Dart doc, Git commit drafter |

### Communications Engineering
The CommsEngineerAgent is essential for handling secure and reliable messaging features. It manages WebSocket/Socket.io architecture, end-to-end encryption via Signal Protocol, offline-first queuing, and push notifications using FCM (Android) and APNs (iOS).

### Code Scribe
The CodeScribeAgent ensures that all changes are well-documented with comments and logs every action in `DEVLOG.md`. This agent helps maintain a clear record of development activities.

### Djinn Integration
The directory structure mirrors existing departments, including an `__init__.py` registration, `agents/`, `tools/`, and `prompts/` for system prompt stubs. The manual includes templates for the Orchestrator, Scribe, and CommsEngineer agents to facilitate immediate configuration.

## References
- [Innowise Blog](https://innowise.com/blog/mobile-app-development-team/)
- [Android Developer](https://developer.android.com/studio/gemini/agent-mode)
- [LinkedIn](https://www.linkedin.com/posts/leadgenmanthan_6-ways-to-build-multi-agent-ai-systems-the-activity-7322196980342906880-mqJw)

## Related
- [[Nuno-Djinn-Ios-Readiness]] — similarity 0.75
