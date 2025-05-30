#!/usr/bin/env node
/**
 * Sistema RPA BGTELECOM - Sistema Simples
 */

import { spawn } from 'child_process';
import path from 'path';

console.log('🚀 SISTEMA RPA BGTELECOM');
console.log('========================');

// Iniciar FastAPI primeiro
const backendProcess = spawn('python', ['-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'], {
  cwd: path.join(process.cwd(), 'backend'),
  stdio: 'pipe'
});

// Log do backend
backendProcess.stdout?.on('data', (data) => {
  console.log(`[BACKEND] ${data.toString().trim()}`);
});

backendProcess.stderr?.on('data', (data) => {
  console.log(`[BACKEND] ${data.toString().trim()}`);
});

// Aguardar 3 segundos e iniciar frontend
setTimeout(() => {
  console.log('🌐 Iniciando frontend...');
  
  const frontendProcess = spawn('npx', ['vite', '--host', '0.0.0.0', '--port', '5000'], {
    cwd: path.join(process.cwd(), 'client'),
    stdio: 'pipe'
  });

  frontendProcess.stdout?.on('data', (data) => {
    console.log(`[FRONTEND] ${data.toString().trim()}`);
  });

  frontendProcess.stderr?.on('data', (data) => {
    console.log(`[FRONTEND] ${data.toString().trim()}`);
  });

}, 3000);