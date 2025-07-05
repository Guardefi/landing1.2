import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    videosFolder: 'artifacts/videos',
    screenshotsFolder: 'artifacts/screenshots',
    supportFile: false,
    specPattern: 'cypress/e2e/**/*.cy.ts',
    excludeSpecPattern: ['**/examples/*']
  }
});
