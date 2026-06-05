---
subject: 3d-printing/printer-maintenance/report-generation
tags:
  - 3d-printing/models/ender-3-v3-plus
  - 3d-printing/models/benchmark-3343
  - 3d-printing/glassware/attachment
  - personal/design
created: 2026-06-04
source: Perplexity export
---

# Report on Legibility Issues with Embossed Text

## Summary
This report documents a legibility issue encountered during the printing of embossed text using an Ender 3v3+ printer. The current settings are producing illegible text, which needs to be addressed by adjusting the font size, typeface, and engraving depth.

## Key Points
- **Current Issue**: Text is illegible due to small size and poor resolution.
- **Suggested Actions**:
  - Use a bold sans-serif font.
  - Increase text height and spacing.
  - Deepen emboss/deboss depth.
  - Test with a flat text patch before full print.

## Details
The issue arises from the current settings, which are not suitable for printing legible embossed text. The text is being converted into abstract shapes rather than readable letters. Here’s a detailed breakdown of the problem and proposed solutions:

### Problem Analysis
- **Font Size**: The font size may be too small for the nozzle and layer height.
- **Text Geometry**: The text might be turned into outlines or relief geometry, losing its internal structure.
- **Spacing and Depth**: Letters are too close together or the depth is insufficient, causing them to merge into broken bands.

### Suggested Solutions
1. **Use a Bold Sans-Serif Font**:
   - This will ensure that the text remains legible even at smaller sizes.
2. **Increase Text Height and Spacing**:
   - Test with larger font sizes and increased spacing to improve readability.
3. **Deepen Emboss/Deboss Depth**:
   - Ensure the embossed/debossed text has a sufficient depth to survive slicing.

### Practical Fix Path
1. Open the model in CAD software.
2. Confirm that the text is still represented as actual letters, not broken outlines or meshes.
3. Switch to a bold font and increase the text size.
4. Test with a flat test coupon containing just the text before printing the full ring.

## References
- [engravers.com/embossing-vs-engraving](https://www.engravers.com/embossing-vs-engraving)
- [youtube.com/watch?v=aEvBC0lSbEg](https://www.youtube.com/watch?v=aEvBC0lSbEg)
- [autodesk.com/community/t5/inventor-forum/problems-embossing-engraving/td-p/11855570](https://forums.autodesk.com/t5/inventor-forum/problems-embossing-engraving/td-p/11855570)
- [printingforless.com](https://www.printingforless.com)

## Related
- [[Preparing-Your-Ender-3-V3-Plus-For-Printing]] — similarity 0.70
- [[3d-Printing-Filament-Recommendations-For-Ender-3-V3]] — similarity 0.71
