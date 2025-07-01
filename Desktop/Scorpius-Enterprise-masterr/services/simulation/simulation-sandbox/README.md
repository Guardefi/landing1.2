# Node.js Simulation Sandbox

## Overview
This is a secure Node.js execution sandbox for the Scorpius Enterprise simulation service. It provides a controlled environment for executing blockchain simulation code and scenarios.

## Features
- Secure code execution using VM2
- Rate limiting and security middleware  
- Blockchain simulation utilities
- Comprehensive logging
- Health checks and monitoring

## API Endpoints

### Health Check
```
GET /health
```

### Execute Code
```
POST /execute
{
  "code": "return 1 + 1;",
  "context": {},
  "timeout": 5000
}
```

### Run Simulation
```
POST /simulate
{
  "scenario": "return Simulation.calculateReward(1000, 365);",
  "parameters": {},
  "iterations": 10,
  "timeout": 10000
}
```

## Security
- VM2 sandbox isolation
- No access to filesystem or network
- Timeout protection
- Rate limiting
- Input validation

## Development
```bash
npm install
npm run dev
```

## Production
```bash
npm start
```
