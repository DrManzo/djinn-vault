# Djinn Development Department
## Mobile & Messaging Specialist Manual

This document defines the **Development Department** as a single engineering department with specialized internal agents for cross-platform mobile application work, Android and iOS delivery, release operations, communications architecture, and documentation discipline.

---

## Department Purpose

The Development Department owns software delivery and routes platform-specific work to the right specialist. This structure is especially suited for a messaging product because chat systems combine UI implementation, mobile platform constraints, push notifications, release workflows, and communications-layer correctness.

The department is built around one orchestrator and seven specialist agents. Apple's App Store Connect separates user roles (App Manager vs Developer), which supports treating iOS engineering and release operations as distinct responsibilities. Android Studio's agent workflow supports reviewed, approval-based task execution that aligns with this specialist-agent model.

---

## Department Roster

| Agent | Primary Domain | Core Responsibilities |
|---|---|---|
| **DevDepartmentOrchestrator** | Planning and routing | Decompose requests, assign specialists, coordinate handoffs, enforce execution order |
| **FlutterSpecialist** | Cross-platform application layer | Build Dart/Flutter UI, state management, navigation, shared app logic, reusable components |
| **AndroidSpecialist** | Android engineering | Android Studio, Gradle, ADB, Logcat, emulator debugging, Android-specific integrations |
| **iOSSpecialist** | Apple platform engineering | Swift/SwiftUI bridges, entitlements, provisioning constraints, native iOS integrations |
| **AppleReleaseSpecialist** | Apple release operations | TestFlight, App Store Connect workflows, metadata, screenshots, submission readiness |
| **AndroidReleaseSpecialist** | Android release operations | Play Console release prep, AAB signing, staged rollout, Firebase-linked release checks |
| **CommunicationsSpecialist** | Messaging and real-time systems | Message transport, delivery state, push integration, sync semantics, encryption-aware design |
| **CodeScribeAgent** | Documentation and change history | Add comments, maintain DEVLOG.md, produce review-ready change summaries |

---

## Routing Rules

| Task Type | Primary Agent(s) | Notes |
|---|---|---|
| Flutter UI, screens, state, navigation | **FlutterSpecialist** | Default for shared mobile product work |
| Android builds, Gradle, emulator, Logcat, permissions | **AndroidSpecialist** | Android-specific implementation and diagnostics |
| iOS entitlements, native Apple bridge work, Xcode technical issues | **iOSSpecialist** | Native Apple engineering tasks only |
| TestFlight, App Store listing, Apple metadata, release readiness | **AppleReleaseSpecialist** | Check App Store Connect role boundaries first |
| Play Console upload, rollout, Android production release prep | **AndroidReleaseSpecialist** | Focused on Android release operations |
| Messaging, push, sync, presence, delivery states, encryption | **CommunicationsSpecialist** + **FlutterSpecialist** | Required pair for all messaging features |
| Any code-producing task | **CodeScribeAgent** (last) | Documentation and devlog always runs last |

---

## Messaging App Policy

For the messaging product, **CommunicationsSpecialist must be attached automatically** when a task touches any of the following:

- Message send or receive behavior
- Delivery state transitions (sent → delivered → read)
- Typing indicators, presence, reconnect behavior, or sync rules
- Push notifications or background delivery behavior
- Encryption, privacy-sensitive communication design, or message retry logic

This policy keeps the chat interface aligned with the actual communication model and prevents UI implementation without a fully defined transport or delivery-state contract.

---

## Orchestrator Decision Policy

The orchestrator applies these rules in order:

1. Determine whether the request is **shared product work**, **platform-native work**, **release work**, or **communications work**.
2. Attach **CommunicationsSpecialist** automatically for any messaging-related task.
3. Prefer **FlutterSpecialist** for shared mobile features unless the request is clearly native.
4. Route release tasks to **AppleReleaseSpecialist** or **AndroidReleaseSpecialist**, not to engineering specialists.
5. Run **CodeScribeAgent** after every code-producing path.
6. Preserve review checkpoints before merge or deployment.

---

## DEVLOG Policy

Maintain `DEVLOG.md` as an append-only implementation history. Each entry contains:

- Timestamp
- Task summary
- Agents involved
- Files changed
- Plain-language implementation summary
- Suggested conventional commit message

### Example Entry

```md
## 2026-06-10T06:00:00Z — Messaging delivery receipts

- Agents: CommunicationsSpecialist, FlutterSpecialist, CodeScribeAgent
- Files changed: lib/chat/thread.dart, lib/chat/message_status.dart
- Summary: Added delivery-state mapping for sent, delivered, and read indicators; aligned widget state with communication status model; documented public methods.
- Suggested commit: feat(chat): add delivery receipt mapping and UI state sync
```

---

## Ready-to-Paste Configuration

```python
DEVELOPMENT_DEPARTMENT = {
    "name": "development",
    "orchestrator": "DevDepartmentOrchestrator",
    "agents": [
        {"id": "flutter", "agent": "FlutterSpecialist"},
        {"id": "android", "agent": "AndroidSpecialist"},
        {"id": "ios", "agent": "iOSSpecialist"},
        {"id": "apple_release", "agent": "AppleReleaseSpecialist"},
        {"id": "android_release", "agent": "AndroidReleaseSpecialist"},
        {"id": "communications", "agent": "CommunicationsSpecialist"},
        {"id": "scribe", "agent": "CodeScribeAgent", "always_last": True},
    ],
    "routing_rules": {
        "flutter_ui": ["flutter"],
        "android_debug": ["android"],
        "ios_native": ["ios"],
        "apple_release": ["apple_release"],
        "android_release": ["android_release"],
        "messaging": ["communications", "flutter"],
    },
}
```

---

## Repository Layout

```text
djinn/
└── workspaces/
    └── mobile-forge/
        ├── DEVELOPMENT-DEPARTMENT-MANUAL.md   ← this file
        ├── MOBILE-FORGE-MANUAL.md
        ├── TEAM.md
        ├── DEVLOG.md
        └── agents/
            ├── VSCODE.md
            ├── ANDROID-STUDIO.md
            ├── FLUTTER-SPECIALIST.md
            ├── IOS-SPECIALIST.md
            ├── APPLE-RELEASE-SPECIALIST.md
            ├── ANDROID-RELEASE-SPECIALIST.md
            ├── COMMUNICATIONS-SPECIALIST.md
            └── CODE-SCRIBE-AGENT.md
```

---

## Implementation Priority

1. Create the department directory and agent files.
2. Implement `DevDepartmentOrchestrator` with deterministic routing.
3. Add prompt definitions for all specialists.
4. Add `CodeScribeAgent` and `DEVLOG.md` support.
5. Add the messaging auto-attach rule for `CommunicationsSpecialist`.
