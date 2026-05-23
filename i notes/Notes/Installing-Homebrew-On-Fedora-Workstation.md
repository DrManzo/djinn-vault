---
subject: business/technology/software-architecture
tags:
  - cs/software-installation
  - ai/development/fedora/workstation
  - business/career-factors/income-stability
created: 2026-05-23
source: Perplexity export
---

# Installing Homebrew on Fedora Workstation

## Summary
This note provides a step-by-step guide for installing Homebrew on the latest Fedora Workstation.

## Key Points
- Install prerequisites using `sudo dnf`.
- Run the official Homebrew installer.
- Add Homebrew to your PATH in the shell configuration.
- Verify installation with `brew --version`, `brew doctor`, and `hello`.

## Details
1. **Install Prerequisites**
   - Open a terminal and run:
     ```bash
     sudo dnf group install "Development Tools"
     sudo dnf install -y procps-ng curl file git
     ```
   - The “Development Tools” group includes gcc, make, and related build tools.
   - `procps-ng`, `curl`, `file`, and `git` are also required by the installer.

2. **Run the Official Homebrew Installer**
   - Still in the terminal, run:
     ```bash
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```
   - This installs to `/home/linuxbrew/.linuxbrew` by default and uses `sudo` only during installation.

3. **Add Homebrew to Your PATH (Fedora Shell Setup)**
   - The installer will print “Next steps” showing what to put in your shell config.
   - For Bash, it is:
     ```bash
     echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv bash)"' >> ~/.bashrc
     eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv bash)"
     ```
   - If you use Zsh or Fish, the installer output will show the appropriate `shellenv` command.

4. **Verify Installation**
   - Run:
     ```bash
     brew --version
     brew doctor
     brew install hello
     hello
     ```
   - `brew --version` should print a version string.
   - `brew doctor` diagnoses setup issues.
   - Installing and running `hello` confirms Homebrew can download, install, and execute packages.

5. **Fedora-Specific Cautions**
   - Prefer Fedora RPMs or Flatpaks first; use Homebrew as an extra user-space package manager when needed.
   - Remember Homebrew is not officially supported by Fedora, so if something breaks, you may need to remove it.

## References
- [Fedora Magazine](https://fedoramagazine.org/how-to-install-homebrew-on-fedora-linux/)
- [Linux Capable](https://linuxcapable.com/how-to-install-homebrew-on-fedora-linux/)
- [Brew Documentation](https://docs.brew.sh/)

## Related
- [[Fedora-Workstation-Ide-Recommendations-For-Ai-Development]] — fedora workstation setup
