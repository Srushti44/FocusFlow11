import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { copyFileSync, mkdirSync, existsSync, readFileSync, writeFileSync } from 'fs';

// Vite configuration for building the Chrome Extension
// This builds the popup and sidepanel HTML files and copies static extension assets
export default defineConfig({
  plugins: [
    react(),
    {
      name: 'copy-extension-files',
      closeBundle() {
        const outDir = 'dist-extension';
        
        // Ensure output directory exists
        if (!existsSync(outDir)) {
          mkdirSync(outDir, { recursive: true });
        }

        // Copy static extension files
        const filesToCopy = [
          { src: 'extension/manifest.json', dest: `${outDir}/manifest.json` },
          { src: 'extension/background.js', dest: `${outDir}/background.js` },
          { src: 'extension/content.js', dest: `${outDir}/content.js` },
          { src: 'extension/popup.js', dest: `${outDir}/extension/popup.js` },
          { src: 'extension/readability.js', dest: `${outDir}/readability.js` },
        ];

        filesToCopy.forEach(({ src, dest }) => {
          try {
            copyFileSync(src, dest);
            console.log(`✓ Copied ${src} → ${dest}`);
          } catch (err) {
            console.error(`✗ Failed to copy ${src}:`, err);
          }
        });

        // Copy icons directory
        const iconsDir = `${outDir}/icons`;
        if (!existsSync(iconsDir)) {
          mkdirSync(iconsDir, { recursive: true });
        }

        const iconFiles = [
          'extension/icons/icon16.png',
          'extension/icons/icon32.png',
          'extension/icons/icon48.png',
          'extension/icons/icon128.png',
        ];

        iconFiles.forEach((src) => {
          try {
            const filename = src.split('/').pop();
            copyFileSync(src, `${iconsDir}/${filename}`);
            console.log(`✓ Copied ${src} → ${iconsDir}/${filename}`);
          } catch (err) {
            console.error(`✗ Failed to copy ${src}:`, err);
          }
        });

        // Fix manifest.json paths after build
        const manifestPath = `${outDir}/manifest.json`;
        try {
          const manifest = JSON.parse(readFileSync(manifestPath, 'utf-8'));
          manifest.action.default_popup = 'extension/popup.html';
          manifest.side_panel.default_path = 'extension/sidepanel.html';
          writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
          console.log('✓ Fixed manifest.json paths');
        } catch (err) {
          console.error('✗ Failed to fix manifest:', err);
        }

        console.log('\n✅ Extension build complete! Load dist-extension/ in Chrome at chrome://extensions\n');
      },
    },
  ],
  resolve: {
    preserveSymlinks: true,
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
  build: {
    outDir: 'dist-extension',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'extension/popup.html'),
        sidepanel: resolve(__dirname, 'extension/sidepanel.html'),
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]',
      },
    },
  },
});
