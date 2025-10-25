# K1C-Board

K1C-Board is a platform for AI-powered agents and tools designed to automate complex tasks, featuring a modern web UI for 3D model generation.

## Features

- 🎨 **Web-based UI** - Modern React + TypeScript interface for easy interaction
- 🤖 **Auto 3D Agent** - Fully automated 3D model generation from text, images, and videos
- 🔧 **Multiple Input Types** - Text descriptions, images, videos, and CAD files
- 📦 **Multiple Output Formats** - STL (3D printing), STEP (CAD), OBJ (general)
- 🌐 **Web Integration** - Optional web search, GitHub, and Reddit integration
- ⚡ **REST API** - Flask-based API for programmatic access

## Included Agents

- **Auto 3D Agent**: A fully automated system to generate 3D models from text, images, and videos, optimized for CAD applications.
- **Web UI**: Modern TypeScript/React interface for easy interaction with the 3D generator.
- Other agents can be added here.

## Quick Start

### Web UI (Recommended)

1. **Install Dependencies**
   ```bash
   # Frontend
   cd webapp
   npm install
   
   # Backend
   pip install -r requirements.txt
   cd ../auto-3d-agent
   pip install -r requirements.txt
   ```

2. **Start the Application**
   
   Option A - Using VSCode:
   - Open the project in VSCode
   - Press F5 and select "Full Stack: Backend + Frontend"
   
   Option B - Manual:
   ```bash
   # Terminal 1 - Backend
   cd webapp
   python server.py
   
   # Terminal 2 - Frontend
   cd webapp
   npm run dev
   ```

3. **Open Browser**
   Navigate to `http://localhost:3000`

### Command Line

For command-line usage, please refer to `auto-3d-agent/README.md`.

## Getting Started

Please refer to the `auto-3d-agent/README.md` for detailed instructions on the Auto 3D Agent.

For the web UI, see `webapp/README.md`.

## Project Structure

- `webapp/` - Modern web UI for 3D model generation (TypeScript/React)
- `auto-3d-agent/` - 3D model generation agent using Blender and FreeCAD
- `.github/` - GitHub workflows and templates
- `AGENTS.md` - List of available agents
- `TODO.md` - Project roadmap and tasks

## Documentation

- [Web UI Documentation](webapp/README.md)
- [Auto 3D Agent Documentation](auto-3d-agent/README.md)
- [Usage Examples](auto-3d-agent/EXAMPLE_USAGE.md)
- [Adapter Generator](auto-3d-agent/README_ADAPTER.md)

## Requirements

- Node.js 16+ and npm (for web UI)
- Python 3.8+
- Blender (for 3D modeling)
- FreeCAD (for CAD export)

## API Endpoints

The Flask backend provides the following REST API:

- `GET /api/health` - Health check
- `POST /api/upload` - Upload input files
- `POST /api/generate` - Generate 3D model
- `GET /api/progress/:jobId` - Check generation progress
- `GET /api/outputs` - List generated files

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

