# ScorpiusCore | Medieval High-Tech Alien War Room

A Fortune 500-worthy cybersecurity platform featuring an immersive 3D interface with real-time threat detection visualization.

![ScorpiusCore](https://img.shields.io/badge/Status-Live-00fff7?style=for-the-badge)
![Next.js](https://img.shields.io/badge/Next.js-14-black?style=for-the-badge&logo=next.js)
![Three.js](https://img.shields.io/badge/Three.js-0.158-white?style=for-the-badge&logo=three.js)

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## ✨ Features

### 🌌 3D Visualization
- **ScorpiusCore**: Living wireframe sphere with advanced GLSL shaders
- **Space Background**: Animated star fields, meteors, and galaxies
- **Energy Layers**: Noise-based organic animations
- **Mouse Interaction**: Reactive sphere responds to cursor movement

### 📱 Interactive UI
- **Scroll-Based Navigation**: Smooth camera movements
- **4 Key Sections**: Core, Detection, Defense, Enterprise
- **Keyboard Controls**: Arrow keys + spacebar navigation
- **Progress Tracking**: Visual scroll indicators

### 🎨 Cyberpunk Design
- **Custom Color Palette**: War room themed with cyan accents
- **Glass Morphism**: Backdrop blur effects
- **Scanning Animations**: Futuristic UI elements
- **Responsive Design**: Works on all devices

## 🛠️ Tech Stack

- **Frontend**: Next.js 14 (App Directory)
- **3D Engine**: React Three Fiber + Drei
- **Animations**: Framer Motion + GSAP
- **Styling**: Tailwind CSS
- **Languages**: TypeScript
- **Shaders**: Custom GLSL

## 🎮 Controls

| Control | Action |
|---------|--------|
| Mouse Move | Interact with energy sphere |
| Scroll | Navigate through sections |
| Arrow Keys | Jump between sections |
| Spacebar | Next section |
| Navigation Dots | Direct section access |

## 📁 Project Structure

```
src/
├── app/
│   ├── layout.tsx      # Root layout with fonts
│   ├── page.tsx        # Main landing page
│   ├── globals.css     # Global styles
│   └── loading.tsx     # Loading component
└── components/
    ├── ScorpiusCore.tsx     # Main 3D scene
    ├── SpaceBackground.tsx  # Animated space
    ├── ScrollUIOverlay.tsx  # Content sections
    ├── AnimatedSection.tsx  # Section animations
    └── useScrollSync.ts     # Scroll state hook
```

## 🎯 Sections

1. **ScorpiusCore** - The quantum defense engine
2. **Quantum Detection** - AI-powered threat recognition
3. **Adaptive Defense** - Multi-chain security layers
4. **Enterprise Command** - Fortune 500 management

## 🔧 Development

```bash
# Development
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Lint code
npm run lint
```

## 🌟 Performance

- **60fps** smooth animations
- **Dynamic loading** for 3D components
- **Optimized shaders** for performance
- **Responsive** across all devices
- **Accessibility** features included

## 🛡️ Security Theme

Perfect for showcasing:
- Cybersecurity platforms
- Blockchain security tools
- Enterprise defense systems
- AI threat detection
- Real-time monitoring dashboards

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🎨 Customization

The project uses custom Tailwind colors:
- `war-room-void`: #0a0a0a
- `cyber-cyan-bright`: #00d4d4
- `cyber-cyan-intense`: #00ffff

## 📄 License

MIT License - Feel free to use for commercial projects!

---

Built with ⚡ by the ScorpiusCore team 