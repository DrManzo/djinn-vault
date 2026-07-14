---
subject: cs/programming/powershell/script-execution
tags:
  - cs/programming/powershell/exec-policy
  - cs/programming/powershell/smart-screen
  - cs/programming/powershell/admin-rights
  - cs/programming/powershell/file-path
created: 2026-07-14
source: Perplexity export
---

# PowerShell Script Execution Troubleshooting

## Summary
This note provides troubleshooting steps for executing a PowerShell script on Windows, including handling execution policies, SmartScreen warnings, admin rights issues, and file path errors.

## Key Points
- **Execution Policy Block**: Use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force` or run the script directly with `-ExecutionPolicy Bypass -File "path\to\script.ps1"`.
- **SmartScreen Warning**: Right-click on the script, click "More info," then "Run Anyway," or unblock the file via properties.
- **Admin Rights Missing**: Run PowerShell as Administrator and execute the script from there if you're not already in an admin session.
- **`#Requires -RunAsAdministrator` Error**: Ensure you right-click and select "Run as Administrator" instead of double-clicking.

## Details
When attempting to run a PowerShell script on Windows, several issues can arise. Here are common troubleshooting steps:

### Execution Policy Block
If the script fails with an execution policy error, you need to adjust the execution policy or run the script directly from an elevated PowerShell session.

```powershell
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

# Or run the script directly with:
powershell -ExecutionPolicy Bypass -File "C:\path\to\script.ps1"
```

### SmartScreen Warning
If you encounter a warning from Windows Defender, click on "More info" and then "Run Anyway." Alternatively, unblock the file via its properties.

```powershell
# Right-click script → Properties → Unblock at bottom → Apply
```

### Admin Rights Missing
Ensure that you are running PowerShell with administrative privileges. If not, open a new PowerShell window as an administrator and run the script from there.

```powershell
# Open PowerShell as Administrator:
Start-Process powershell -Verb RunAs

# Then execute the script:
.\script.ps1
```

### `#Requires -RunAsAdministrator` Error
This error occurs if you double-clicked on the `.ps1` file instead of right-clicking and selecting "Run as Administrator."

To resolve, open PowerShell as an administrator and run the script from there.

```powershell
# Run in an admin session:
.\script.ps1
```

### File Path Error
Ensure that the path to the script is correct. Use commands like `dir` or `Get-ChildItem` to verify the file's location.

```powershell
cd $env:USERPROFILE\Downloads
dir *.ps1

# Or find the full path:
Get-ChildItem -Path C:\Users -Recurse -Filter "script.ps1" -ErrorAction SilentlyContinue | Select-Object FullName
```

### Encoding Issue
If you encounter parser errors due to encoding issues, rewrite the script with a proper UTF-8 BOM.

```powershell
# Rewrite the file:
$content = Get-Content "C:\path\to\script.ps1" -Raw -Encoding UTF8
Set-Content "C:\path\to\script.ps1" -Value $content -Encoding UTF8
```

## References
- [Set-ExecutionPolicy Documentation](https://docs.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-7.3)
- [Run PowerShell as Administrator](https://docs.microsoft.com/en-us/powershell/scripting/learn/get-started-elevate-your-powershell-session?view=powershell-7.3)

## Related
- [[cs-Scripting-Basics]] — Basic scripting concepts and best practices.
- [[cs-PowerShell-Guides]] — Comprehensive guides for PowerShell scripting.
- [[cs-Windows-Security]] — Security considerations when running scripts on Windows.