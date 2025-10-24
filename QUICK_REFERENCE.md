# K1C-Board Quick Reference

## Quick Start

```bash
# Install
cd webapp && npm install && pip install -r requirements.txt

# Start (Option 1: VSCode)
Press F5 → Select "Full Stack: Backend + Frontend"

# Start (Option 2: Manual)
# Terminal 1:
cd webapp && python server.py

# Terminal 2:
cd webapp && npm run dev

# Open browser
http://localhost:3000
```

## Common Commands

```bash
# Frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run type-check   # Check TypeScript types
npm run lint         # Lint code

# Backend
python server.py     # Start Flask API server

# Testing
curl http://localhost:5000/api/health  # Test API
```

## File Structure

```
webapp/
├── src/
│   ├── components/App.tsx     # Main UI component
│   ├── services/api.ts        # API client
│   ├── types/index.ts         # TypeScript types
│   └── index.tsx              # Entry point
├── server.py                  # Flask backend
├── package.json               # NPM config
└── tsconfig.json              # TypeScript config
```

## TypeScript Path Aliases

```typescript
import App from '@components/App';
import api from '@services/api';
import type { Config } from '@app-types/index';
```

Note: Use `@app-types/*` not `@types/*` to avoid TypeScript error TS6137 (conflicts with built-in type declaration packages).

## API Endpoints

```
GET  /api/health              # Health check
POST /api/upload              # Upload file
POST /api/generate            # Generate model
GET  /api/progress/:jobId     # Check progress
GET  /api/outputs             # List outputs
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Module not found | `npm install` |
| TypeScript errors | `npm run type-check` |
| Backend won't start | `pip install -r requirements.txt` |
| Port already in use | Change port in config files |
| Import errors | Check path aliases in tsconfig.json |

## Configuration Files

- `tsconfig.json` - TypeScript compiler settings
- `webpack.config.js` - Webpack bundler config
- `package.json` - NPM dependencies
- `.eslintrc.json` - Code linting rules
- `server.py` - Flask backend configuration

## Development Tips

1. **Hot Reload**: Frontend auto-reloads on file changes
2. **Source Maps**: Debug TypeScript directly in browser
3. **Mock Mode**: Backend works without Blender/FreeCAD for testing
4. **VSCode**: Use F5 to start both servers together

## Production Deployment

```bash
# Build
npm run build

# Serve frontend (option 1)
python -m http.server -d dist 8080

# Serve backend with Gunicorn (option 2)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```

## Documentation

- Full guide: [USAGE_GUIDE.md](USAGE_GUIDE.md)
- Webapp docs: [webapp/README.md](webapp/README.md)
- 3D Agent docs: [auto-3d-agent/README.md](auto-3d-agent/README.md)

## Support

- GitHub Issues: Report bugs or request features
- Check logs: Browser console & terminal output
- Review docs: README files in each directory
