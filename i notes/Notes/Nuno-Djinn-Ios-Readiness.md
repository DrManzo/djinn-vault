---
subject: tech/software-development/mobile-apps/djinn-vault/nuno-djinn-ios-readiness
tags:
  - business/software-development
  - cs/mobile-apps
  - cs/flutter
  - personal/development-tools
created: 2026-06-14
source: Perplexity export
---

# NUNO-Djinn iOS Readiness

## Summary
This document outlines the steps required to build and deploy the NUNO-Djinn Flutter-based messenger app for iOS, including prerequisites, configuration details, and specific issues to watch out for.

## Key Points
- **NUNO-Djinn** is a full-stack Flutter app with iOS support already in place.
- **Prerequisites**: Mac with Xcode, Flutter SDK 3.5.4 or higher, CocoaPods, Apple Developer account.
- **Server URLs**: Must be configured to point to a real server (local IP not supported).
- **Xcode Configuration**: Sign the app using your Apple ID and ensure proper entitlements.

## Details
The NUNO-Djinn app is a self-hosted messenger with iOS support already set up. Here’s how you can build and deploy it on an iPhone:

### What NUNO-Djinn Is
- **Flutter-based Messenger App**: Targets iOS, Android, Web, macOS, Linux, and Windows.
- **Backend**: Two Java Spring Boot servers (REST API server and WebSocket messaging server) orchestrated with Docker Compose.

### iOS Support Already Exists
- **Minimum iOS Version**: 15.5 (iPhone 7+).
- **Xcode Project Files**: Present in `Runner.xcodeproj` and `Runner.xcworkspace`.
- **Push Notifications & Call Handling**: Integrated via `AppDelegate.swift`, `NunoCallKitService.swift`, and `NunoIncomingPushInterceptor.swift`.

### What You Need to Do
1. **Prerequisites**:
   - **Mac with Xcode**: Required for building iOS `.ipa` files.
   - **Flutter SDK 3.5.4 or higher**.
   - **CocoaPods**: Install via `sudo gem install cocoapods`.
   - **Apple Developer Account**: Free for TestFlight, $99/year for App Store.

2. **Fix Server URLs**:
   - Update `assets/config.json` to point to a real server (local IP not supported).

3. **Configure Signing in Xcode**:
   ```bash
   cd nuno_client
   flutter pub get
   cd ios
   pod install
   ```
   - Open `ios/Runner.xcworkspace` in Xcode.
   - Go to **Signing & Capabilities**, select your Apple team/Developer Account, and let Xcode auto-manage the provisioning profile.

4. **Build and Deploy**:
   - For a physical iPhone (without App Store):
     ```bash
     cd nuno_client
     flutter build ios --release
     flutter run --release
     ```
   - Or build an `.ipa` archive in Xcode → **Product → Archive → Distribute App**.

5. **iOS-Specific Gotchas to Watch**:
   - **VoIP Push Entitlement**: Requires Apple to grant VoIP entitlement.
   - **CallKit**: Works only on real devices, not simulator.
   - **APNs for prod**: Change `Runner.entitlements` APS environment from `development` to `production`.
   - **`media_kit` on iOS**: Known build quirks; may need `use_modular_headers!` in Podfile.
   - **Associated Domain**: Requires the `apple-app-site-association` file.

### Summary Path
1. Get a Mac with Xcode (or use CI services like Codemagic/GitHub Actions).
2. Update `config.json` to point to a real hosted server.
3. Run `flutter pub get`, `pod install`, and open `.xcworkspace`.
4. Sign the app using your Apple ID in Xcode.

## References
- [NUNO-Djinn iOS Readiness](https://github.com/DrManzo/NUNO-Djinn)
- [Flutter Documentation](https://flutter.dev/)
- [Xcode Documentation](https://developer.apple.com/xcode/)
- [Apple Developer Program](https://developer.apple.com/programs/)

## Related
- [[Can-I-Install-An-Apk-On-Parrot-Os]] — iOS development tools and environment
