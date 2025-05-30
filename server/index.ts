#!/usr/bin/env node
/**
 * Sistema RPA BGTELECOM - Apenas Vite Frontend
 */

import { spawn } from 'child_process';
import path from 'path';

console.log('🚀 SISTEMA RPA BGTELECOM - FRONTEND');
console.log('====================================');

// Iniciar apenas o Vite frontend com proxy para FastAPI
const viteProcess = spawn('npx', ['vite', '--host', '0.0.0.0', '--port', '5000'], {
  cwd: path.join(process.cwd(), 'client'),
  stdio: 'inherit'
});

viteProcess.on('error', (error) => {
  console.error('❌ Erro ao iniciar Vite:', error);
  process.exit(1);
});

viteProcess.on('close', (code) => {
  console.log(`🔴 Vite finalizado com código ${code}`);
  process.exit(code || 0);
});