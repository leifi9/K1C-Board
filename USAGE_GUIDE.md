# K1C-Board Web UI - Complete Usage Guide

## Overview

The K1C-Board Web UI provides an intuitive interface for generating 3D models from various input types. This guide will walk you through installation, configuration, and usage.

## Table of Contents

1. [Installation](#installation)
2. [Starting the Application](#starting-the-application)
3. [Using the Web Interface](#using-the-web-interface)
4. [Troubleshooting](#troubleshooting)
5. [Advanced Configuration](#advanced-configuration)

## Installation

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js 16 or higher** - [Download](https://nodejs.org/)
- **Python 3.8 or higher** - [Download](https://www.python.org/)
- **npm** (comes with Node.js)
- **pip** (comes with Python)

### Step 1: Install Frontend Dependencies

```bash
cd webapp
npm install
```

This will install all required JavaScript packages including:
- React and React DOM
- TypeScript
- Webpack and related tools
- Axios for API communication

### Step 2: Install Backend Dependencies

```bash
# Install webapp backend dependencies
cd webapp
pip install -r requirements.txt

# Install 3D generator dependencies
cd ../auto-3d-agent
pip install -r requirements.txt
```

### Step 3: (Optional) Install Blender and FreeCAD

For full functionality, install:
- **Blender 3.0+** - [Download for Windows/Mac/Linux](https://www.blender.org/download/)
- **FreeCAD 0.20+** - [Download for Windows/Mac/Linux](https://www.freecad.org/downloads.php)

Without these, the webapp will run in mock mode for testing.

## Starting the Application

### Option 1: Using VSCode (Recommended)

1. Open the K1C-Board folder in Visual Studio Code
2. Press `F5` or go to Run → Start Debugging
3. Select "Full Stack: Backend + Frontend" from the dropdown
4. Both servers will start automatically
5. Your browser will open to `http://localhost:3000`

### Option 2: Manual Start

Open two terminal windows:

**Terminal 1 - Backend Server:**
```bash
cd webapp
python server.py
```

You should see:
```
Starting K1C-Board API Server...
Upload folder: /path/to/webapp/uploads
Output folder: /path/to/auto-3d-agent/output
Backend mode: available (or mock)
 * Running on http://0.0.0.0:5000
```

**Terminal 2 - Frontend Server:**
```bash
cd webapp
npm run dev
```

You should see:
```
webpack 5.x.x compiled successfully
Project is running at http://localhost:3000
```

The frontend will automatically proxy API requests to the backend.

## Using the Web Interface

### Step 1: Select Input Type

Choose how you want to provide input for your 3D model:

- **Text Description** - Describe the model in words
- **Image** - Upload a reference image
- **Video** - Upload a video showing the object
- **CAD File** - Upload an existing CAD file (STEP, STL, OBJ)

### Step 2: Provide Input

#### For Text Input:
Type a description of the 3D model you want to generate, for example:
```
"A cylindrical adapter with a 25mm outer diameter on one end 
and a 20mm inner diameter on the other end, 50mm long"
```

#### For File Input:
1. Click the "Choose File" button
2. Select your input file
3. Wait for the upload to complete
4. The filename will appear below the button

### Step 3: Configure Output

1. **Output Format**: Choose from:
   - **STL** - Best for 3D printing
   - **STEP** - Best for CAD applications
   - **OBJ** - General purpose 3D format

2. **Output Path**: Specify where to save the file (default: `./output`)

### Step 4: Enable Data Sources (Optional)

For better results, you can enable:
- **Web Search** - Search the web for reference models
- **GitHub** - Find related projects on GitHub
- **Reddit** - Look for community discussions

### Step 5: Generate

Click the "Generate 3D Model" button. You'll see:
- A progress bar (if available)
- Status messages showing what's happening
- The output file path when complete

### Step 6: Access Your Model

When generation completes, you'll see:
```
Generation Complete!
Output file: /path/to/output/generated_model_xxx.stl
```

The file will be saved to the specified output directory.

## Troubleshooting

### Frontend won't start

**Error**: "Cannot find module..."
```bash
cd webapp
rm -rf node_modules package-lock.json
npm install
```

**Error**: TypeScript errors
```bash
npm run type-check
```
This will show any type errors. Usually fixed by updating imports.

### Backend won't start

**Error**: "No module named 'flask'"
```bash
pip install -r webapp/requirements.txt
```

**Error**: "Could not import AdapterCreationApp"
This is expected if Blender isn't installed. The server runs in mock mode.

### Connection refused to API

1. Ensure backend is running on port 5000
2. Check the browser console for errors
3. Verify proxy configuration in `webpack.config.js`:
   ```javascript
   proxy: [{
     context: ['/api'],
     target: 'http://localhost:5000'
   }]
   ```

### File upload fails

1. Check file size (max 100MB)
2. Verify file extension is allowed:
   - Images: png, jpg, jpeg, gif
   - Videos: mp4, avi, mov
   - CAD: step, stp, stl, obj
3. Check backend console for errors

## Advanced Configuration

### Changing Backend Port

Edit `webapp/server.py`:
```python
app.run(host='0.0.0.0', port=5000, debug=True)  # Change port here
```

And update `webapp/webpack.config.js`:
```javascript
devServer: {
  // ... other settings
  proxy: [{
    context: ['/api'],
    target: 'http://localhost:5000',  // Change port here
    changeOrigin: true,
  }],
}
```

### Changing Frontend Port

Edit `webapp/webpack.config.js`:
```javascript
devServer: {
  port: 3000,  // Change this
  // ...
}
```

### Enabling Production Mode

Build the production bundle:
```bash
cd webapp
npm run build
```

Serve with a production server:
```bash
# Using Python's built-in server
python -m http.server -d dist 8080
```

### Environment Variables

Create `webapp/.env`:
```
API_BASE_URL=http://localhost:5000
MAX_FILE_SIZE=104857600
```

To use these in webpack, install `dotenv-webpack`:
```bash
npm install --save-dev dotenv-webpack
```

Then update `webpack.config.js`:
```javascript
const Dotenv = require('dotenv-webpack');

module.exports = {
  // ... other config
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
    new Dotenv(),  // Add this
  ],
};
```

## Development Tips

### Hot Reload

The development server supports hot reload. Changes to TypeScript/React files will automatically refresh the browser.

### Debugging

1. Open browser DevTools (F12)
2. Go to Sources tab
3. Source maps are enabled, so you can debug TypeScript directly
4. Set breakpoints in `.tsx` files

### API Testing

Test API endpoints directly:
```bash
# Health check
curl http://localhost:5000/api/health

# Upload file
curl -X POST -F "file=@test.png" http://localhost:5000/api/upload

# Generate model (mock)
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"config": {"inputType": "text", "inputText": "test model", "outputFormat": "stl", "outputPath": "./output"}}'
```

### TypeScript Type Checking

Run type checking without building:
```bash
npm run type-check
```

### Linting

Check code quality:
```bash
npm run lint
```

## Production Deployment

### Build Production Assets

```bash
cd webapp
npm run build
```

### Serve with NGINX

Example NGINX configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/webapp/dist;
        try_files $uri /index.html;
    }

    # API Proxy
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Run Backend with Gunicorn

```bash
pip install gunicorn
cd webapp
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

## Support

For issues or questions:
1. Check the [README.md](README.md)
2. Review [auto-3d-agent documentation](../auto-3d-agent/README.md)
3. Open an issue on GitHub

## License

MIT License - see LICENSE file for details.
