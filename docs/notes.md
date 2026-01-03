# Development Notes & Ideas

## Completed Features ✅

- ✅ English language support
- ✅ User copy-paste text upload
- ✅ PDF and Word file upload
- ✅ Latvian simplifier with separate editing program
- ✅ Simplifier as checkbox for English
- ✅ Audio TTS integration
- ✅ Difficulty levels for questions

## Current Tasks 🚧

- Improve simplifier (Latvian)
- Play with question maker prompt for more creativity
- Make UI a bit less wide

## Future App Ideas 💡

### Short-term
1. Add audio to default library
2. Highlight wrong/right answers (if user answers wrong or right, text fragment with right answer is highlighted)
3. Add "read again" button
4. Adjust text fragment limitation (text splitter makes too big fragments - need to fit screen better)
5. Add "TO UPPER" button (button that makes text fragment uppercased)
6. Open fragment one by default (when user uploads text, auto open fragment one)
7. Translation fixes (when user opens any language, UI should follow chosen language)
8. Audio text highlight (synchronize highlighting with audio playback)

### Long-term
1. Image description feature ("Apraksti attēlu")
2. Video comprehension ("Skaties video un atbildi uz jautājumiem")
3. AI for science books
4. Book UI (optional for now, but as idea of UI)

## Technical Notes 📝

### TTS Integration
Currently using HuggingFace Spaces for TTS:
- English: MohamedRashad/Multilingual-TTS
- Latvian: RaivisDejus/Latvian-Piper-TTS
- Spanish: MohamedRashad/Multilingual-TTS
- Russian: MohamedRashad/Multilingual-TTS

### Alternative UI Frameworks
Considered for future desktop version:
- tkinter - Built-in Python GUI library, good for simple apps
- PyQt5/PyQt6 or PySide6 - More powerful, professional-looking GUIs
- Kivy - For cross-platform apps including mobile

## Known Issues 🐛

- Simplifier occasionally returns to previous version
- Text fragments can be too large for comfortable screen reading
- UI translations don't always follow language selection

## Optimization Complete (Dec 2024) ✨

- Reduced dependencies from 3.7GB → 220MB
- Centralized LLM initialization
- Removed code duplication
- Added structured logging
- PythonAnywhere deployment ready

