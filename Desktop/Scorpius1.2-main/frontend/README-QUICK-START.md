# 🚀 Scorpius Frontend - Quick Start

## Immediate Setup (Windows PowerShell)

**⚡ Just run these 3 commands:**

```powershell
cd frontend
.\setup-windows.ps1
# Follow the prompts - it will automatically install everything and start the server
```

**Alternative (Windows Command Prompt):**

```cmd
cd frontend
setup-windows.bat
```

**Manual Setup:**

```powershell
cd frontend
npm install --legacy-peer-deps
npm run dev
```

## ✅ What You Should See

1. **Development server starts** at `http://localhost:3000`
2. **Login page loads** with animated cyber background (not video - that's normal!)
3. **No red errors** in the console
4. **Smooth animations** and glowing effects
5. **Demo mode works** - you can login with any email/password

## 🎯 Test the Application

### 1. **Login Page** (`http://localhost:3000/login`)

- Animated cyber background ✅
- Login form with glowing effects ✅
- Can login with any credentials (demo mode) ✅

### 2. **Command Center** (`http://localhost:3000/`)

- Real-time metrics cards ✅
- Interactive tabs (Dashboards, Modules, Overview) ✅
- Smooth animations and transitions ✅

### 3. **API Status** (`http://localhost:3000/api/status`)

- Shows health of all backend services ✅
- Real-time connection monitoring ✅
- Troubleshooting information ✅

### 4. **Scanner** (`http://localhost:3000/scanner`)

- Multi-tab interface (Scanner, Honeypot, Wallet, etc.) ✅
- Demo scan functionality ✅
- Progress indicators and results ✅

## 🐛 If Something Looks Wrong

### CSS/Styling Issues

```powershell
# Restart the dev server
npm run dev

# Clear browser cache: Ctrl + Shift + R
```

### Port Issues

```powershell
# If port 3000 is in use
$env:VITE_PORT=3001; npm run dev
```

### Dependency Issues

```powershell
Remove-Item -Recurse -Force node_modules
Remove-Item -Force package-lock.json
npm cache clean --force
npm install --legacy-peer-deps
```

## 🎨 Visual Features You Should See

### ✅ Working Correctly:

- **Cyber-themed dark UI** with cyan/blue accents
- **Glass morphism effects** (transparent backgrounds with blur)
- **Glowing buttons and borders**
- **Smooth hover animations**
- **Particle effects** and animated backgrounds
- **Responsive grid layouts**
- **Real-time data updates** (demo data)

### ❌ Known Differences from Cloud Version:

- **No video on login page** - uses animated background instead (this is intentional)
- **Demo data only** - real backend integration requires backend services
- **Some features may show mock data** - this is expected behavior

## 🔧 Environment Variables

The app automatically creates a `.env` file with these defaults:

```env
VITE_API_BASE_URL=http://localhost:8000    # Backend API (optional)
VITE_WS_BASE_URL=ws://localhost:8000       # WebSocket API (optional)
VITE_GRAFANA_URL=http://localhost:3001     # Grafana URL (optional)
VITE_PORT=3000                             # Dev server port
VITE_DEMO_MODE=true                        # Enables demo mode
```

## 📱 Browser Compatibility

**Recommended**: Chrome, Firefox, Edge (latest versions)

**Features that need modern browser**:

- CSS Grid and Flexbox
- CSS Custom Properties (variables)
- ES2020+ JavaScript features
- WebGL for 3D effects (optional)

## 🚨 Common Issues & Fixes

### "Module not found" errors

```powershell
npm install --force
```

### "Port 3000 in use"

```powershell
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process
```

### Blank white page

- Check browser console (F12) for errors
- Try in incognito/private mode
- Clear browser cache

### Styling looks broken

- Restart dev server (`npm run dev`)
- Hard refresh browser (Ctrl + Shift + R)
- Check if Tailwind CSS is loading

## ✨ Demo Features Working

All these features work without any backend:

- ✅ **Authentication** (demo login)
- ✅ **Dashboard metrics** (mock data)
- ✅ **Vulnerability scanning** (simulated results)
- ✅ **Trading bot interface** (demo bots)
- ✅ **Security monitoring** (mock threats)
- ✅ **Bridge transactions** (simulated transfers)
- ✅ **Analytics charts** (sample data)
- ✅ **Real-time updates** (mock WebSocket data)

## 🎯 Next Steps

1. **Explore the UI** - All pages work in demo mode
2. **Check API Status** - Visit `/api/status` to see backend integration
3. **Test responsiveness** - Resize browser window
4. **Try dark/light themes** - Should be dark by default
5. **Monitor console** - Should be clean (no red errors)

---

**🎉 If you see the login page with the animated cyber background and can navigate through the app smoothly, everything is working perfectly!**

The visual differences from the cloud version are intentional design choices for local development.
