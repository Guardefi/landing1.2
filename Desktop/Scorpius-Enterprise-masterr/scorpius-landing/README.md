# Scorpius - Cinematic WebGL Landing Page

A high-performance, cinematic WebGL landing page built with React Three Fiber and GSAP scroll animations.

## 🎬 Overview

This project implements a scroll-driven cinematic experience that guides users through the "Dark Forest" of blockchain security, showcasing the Scorpius AI platform through immersive 3D visuals and seamless animations.

## 🚀 Tech Stack

- **React 18** + **TypeScript** - Modern React with full type safety
- **Vite** - Lightning-fast development and build tool
- **Three.js** - 3D graphics library for WebGL
- **React Three Fiber (R3F)** - React renderer for Three.js
- **Drei** - Useful helpers for React Three Fiber
- **GSAP** - Professional-grade animation library with ScrollTrigger
- **Tailwind CSS** - Utility-first CSS framework for UI overlays

## 🎯 Architecture

### Phase 1: Foundation (✅ Complete)
- Scene setup with Dark Forest particle field
- Animated Scorpius Core (central AI sentinel)
- Basic lighting and camera configuration

### Phase 2: Scroll Animation (✅ Complete)
- GSAP timeline controlling camera movements
- ScrollTrigger linking scroll progress to 3D scene
- Smooth transitions between story beats

### Phase 3: UI Integration (✅ Complete)
- HTML overlays synchronized with 3D camera
- Responsive text content with cinematic styling
- Feature module presentations (Hive Alert, Bytecode Engine)

### Phase 4: Polish & Optimization (🔄 Next)
- Custom shaders for enhanced visual effects
- Performance optimization with LOD and instancing
- Audio integration and post-processing effects

## 📁 Project Structure

```
src/
├── components/
│   ├── Scene.tsx          # Main WebGL canvas and scene setup
│   ├── ScorpiusCore.tsx   # Central AI core with animations
│   ├── CameraRig.tsx      # Scroll-driven camera controller
│   └── UIOverlay.tsx      # HTML text overlays
├── index.css              # Tailwind + custom styles
└── App.tsx                # Main app component
```

## 🛠 Development

### Prerequisites
- Node.js 18+
- npm or yarn

### Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Key Features
- **Scroll-driven Animation**: Smooth camera movements tied to scroll position
- **Cinematic UI**: Text overlays that appear/disappear in sync with 3D scene
- **Performance Optimized**: Uses React Three Fiber's efficient rendering
- **Responsive Design**: Adapts to different screen sizes
- **TypeScript**: Full type safety throughout the project

## 🎨 Visual Effects

### Current Implementation
- Particle field representing the "Dark Forest" of transactions
- Animated Scorpius Core with pulsing energy effects
- Smooth camera transitions between story moments
- Glowing UI elements with cyber-themed styling

### Planned Enhancements
- Custom GLSL shaders for enhanced core effects
- Dynamic particle behaviors based on threat levels
- Post-processing effects (bloom, vignette, film grain)
- Audio-reactive animations

## 📱 Browser Compatibility

- Modern browsers with WebGL 2.0 support
- Chrome 60+, Firefox 60+, Safari 12+, Edge 79+
- Responsive design for mobile and desktop

## 🚀 Deployment

This is a standard Vite React project that can be deployed to any static hosting service:

- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront

## 🤝 Contributing

This project follows the technical blueprint for creating a cinematic WebGL experience. Future enhancements should focus on:

1. Visual polish and shader development
2. Performance optimization
3. Audio integration
4. Enhanced interactivity

---

Built with ❤️ for the future of blockchain security
