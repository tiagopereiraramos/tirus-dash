#!/usr/bin/env node
/**
 * Sistema RPA BGTELECOM - Sistema com Proxy
 */

import { spawn } from 'child_process';
import path from 'path';
import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';

console.log('🚀 SISTEMA RPA BGTELECOM');
console.log('========================');

// Criar servidor Express para proxy
const app = express();

// Configurar proxy para API
app.use('/api', createProxyMiddleware({
  target: 'http://localhost:8000',
  changeOrigin: true,
  logLevel: 'debug'
}));

// Servir arquivos estáticos do frontend
app.use(express.static(path.join(process.cwd(), 'client/dist')));

// Fallback para SPA
app.get('*', (req, res) => {
  res.sendFile(path.join(process.cwd(), 'client/dist/index.html'));
});

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

  // Iniciar servidor proxy na porta 3000
  setTimeout(() => {
    app.listen(3000, () => {
      console.log('🔗 Servidor proxy rodando na porta 3000');
    });
  }, 2000);

}, 3000);