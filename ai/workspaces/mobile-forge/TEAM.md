# MobileForge — Agent Team Roster

**Department:** MobileForge  
**Last Updated:** 2026-06-10  

---

## Active Agents

### 1. VSCODE — VS Code Specialist

**Role:** Development environment authority for VS Code. Owns workspace configuration, extension setup, debugging profiles, and editor-level productivity.

**Responsibilities:**
- `.vscode/settings.json` — project-level editor config
- `.vscode/extensions.json` — recommended extension list
- `.vscode/launch.json` — Flutter debug and device profiles
- `.vscode/tasks.json` — build/run task automation
- Dart/Flutter linting rules (`analysis_options.yaml`)
- Code formatting standards (Dart formatter, line length)
- Workspace-level keybindings and snippets

**Key Extensions Managed:**
- `Dart-Code.flutter` — Flutter/Dart support
- `ms-vscode.vscode-flutter` — Flutter tools
- `usernamehw.errorlens` — inline error display
- `streetsidesoftware.code-spell-checker` — catch typos in comments
- `pkief.material-icon-theme` — file icons
- `formulahendry.auto-rename-tag` — XML/widget tag sync

**Escalation:** If Android-native Gradle configuration is needed, hand off to `ANDROID-STUDIO`.

---

### 2. ANDROID-STUDIO — Android Studio Specialist

**Role:** Android-native build environment. Handles anything that requires the Android SDK, Gradle, AVD (emulator), or ADB directly.

**Responsibilities:**
- `android/` directory configuration in the Flutter project
- `build.gradle` (app-level and project-level)
- `AndroidManifest.xml` — permissions, activities, services
- Android Virtual Device (AVD) setup and management
- ADB device/emulator connectivity
- ProGuard/R8 rules for release builds
- Android-specific plugin integration
- Native Kotlin/Java bridge code when Dart FFI is insufficient

**Tools Owned:**
- Android Studio IDE (separate from VS Code lane)
- `sdkmanager`, `avdmanager` CLI tools
- `gradlew` build scripts

**Escalation:** UI and Dart code stays with `FLUTTER`. Store submission hands off to `ANDROID`.

---

### 3. FLUTTER — Flutter Architect

**Role:** The primary application builder. Owns the Dart codebase, widget tree, navigation, state management, and cross-platform logic.

**Responsibilities:**
- `lib/` directory — all Dart source code
- Widget architecture (stateful/stateless, custom widgets)
- Navigation system (GoRouter or Navigator 2.0)
- State management implementation (Riverpod preferred)
- `pubspec.yaml` — dependency management
- Platform channels to native Android/iOS code
- Theming, typography, and design system tokens in Flutter
- Unit and widget tests (`test/` directory)
- Performance profiling (Flutter DevTools)

**Specialties for Messaging App:**
- Chat UI patterns: bubble widgets, message list, keyboard handling
- Real-time stream subscriptions (StreamBuilder)
- Background isolates for message processing
- Offline-first data layer (local SQLite / Hive)

**Escalation:** Real-time transport layer hands off to `COMMS`.

---

### 4. COMMS — Communications Engineer

**Role:** The real-time messaging backbone. Owns everything related to data transport, push notifications, and live connection management. This is the most critical specialist for a messaging app.

**Responsibilities:**

**WebSocket / Real-Time:**
- WebSocket client implementation in Dart (`web_socket_channel`)
- Connection lifecycle: open, reconnect, heartbeat, close
- Message serialization/deserialization (JSON, Protocol Buffers)
- Presence system (online/offline/typing indicators)
- Message ordering and delivery receipts
- Backoff and retry logic for unstable connections

**Push Notifications — Android (FCM):**
- Firebase project setup and `google-services.json`
- `firebase_messaging` Flutter plugin integration
- Foreground, background, and terminated-state message handling
- Notification channels (Android 8+)
- Data messages vs. notification messages
- FCM token management and refresh

**Push Notifications — iOS (APNs):**
- APNs certificate vs. APNs Auth Key (.p8) setup
- Background fetch entitlement configuration
- `UNUserNotificationCenter` delegate wiring
- Silent push for background sync
- Notification service extension (for media attachments)
- APNs → FCM bridge (recommended: use FCM as unified layer)

**Security:**
- TLS/SSL pinning for WebSocket connections
- End-to-end encryption design (Signal protocol patterns)
- Auth token refresh for persistent connections

**Escalation:** Platform-specific notification permission UI hands off to `IOS` or `ANDROID`. Message UI hands off to `FLUTTER`.

---

### 5. IOS — Apple Platform Specialist

**Role:** Everything Apple. Owns the iOS build pipeline, code signing, TestFlight distribution, and App Store submission.

**Responsibilities:**

**Xcode & Build:**
- `ios/` directory in Flutter project
- Xcode project settings (`Runner.xcodeproj`)
- Bundle identifier and version management
- Build schemes: Debug, Profile, Release
- Info.plist — permissions, URL schemes, capabilities

**Code Signing:**
- Apple Developer account certificates
- Provisioning profiles (development, distribution)
- Automatic vs. manual signing
- Keychain management on build machine

**Capabilities & Entitlements:**
- Push Notifications entitlement
- Background Modes (remote notifications, background fetch)
- Associated Domains (for deep linking)
- App Groups (for notification service extension sharing)

