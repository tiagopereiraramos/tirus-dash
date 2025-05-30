// Teste completo de todos os endpoints
const BASE_URL = 'http://localhost:5000';

const endpoints = [
  '/api/dashboard/metrics',
  '/api/operadoras', 
  '/api/clientes',
  '/api/execucoes',
  '/api/notificacoes',
  '/api/faturas',
  '/api/aprovacoes', 
  '/api/contratos',
  '/api/rpa/status'
];

async function testAllEndpoints() {
  console.log('=== TESTE DE COBERTURA COMPLETO - TODOS OS ENDPOINTS ===\n');
  
  for (const endpoint of endpoints) {
    try {
      console.log(`\n${endpoint}:`);
      console.log('='.repeat(endpoint.length + 1));
      
      const response = await fetch(`${BASE_URL}${endpoint}`);
      const data = await response.json();
      
      console.log('Status:', response.status);
      console.log('Response:', JSON.stringify(data, null, 2));
      
    } catch (error) {
      console.log(`ERRO em ${endpoint}:`, error.message);
    }
  }
}

// Executar se for Node.js
if (typeof module !== 'undefined' && module.exports) {
  testAllEndpoints();
}