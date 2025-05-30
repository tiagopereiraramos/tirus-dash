#!/bin/bash

# Sistema RPA BGTELECOM - Inicialização Exclusiva FastAPI
# Backend: FastAPI (Python) - Porta 8000
# Frontend: Vite (React) - Porta 3000
# Express: COMPLETAMENTE REMOVIDO

echo "🚀 Iniciando Sistema RPA BGTELECOM"
echo "✅ Backend: FastAPI (Python)"
echo "✅ Frontend: Vite + React"
echo "❌ Express: REMOVIDO"
echo "================================"

# Matar processos existentes nas portas
echo "🧹 Limpando portas..."
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

# Iniciar backend FastAPI
echo "🐍 Iniciando Backend FastAPI na porta 8000..."
python backend_fastapi_completo.py &
FASTAPI_PID=$!

# Aguardar backend inicializar
sleep 5

# Verificar se backend está rodando
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend FastAPI funcionando"
else
    echo "❌ Erro no Backend FastAPI"
    exit 1
fi

# Iniciar frontend Vite
echo "⚛️  Iniciando Frontend Vite na porta 3000..."
cd client && npx vite --host 0.0.0.0 --port 3000 &
VITE_PID=$!

echo ""
echo "🎉 Sistema iniciado com sucesso!"
echo "📊 Backend FastAPI: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🌐 Frontend: http://localhost:3000"
echo ""
echo "⏹️  Pressione Ctrl+C para parar"

# Função para limpar ao sair
cleanup() {
    echo ""
    echo "⏹️  Parando sistema..."
    kill $FASTAPI_PID 2>/dev/null || true
    kill $VITE_PID 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    echo "✅ Sistema parado"
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT SIGTERM

# Aguardar indefinidamente
wait