**Distribution:**
- TestFlight builds and external tester groups
- App Store Connect upload via Xcode Organizer or `xcrun altool`
- `fastlane` automation for iOS lane

**Escalation:** App Store metadata and screenshots hand off to `STORE`.

---

### 6. ANDROID — Android Platform Specialist

**Role:** Android release pipeline, signing infrastructure, and Play Store deployment. Works alongside `ANDROID-STUDIO` but focuses on the release lane rather than development.

**Responsibilities:**

**Signing:**
- Keystore generation (`keytool`)
- `key.properties` — signing config (never committed to git)
- `build.gradle` signing block for release builds
- APK vs. AAB (Android App Bundle) — always AAB for Play Store

**Release Build:**
- `flutter build appbundle --release`
- ProGuard/R8 obfuscation verification
- Deobfuscation mapping file preservation
- Multi-ABI builds if needed

**Play Console:**
- Internal testing track → Alpha → Beta → Production pipeline
- Release notes per language
- Rollout percentage management
- Pre-launch report review

**fastlane Android lane:**
- `Fastfile` Android lane setup
- `supply` for Play Store metadata upload
- Google Play API service account credentials

**Escalation:** Store metadata and screenshots hand off to `STORE`.

---

### 7. STORE — Store Deployment Agent

**Role:** The final gate before users. Manages all submission-facing content for both the Google Play Store and Apple App Store.

**Responsibilities:**

**App Store Connect (iOS):**
- App name, subtitle, description (keyword-optimized)
- Screenshots for all required device sizes (6.7", 5.5", iPad Pro)
- App preview videos
- Keywords, categories, age rating
- Privacy policy URL
- Support URL
- Review notes for Apple reviewers
- Version release strategy (manual vs. automatic)

**Google Play Console (Android):**
- Store listing: title, short description, full description
- Screenshots for phone, 7" tablet, 10" tablet
- Feature graphic (1024×500)
- App icon (512×512)
- Content rating questionnaire
- Data safety section
- Target audience

**Both Platforms:**
- ASO (App Store Optimization) research
- Localization coordination
- Release timing strategy
- Review response templates

**Escalation:** Binary (IPA/AAB) preparation hands back to `IOS` or `ANDROID`.

---

### 8. SCRIBE — Code Scribe (Always-On)

**Role:** The department's memory and documentation guardian. SCRIBE runs at the end of every session and monitors code quality from a documentation perspective. Also responsible for comment injection in new code.

**Responsibilities:**

**Code Comments:**
- Every Dart function/method gets a `///` doc comment
- Every class gets a class-level `///` comment explaining its purpose
- Complex logic gets inline `//` comments explaining *why*, not just *what*
- TODO markers formatted as: `// TODO(javier): <description> — <date>`
- FIXME markers formatted as: `// FIXME(javier): <issue> — <date>`

**Comment Format Standards:**
```dart
/// Handles an incoming WebSocket message and routes it to the
/// appropriate message handler based on [MessageType].
///
/// Throws [MessageParseException] if the payload is malformed.
void handleIncoming(String raw) {
  // Parse first — fail fast if malformed
  final msg = MessageParser.parse(raw);
  // Route by type to avoid a massive switch block
  _router.dispatch(msg);
}
```

**Session Logging:**
After every work session, SCRIBE writes to two files:

1. **`WORK-LOG.md`** — append an entry:
```markdown
## [DATE TIME] — [SESSION TOPIC]
**Agent(s) involved:** FLUTTER, COMMS
**What was done:**
- Implemented WebSocket reconnect logic with exponential backoff
- Added FCM token refresh handler
- 3 new functions, all commented
**Files changed:**
- lib/services/socket_service.dart
- lib/services/notification_service.dart
**Next:** Wire APNs token to FCM unified layer
```

2. **`CHANGELOG.md`** — append a versioned entry:
```markdown
## [vX.Y.Z] — YYYY-MM-DD
### Added
- WebSocket reconnect with exponential backoff (socket_service.dart)
### Changed
- FCM token refresh handler updated for token rotation
### Fixed
- N/A
```

**Escalation:** SCRIBE does not edit logic. If missing comments suggest confusion about what code does, flag to the owning agent (FLUTTER, COMMS, etc.).

---

## Routing Matrix — Quick Reference

| Situation | Route To |
|---|---|
| VS Code not finding Flutter SDK | `VSCODE` |
| Gradle sync failing | `ANDROID-STUDIO` |
| Widget layout broken | `FLUTTER` |
| WebSocket dropping on background | `COMMS` |
| Push notification not arriving on iOS | `COMMS` → `IOS` |
| Push notification not arriving on Android | `COMMS` → `ANDROID-STUDIO` |
| App crashes on iOS device only | `IOS` |
| App crashes on Android device only | `ANDROID-STUDIO` |
| Signing error on release build (iOS) | `IOS` |
| Signing error on release build (Android) | `ANDROID` |
| Play Store rejection | `STORE` → `ANDROID` |
| App Store rejection | `STORE` → `IOS` |
| Missing comments in new code | `SCRIBE` |
| Session not logged | `SCRIBE` |

---

*TEAM.md — MobileForge, Djinn Vault*
