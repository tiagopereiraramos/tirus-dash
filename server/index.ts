#!/usr/bin/env node

/**
 * Sistema RPA BGTELECOM - Redirecionamento para FastAPI
 * Express COMPLETAMENTE REMOVIDO
 * Backend exclusivo: FastAPI (Python)
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

console.log('🚀 Sistema RPA BGTELECOM - Inicialização');
console.log('❌ Express: REMOVIDO');
console.log('✅ Backend: FastAPI (Python)');
console.log('✅ Frontend: Vite + React');
console.log('================================');

// Iniciar Backend FastAPI
console.log('🐍 Iniciando Backend FastAPI na porta 8000...');
const fastapi = spawn('python', ['backend_fastapi_completo.py'], {
  cwd: projectRoot,
  stdio: 'inherit'
});

// Aguardar um pouco e iniciar frontend
setTimeout(() => {
  console.log('⚛️  Iniciando Frontend Vite na porta 3000...');
  const vite = spawn('npx', ['vite', '--host', '0.0.0.0', '--port', '3000'], {
    cwd: join(projectRoot, 'client'),
    stdio: 'inherit'
  });

  // Limpar processos ao sair
  process.on('SIGINT', () => {
    console.log('\n⏹️  Parando sistema...');
    fastapi.kill();
    vite.kill();
    process.exit(0);
  });

  vite.on('close', (code) => {
    if (code !== 0) {
      console.log(`Frontend encerrado com código ${code}`);
    }
  });

}, 3000);

fastapi.on('close', (code) => {
  if (code !== 0) {
    console.log(`Backend FastAPI encerrado com código ${code}`);
  }
});

console.log('\n🎉 Sistema iniciado!');
console.log('📊 Backend FastAPI: http://localhost:8000');
console.log('📖 API Docs: http://localhost:8000/docs');
console.log('🌐 Frontend: http://localhost:3000');