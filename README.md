# Aura AI Design Assistant

## Overview
Aura is a professional-grade Blender add-on that provides advanced AI-powered 3D design capabilities. It integrates ONNX Runtime, robust mesh tools, manufacturing analysis, and asset management into a streamlined workflow for designers and engineers.

## Features
- **AI Generation**: Create new 3D models from text prompts using ONNX-based AI models.
- **Detail Addition**: Add AI-generated details to existing objects, with asynchronous processing for a responsive UI.
- **Manufacturing Analysis**: Run checks for wall thickness, prong integrity, and other manufacturability criteria.
- **Asset Library**: Easily add and manage reusable components from a built-in library.
- **Import/Export**: Seamless import/export of OBJ and STL files.
- **User Preferences**: Configure model paths, compute device (CPU/GPU), and analysis settings.
- **Dependency Management**: All Python dependencies are managed via `requirements.txt` and packaged in the `vendor/` folder for Blender compatibility.

## Codebase Structure
```
frontend/
  aura_panel.py         # All UI panels and operators
backend/
  aura_backend.py       # All backend logic (AI, mesh, analysis, interop)
  aura_helpers.py       # Helper functions (paths, vendor setup)
settings.py             # Scene/session settings
preferences.py          # User preferences
setup.py                # Add-on registration and setup
requirements.txt        # Python dependencies
assets/
  library/              # Asset library (blend files, README)
models/                 # AI model files (.onnx, README)
vendor/                 # Packaged Python dependencies for Blender
README.md               # This documentation
```

## Installation & Setup
1. **Clone the repository**:
   ```
   git clone https://github.com/elliotttmiller/aura.git
   ```
2. **Create a virtual environment** (recommended):
   ```
   python -m venv venv
   .\venv\Scripts\Activate
   ```
3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```
4. **Copy dependencies to vendor/**:
   - Manually copy all installed packages from `venv/Lib/site-packages` to `vendor/` for Blender compatibility.
5. **Install the add-on in Blender**:
   - Zip the `aura` folder and install via Blender's Add-ons menu.

## Usage
- Access the Aura panels in Blender's Sidebar under the "Design" tab.
- Configure preferences (model path, compute device, wall thickness) in the add-on settings.
- Use the AI panel to generate models or add details.
- Run manufacturing analysis from the Analysis panel.
- Add assets from the Library panel.
- Import/export models using the Workflow panel.

## Development Workflow
- All code is modular and future-proofed, with dependencies imported at the top of each file.
- Backend and frontend logic are fully merged for maintainability.
- Async operations ensure Blender UI remains responsive during heavy processing.
- All advanced logic is consolidated in `aura_backend.py` and `aura_panel.py`.

## Contributing
- Fork the repo and submit pull requests for new features or bug fixes.
- Ensure all new dependencies are added to `requirements.txt` and tested in Blender.

## License
MIT License

## Contact
For support or collaboration, contact elliotttmiller on GitHub.
