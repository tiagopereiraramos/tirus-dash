import { spawn } from 'child_process';

// Conecta diretamente com os dados reais da BGTELECOM no PostgreSQL
export class RealDataConnector {
  
  static async executePythonService(script: string): Promise<any> {
    return new Promise((resolve, reject) => {
      const python = spawn('python', ['-c', script], { cwd: process.cwd() });
      
      let output = '';
      let errorOutput = '';
      
      python.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      python.stderr.on('data', (data) => {
        errorOutput += data.toString();
      });
      
      python.on('close', (code) => {
        try {
          if (output.trim()) {
            const result = JSON.parse(output.trim());
            resolve(result);
          } else {
            reject(new Error(errorOutput || 'No output from Python service'));
          }
        } catch (error) {
          reject(new Error(`JSON parse error: ${error.message}`));
        }
      });
    });
  }

  static async getDashboardMetrics() {
    const script = `
import sys
sys.path.append('./backend')
from database_postgresql import DashboardService
import json
try:
    result = DashboardService.obter_metricas_dashboard()
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;
    return this.executePythonService(script);
  }

  static async getFaturas(status?: string, operadoraId?: string) {
    const script = `
import sys
sys.path.append('./backend')
from database_postgresql import ProcessoService
import json
try:
    result = ProcessoService.listar_processos(0, 100, "${operadoraId || ''}", "${status || ''}")
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;
    return this.executePythonService(script);
  }

  static async getExecucoes(status?: string) {
    const script = `
import sys
sys.path.append('./backend')
from database_postgresql import ExecucaoService
import json
try:
    result = ExecucaoService.listar_execucoes_completas(0, 100, "${status || ''}")
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;
    return this.executePythonService(script);
  }

  static async getOperadoras() {
    const script = `
import sys
sys.path.append('./backend')
from database_postgresql import OperadoraService
import json
try:
    result = OperadoraService.listar_operadoras(True, True)
    print(json.dumps({"operadoras": result}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;
    return this.executePythonService(script);
  }

  static async getClientes() {
    const script = `
import sys
sys.path.append('./backend')
from database_postgresql import ClienteService
import json
try:
    result = ClienteService.listar_clientes(None, True, '')
    print(json.dumps({"clientes": result}))
except Exception as e:
    print(json.dumps({"error": str(e)}))
`;
    return this.executePythonService(script);
  }
}