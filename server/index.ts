#!/usr/bin/env node
/**
 * Sistema RPA BGTELECOM - Proxy para iniciar FastAPI
 * Este arquivo substitui o servidor Express removido
 */

import { spawn } from 'child_process';
import path from 'path';

console.log('🚀 SISTEMA RPA BGTELECOM');
console.log('========================');
console.log('Iniciando backend FastAPI...');

const backendDir = path.resolve(process.cwd(), 'backend');
const pythonProcess = spawn('python', ['main.py'], {
  cwd: backendDir,
  stdio: 'inherit'
});

pythonProcess.on('error', (error) => {
  console.error('❌ Erro ao iniciar FastAPI:', error);
  process.exit(1);
});

pythonProcess.on('close', (code) => {
  console.log(`🔴 FastAPI finalizado com código ${code}`);
  process.exit(code || 0);
});

// Capturar sinais para finalização limpa
process.on('SIGINT', () => {
  console.log('\n🔴 Finalizando sistema...');
  pythonProcess.kill('SIGINT');
});

process.on('SIGTERM', () => {
  console.log('\n🔴 Finalizando sistema...');
  pythonProcess.kill('SIGTERM');
});