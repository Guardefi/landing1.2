# 🚀 Scorpius Frontend - Windows Setup Guide

## Quick Start (PowerShell)

```powershell
# 1. Navigate to the frontend directory
cd frontend

# 2. Run the automated setup script
.\setup-windows.ps1

# 3. Start the development server
npm run dev
```

## Manual Setup

### Prerequisites

1. **Node.js 18+** - Download from [nodejs.org](https://nodejs.org)
2. **Windows PowerShell** (recommended) or Command Prompt
3. **Git** (optional) - For version control

### Step-by-Step Installation

```powershell
# 1. Check your Node.js version
node --version
# Should show v18.x.x or higher

# 2. Check npm version
npm --version
# Should show 8.x.x or higher

# 3. Clean any previous installations
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue

# 4. Clear npm cache
npm cache clean --force

# 5. Install dependencies
npm install --legacy-peer-deps

# 6. Start the development server
npm run dev
```

## Common Issues & Solutions

### ❌ "npm install" fails

**Solution 1**: Use legacy peer deps

```powershell
npm install --legacy-peer-deps
```

**Solution 2**: Use force flag

```powershell
npm install --force
```

**Solution 3**: Clear everything and retry

```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json
npm cache clean --force
npm install
```

### ❌ "Cannot find module" errors

**Cause**: Missing dependencies or path issues

**Solution**:

```powershell
# Reinstall dependencies
npm ci

# Or reinstall specific packages
npm install @types/react @types/react-dom
```

### ❌ Port 3000 already in use

**Solution**: Kill the process or use different port

```powershell
# Kill process on port 3000
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process

# Or use different port
$env:VITE_PORT=3001; npm run dev
```

### ❌ Video not loading on login page

**Cause**: Missing video file or browser compatibility

**Solution**: This is normal - the app uses a fallback animated background when video is unavailable.

### ❌ Styling looks broken

**Cause**: CSS not loading properly or missing Tailwind compilation

**Solution**:

```powershell
# Restart the dev server
npm run dev

# Clear browser cache (Ctrl + Shift + R)

# Check if tailwind.config.ts exists
Get-ChildItem tailwind.config.ts
```

### ❌ API errors (500 Internal Server Error)

**Cause**: Backend services not running

**Solution**: This is expected behavior. The app works in demo mode when backend is unavailable.

- Visit `http://localhost:3000/api/status` to check backend health
- All pages work with mock data when backend is down
- See the integration status in the API Status page

## Environment Configuration

The app uses these environment variables (configured in `.env`):

```env
VITE_API_BASE_URL=http://localhost:8000      # Backend API URL
VITE_WS_BASE_URL=ws://localhost:8000         # WebSocket URL
VITE_GRAFANA_URL=http://localhost:3001       # Grafana URL
VITE_PORT=3000                               # Dev server port
VITE_DEMO_MODE=true                          # Enable demo mode
```

## Development Commands

```powershell
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run type checking
npm run typecheck

# Run tests
npm test

# Fix code formatting
npm run format.fix

# Run linting
npm run lint
```

## Browser Compatibility

**Recommended browsers**:

- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+

**Features requiring modern browser**:

- CSS Grid and Flexbox
- CSS Variables
- ES2020+ JavaScript features
- WebSocket connections

## Performance Tips

### For better development experience:

1. **Use fast storage**: Install on SSD if possible
2. **Close other applications**: Free up RAM for Node.js
3. **Use PowerShell**: Better terminal support than CMD
4. **Enable WSL2**: For better Node.js performance (optional)

### For better app performance:

1. **Use Chrome DevTools**: Monitor performance and network
2. **Check API Status**: Visit `/api/status` to see what's working
3. **Enable Hardware Acceleration**: In browser settings
4. **Close unused browser tabs**: Free up memory

## Troubleshooting Network Issues

### CORS Errors

The Vite dev server is configured with CORS proxy. If you see CORS errors:

1. Check if backend is running on `http://localhost:8000`
2. Verify the `VITE_API_BASE_URL` in `.env`
3. Restart the dev server after changing `.env`

### WebSocket Connection Issues

WebSocket connections may fail in some network configurations:

1. Check if backend WebSocket server is running
2. Try disabling VPN or proxy
3. Check Windows Firewall settings
4. The app will fallback to polling if WebSockets fail

## Getting Help

### Check Application Status

1. Visit `http://localhost:3000/api/status` after starting the app
2. This page shows the health of all backend integrations
3. Green = working, Red = needs attention

### Debug Information

When reporting issues, include:

1. **Node.js version**: `node --version`
2. **npm version**: `npm --version`
3. **Windows version**: `winver`
4. **Browser and version**
5. **Console errors** (F12 → Console)
6. **Network errors** (F12 → Network)

### Support Resources

- **API Status Page**: `/api/status` - Real-time integration health
- **Browser Console**: F12 → Console - JavaScript errors
- **Network Tab**: F12 → Network - API call failures
- **Application Tab**: F12 → Application - Local storage issues

---

## ✅ Success Indicators

When everything is working correctly, you should see:

1. **Development server starts** without errors
2. **Browser opens** to `http://localhost:3000`
3. **Login page loads** with animated background
4. **No console errors** in browser developer tools
5. **API Status page** shows service health at `/api/status`
6. **Smooth animations** and responsive UI
7. **Demo data** loads correctly throughout the app

The app is designed to work perfectly even without a backend, providing a complete demo experience!
