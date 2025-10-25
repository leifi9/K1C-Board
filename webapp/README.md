# K1C-Board Web UI

Web-based user interface for the K1C-Board 3D Model Generator.

## Features

- 🎨 Modern React + TypeScript frontend
- 🚀 Flask REST API backend
- 📁 File upload support for images, videos, and CAD files
- 💬 Text-to-3D model generation
- 🔧 Multiple output formats (STL, STEP, OBJ)
- 🌐 Optional web search integration
- 📊 Real-time progress tracking

## Installation

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- Blender and FreeCAD (for full functionality)

### Frontend Setup

```bash
cd webapp
npm install
```

### Backend Setup

```bash
cd webapp
pip install -r requirements.txt
```

Also install the main auto-3d-agent dependencies:

```bash
cd ../auto-3d-agent
pip install -r requirements.txt
```

## Usage

### Development Mode

You can run the frontend and backend separately or together:

#### Option 1: Run Both Servers Separately

Terminal 1 - Backend API:
```bash
cd webapp
python server.py
```

Terminal 2 - Frontend Dev Server:
```bash
cd webapp
npm run dev
```

#### Option 2: Use VSCode Launch Configuration

1. Open the project in VSCode
2. Go to Run and Debug (Ctrl+Shift+D)
3. Select "Full Stack: Backend + Frontend"
4. Click Start Debugging (F5)

The webapp will open automatically at `http://localhost:3000`

### Production Build

```bash
cd webapp
npm run build
```

The production files will be in `webapp/dist/`

## Project Structure

```
webapp/
├── src/
│   ├── components/      # React components
│   │   ├── App.tsx      # Main app component
│   │   └── App.css      # App styles
│   ├── services/        # API services
│   │   └── api.ts       # API client
│   ├── types/           # TypeScript type definitions
│   │   └── index.ts     # Shared types
│   ├── utils/           # Utility functions
│   └── index.tsx        # Entry point
├── public/              # Static files
│   └── index.html       # HTML template
├── server.py            # Flask API server
├── package.json         # NPM dependencies
├── tsconfig.json        # TypeScript config
├── webpack.config.js    # Webpack config
└── requirements.txt     # Python dependencies
```

## API Endpoints

- `GET /api/health` - Health check
- `POST /api/upload` - Upload input files
- `POST /api/generate` - Generate 3D model
- `GET /api/progress/:jobId` - Check generation progress
- `GET /api/outputs` - List generated files

## Configuration

### TypeScript Module Resolution

The project uses path aliases for cleaner imports:

```typescript
import Component from '@components/Component';
import api from '@services/api';
import type { MyType } from '@app-types/index';
```

**Note**: We use `@app-types` instead of `@types` to avoid conflicts with TypeScript's built-in `@types` directory handling. This prevents the TS6137 error "Cannot import type declaration files".

These are configured in:
- `tsconfig.json` - TypeScript compiler
- `webpack.config.js` - Webpack bundler

### Proxy Configuration

The webpack dev server proxies `/api` requests to the Flask backend running on port 5000.

## Troubleshooting

### Module Import Errors

If you encounter TypeScript module import errors:

1. Ensure all dependencies are installed: `npm install`
2. Check that path aliases match in `tsconfig.json` and `webpack.config.js`
3. Restart the TypeScript server in VSCode: Ctrl+Shift+P → "TypeScript: Restart TS Server"

### Backend Connection Issues

If the frontend can't connect to the backend:

1. Ensure the Flask server is running on port 5000
2. Check the proxy configuration in `webpack.config.js`
3. Verify CORS is enabled in `server.py`

## License

MIT
