#!/usr/bin/env node
/**
 * Sistema RPA BGTELECOM - Servidor Integrado Frontend + Backend
 */

import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import express from 'express';
import { createProxyMiddleware } from 'http-proxy-middleware';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();

console.log('🚀 SISTEMA RPA BGTELECOM');
console.log('========================');
console.log('Iniciando backend FastAPI...');

// Iniciar backend FastAPI
const backendDir = path.resolve(process.cwd(), 'backend');
const pythonProcess = spawn('python', ['main.py'], {
  cwd: backendDir,
  stdio: 'pipe'
});

// Processar logs do backend
pythonProcess.stdout?.on('data', (data) => {
  process.stdout.write(data);
});

pythonProcess.stderr?.on('data', (data) => {
  process.stderr.write(data);
});

// Aguardar backend inicializar
setTimeout(() => {
  console.log('🌐 Configurando servidor frontend...');
  
  // Proxy para API do FastAPI
  app.use('/api', createProxyMiddleware({
    target: 'http://localhost:8000',
    changeOrigin: true,
    pathRewrite: {
      '^/api': '/api'
    }
  }));

  // Iniciar Vite dev server
  const viteProcess = spawn('npx', ['vite', '--host', '0.0.0.0', '--port', '5173'], {
    cwd: path.join(process.cwd(), 'client'),
    stdio: 'pipe'
  });

  viteProcess.stdout?.on('data', (data) => {
    const output = data.toString();
    if (output.includes('Local:')) {
      console.log('✅ Frontend Vite disponível em: http://localhost:5173');
      console.log('🔗 API backend em: http://localhost:8000');
      console.log('========================');
    }
    process.stdout.write(data);
  });

  viteProcess.stderr?.on('data', (data) => {
    process.stderr.write(data);
  });

  // Proxy para Vite dev server
  app.use('/', createProxyMiddleware({
    target: 'http://localhost:5173',
    changeOrigin: true,
    ws: true
  }));

  const PORT = process.env.PORT || 5000;
  app.listen(PORT, () => {
    console.log('🔗 Proxy servidor ativo em: http://localhost:' + PORT);
  });
}, 3000);

pythonProcess.on('error', (error) => {
  console.error('❌ Erro ao iniciar FastAPI:', error);
  process.exit(1);
});

pythonProcess.on('close', (code) => {
  console.log(`🔴 FastAPI finalizado com código ${code}`);
  process.exit(code || 0);
});

// Finalização limpa
process.on('SIGINT', () => {
  console.log('\n🔴 Finalizando sistema...');
  pythonProcess.kill('SIGINT');
});

process.on('SIGTERM', () => {
  console.log('\n🔴 Finalizando sistema...');
  pythonProcess.kill('SIGTERM');
});