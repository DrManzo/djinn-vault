---
subject: djinn/technology/app-development/dnd-tools
tags:
  - cs/software-development
  - cs/image-processing
  - creative/dnd-tools
  - personal/technology
created: 2026-06-14
source: Perplexity export
---

# Djinn Dice Scanner

## Summary
This note documents the development of a web-based application, "Djinn Dice Scanner," designed to capture images of dice for Dungeons & Dragons (DND) and automatically sum their values.

## Key Points
- **Live Camera Capture**: Direct access to device's rear-facing camera.
- **Upload Functionality**: Supports uploading photos from gallery or filesystem.
- **Dice Detection**: Uses computer vision techniques like grayscale conversion, adaptive thresholding, and connected-component blob detection for accurate dice value recognition.
- **Manual Override**: Allows manual addition or removal of detected dice.
- **Stat Assignment**: Assigns dice values to DND stats (STR, DEX, CON, INT, WIS, CHA) with auto-assignment functionality.

## Details
The application is built as a static HTML file and can be integrated into the Djinn project's frontend. The core vision logic resides in the `detectDiceFromCanvas()` function, which could potentially be enhanced using a local Ollama vision model for higher accuracy.

### Features

**📸 Image Capture**
- **Live Camera**: Direct access to device’s rear-facing camera.
- **Upload**: Supports photos from gallery or filesystem. Falls back to upload-only if camera permission is denied.

**🎲 Dice Detection**
- Converts image to grayscale and applies adaptive thresholding.
- Runs connected-component blob detection for pips (dots).
- Clusters blobs spatially to identify individual dice and their face values.
- Best results with flat, well-lit surface, spread-out dice without overlapping, and standard pip dice.

**Manual Override**
- Allows adding or removing dice manually if detection is inaccurate.

**⚔️ D&D Stat Assignment**
- Clicks on dice in the pool to select them (they highlight + running total shows).
- Assigns values to stats with auto-assignment functionality.
- Modifiers are calculated and color-coded (green for positive, red for negative).
- Exports a clean `.txt` stat block.

## References
- [Computer Vision Basics](https://math.mit.edu/~djk/calculus_beginners/chapter00/section02.html)

## Related
- [[Source-Keeper-Overview]] — similarity
- [[Smart-Pens-Handwritten-Note-Digitization]] — digitization
