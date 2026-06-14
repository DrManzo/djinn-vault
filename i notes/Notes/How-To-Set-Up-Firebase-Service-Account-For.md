---
subject: 3d-printing/models/forge-upgrades
tags:
  - cs/security
  - cs/firebase
  - business/development-process
created: 2026-06-14
source: Perplexity export
---

# How to Set Up Firebase Service Account for Djinn Beta Server

## Summary
This note provides instructions on how to properly set up and use a Firebase service account JSON file in the `secrets/` directory of your project, ensuring secure and functional deployment.

## Key Points
- Obtain the Firebase service account JSON from the Firebase console.
- Place it securely in the `secrets/` folder within your repository.
- Use environment variables for better security during local development or non-Google server deployments.

## Details
To ensure that your Djinn beta server can access real admin credentials, follow these steps:

1. **Obtain the Service Account JSON File:**
   - Open the [Firebase console](https://console.firebase.google.com/).
   - Navigate to **Project settings** → **Service accounts**.
   - Click on **Generate New Private Key** and confirm.
   - Firebase will download a JSON credentials file that you must store securely.

2. **Securely Place the File:**
   - Rename the downloaded file to `firebase-service-account.json` if necessary.
   - Place it in your project’s `secrets/` folder so the final path is `secrets/firebase-service-account.json`.
   - The JSON typically contains fields like `type`, `project_id`, `private_key_id`, `private_key`, and `client_email`.

3. **Important Safety Measures:**
   - Do not commit this file to GitHub or any public repository, as Google warns that anyone who gets the private key can use the resources associated with the service account.
   - Store it carefully; if it leaks, create a new key and delete the old one.

4. **Better Deployment Option:**
   - For environments like Cloud Run, App Engine, or Cloud Functions, Firebase recommends using **Application Default Credentials** with `initializeApp()` and no key file.
   - If running locally or on non-Google servers, set `GOOGLE_APPLICATION_CREDENTIALS` to the JSON file path or explicitly pass the key path in code. The environment-variable approach is more secure.

5. **Example Local Setup:**
   ```bash
   mkdir -p secrets
   mv ~/Downloads/your-downloaded-file.json secrets/firebase-service-account.json
   export GOOGLE_APPLICATION_CREDENTIALS="$PWD/secrets/firebase-service-account.json"
   ```

## References
- [Firebase Admin SDK setup](https://firebase.google.com/docs/admin/setup)
- [Google Application Default Credentials](https://firebase.google.com/docs/admin/setup)

## Related
- [[Djinn-Development-Specification]] — development context
