---
title: "PyQt6 Modular UI Architecture"
created: 2026-05-19
modified: 2026-05-19
tags: [python, pyqt6, gui-development, modular-programming, ui-design, software-architecture, widget-design]
source: "Perplexity AI Export"
category: "Computer Science/Python"
---

## Summary
A guide to structuring PyQt6 desktop applications using modular programming principles, demonstrated through the "Notation Clark" reference card system. The architecture separates UI components (windows, buttons, dialogs, images, styles) into individual scripts imported by a main controller file, improving maintainability, testability, and scalability.

## Key Points
- Modular programming splits UI components into separate files by responsibility
- Each module handles a single concern: window logic, widget creation, styling, data, or layout
- Main file acts as controller, importing and connecting all components
- Enables independent testing, easier debugging, and straightforward extension
- Demonstrated with a complete 8-file PyQt6 application structure
- Follows separation of concerns and single responsibility principles
- Supports Python 3.14+ with explicit imports and clear documentation

## Details

### Recommended Project Structure
```
notation_clark_modular/
├── main.py              # Entry point - run this file
├── window.py            # Main window class (NotationClarkApp)
├── sidebar.py           # Sidebar creation functions
├── content_area.py      # Content area creation functions
├── card_widget.py       # IndexCard widget class
├── card_list_item.py    # CardListItem widget class (sidebar previews)
├── styles.py            # All CSS styling definitions
└── sample_data.py       # Sample data generation
```

### Module Responsibilities

#### `styles.py` - Centralized Styling
- Defines color palette as dictionary constants
- Provides functions returning CSS strings for each widget type
- Examples: `get_sidebar_background()`, `get_card_style()`, `get_nav_button_style()`
- Single source of truth for visual design; changing colors updates entire app

#### `sample_data.py` - Test Data
- `create_sample_data()` returns list of card dictionaries
- Each card contains: ref_number, category, tags, title, content, date, source
- Replace with database queries in production

#### `card_widget.py` - IndexCard Class
- Custom `QFrame` subclass representing a single reference card
- Fixed size (600x400) mimicking physical index cards
- Horizontal layout: left margin (red line) + right content area
- Displays: reference number, category badge, tags, title, scrollable content, footer with date/source
- Applies styles from `styles.py`

#### `card_list_item.py` - CardListItem Class
- Small clickable preview items in sidebar
- Shows: reference number, category, title
- Fixed height (80px)
- `on_click()` event tells parent app to display corresponding full card
- Hover effects for better UX

#### `sidebar.py` - Sidebar Creation
- `create_sidebar(app_instance)` builds left panel
- Contains: title, search box (with live filtering), scrollable card list, "New Card" button
- `populate_card_list(app_instance)` creates `CardListItem` for each card
- Fixed width (300px), doesn't resize

#### `content_area.py` - Content Area Creation
- `create_content_area(app_instance)` builds right panel
- Centers card display with horizontal stretchers
- Navigation buttons: Previous/Next with card counter (e.g., "1 / 3")
- Buttons connected to `previous_card()` and `next_card()` methods

#### `window.py` - Main Application Logic
- `NotationClarkApp(QMainWindow)` class
- `setup_window()`: Configures title, geometry, background
- `create_ui()`: Assembles sidebar + content area in horizontal layout
- `display_card(index)`: Renders specific card, updates counter
- `next_card()` / `previous_card()`: Navigation with bounds checking
- `filter_cards(search_text)`: Live search across title, category, tags, content

#### `main.py` - Entry Point
- Creates `QApplication`, sets default font
- Instantiates and shows `NotationClarkApp`
- Starts event loop with `sys.exit(app.exec())`

### Key Design Patterns
- **Controller Pattern**: `main.py` and `window.py` orchestrate component interaction
- **Factory Functions**: `create_sidebar()` and `create_content_area()` build complex widgets
- **Event-Driven Architecture**: Qt signal/slot connections handle user interactions
- **Data-Driven UI**: Card data stored in list of dicts, UI reflects data state

### Benefits
1. Easy to maintain - Each component in its own file
2. Easy to test - Test individual components separately
3. Easy to modify - Change styles without touching logic
4. Easy to extend - Add new card types or widgets easily
5. Reusable - Import components into other projects
6. Clean - Each file has one clear purpose

### Running the Application
```bash
python main.py
```

## References
- PyQt6 Documentation: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- Qt Widget Styling with CSS
- Perplexity AI Chat Export (2026-05-19)

## Related
- [[Python Programming Hub]]
- [[Scrambled Notes to APA Essay Converter]]
- [[Django Template Conversion Guide]]
- [[Django-Template-Conversion-Guide]]
- [[Scrambled-Notes-to-APA-Essay-Converter]]
