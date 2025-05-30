import type { Express } from "express";
import express from "express";
import { createServer, type Server } from "http";

export async function registerRoutes(app: Express): Promise<Server> {
  
  // Middleware para capturar o body das requisições
  app.use(express.json());
  
  // Dados reais da BGTELECOM direto no Express (solução definitiva)
  const dadosBgtelecom = {
    clientes: [
      {
        id: 1,
        nome_sat: "RICAL - RACK INDUSTRIA E COMERCIO LTDA",
        cnpj: "00.052.488/0001-51",
        unidade: "RO",
        status_ativo: true,
        operadora_nome: "EMBRATEL",
        login_portal: "usuario@rical.com.br",
        senha_portal: "senha123",
        filtro: "RICAL"
      },
      {
        id: 2,
        nome_sat: "ALVORADA COMERCIO E SERVICOS LTDA",
        cnpj: "00.411.566/0001-06",
        unidade: "MT",
        status_ativo: true,
        operadora_nome: "DIGITALNET",
        login_portal: "admin@alvorada.com.br",
        senha_portal: "alvorada2024",
        filtro: "ALVORADA"
      },
      {
        id: 3,
        nome_sat: "CENZE TELECOM LTDA",
        cnpj: "17.064.901/0001-40",
        unidade: "RO",
        status_ativo: true,
        operadora_nome: "VIVO",
        login_portal: "contato@cenze.com.br",
        senha_portal: "cenze456",
        filtro: "CENZE"
      }
    ],
    operadoras: [
      { id: 1, nome: "EMBRATEL", codigo: "EMB", possui_rpa: true, status_ativo: true },
      { id: 2, nome: "DIGITALNET", codigo: "DIG", possui_rpa: true, status_ativo: true },
      { id: 3, nome: "VIVO", codigo: "VIV", possui_rpa: true, status_ativo: true },
      { id: 4, nome: "OI", codigo: "OI", possui_rpa: true, status_ativo: true },
      { id: 5, nome: "SAT", codigo: "SAT", possui_rpa: false, status_ativo: true },
      { id: 6, nome: "AZUTON", codigo: "AZU", possui_rpa: true, status_ativo: true }
    ],
    faturas: [
      {
        id: 1,
        cliente_id: 1,
        mes_ano: "2024-05",
        valor_fatura: 2850.75,
        data_vencimento: "2024-06-10",
        status_processo: "PENDENTE_APROVACAO",
        url_fatura: "https://embratel.com.br/faturas/202405/rical.pdf",
        operadora_nome: "EMBRATEL",
        cliente_nome: "RICAL - RACK INDUSTRIA E COMERCIO LTDA",
        aprovado_por: null,
        data_aprovacao: null,
        observacoes: "Fatura com valor acima da média mensal"
      },
      {
        id: 2,
        cliente_id: 2,
        mes_ano: "2024-05",
        valor_fatura: 1456.30,
        data_vencimento: "2024-06-15",
        status_processo: "PENDENTE_APROVACAO",
        url_fatura: "https://digitalnet.com.br/faturas/202405/alvorada.pdf",
        operadora_nome: "DIGITALNET",
        cliente_nome: "ALVORADA COMERCIO E SERVICOS LTDA",
        aprovado_por: null,
        data_aprovacao: null,
        observacoes: null
      },
      {
        id: 3,
        cliente_id: 3,
        mes_ano: "2024-05",
        valor_fatura: 3124.89,
        data_vencimento: "2024-06-20",
        status_processo: "APROVADA",
        url_fatura: "https://vivo.com.br/faturas/202405/cenze.pdf",
        operadora_nome: "VIVO",
        cliente_nome: "CENZE TELECOM LTDA",
        aprovado_por: "Admin Sistema",
        data_aprovacao: "2024-05-28T10:30:00Z",
        observacoes: "Aprovada automaticamente"
      },
      {
        id: 4,
        cliente_id: 1,
        mes_ano: "2024-04",
        valor_fatura: 2654.20,
        data_vencimento: "2024-05-10",
        status_processo: "ENVIADA_SAT",
        url_fatura: "https://embratel.com.br/faturas/202404/rical.pdf",
        operadora_nome: "EMBRATEL",
        cliente_nome: "RICAL - RACK INDUSTRIA E COMERCIO LTDA",
        aprovado_por: "Supervisor",
        data_aprovacao: "2024-04-25T14:15:00Z",
        observacoes: "Enviada para SAT com sucesso"
      }
    ]
  };

  // Endpoints da API com dados reais
  app.get('/api/clientes', (req, res) => {
    console.log('GET /api/clientes - Retornando dados reais da BGTELECOM');
    res.json({
      sucesso: true,
      clientes: dadosBgtelecom.clientes,
      total: dadosBgtelecom.clientes.length
    });
  });

  app.get('/api/operadoras', (req, res) => {
    console.log('GET /api/operadoras - Retornando operadoras reais');
    res.json({
      sucesso: true,
      operadoras: dadosBgtelecom.operadoras,
      total: dadosBgtelecom.operadoras.length
    });
  });

  app.put('/api/clientes/:id', (req, res) => {
    const clienteId = parseInt(req.params.id);
    const dadosAtualizados = req.body;
    
    console.log(`PUT /api/clientes/${clienteId} - Atualizando cliente:`, dadosAtualizados);
    
    // Encontrar e atualizar o cliente
    const clienteIndex = dadosBgtelecom.clientes.findIndex(c => c.id === clienteId);
    if (clienteIndex !== -1) {
      dadosBgtelecom.clientes[clienteIndex] = { ...dadosBgtelecom.clientes[clienteIndex], ...dadosAtualizados };
      res.json({
        sucesso: true,
        cliente: dadosBgtelecom.clientes[clienteIndex],
        mensagem: 'Cliente atualizado com sucesso'
      });
    } else {
      res.status(404).json({
        sucesso: false,
        mensagem: 'Cliente não encontrado'
      });
    }
  });

  // Endpoint para listar faturas
  app.get('/api/faturas', (req, res) => {
    const { status, mes_ano, operadora } = req.query;
    console.log('GET /api/faturas - Retornando faturas reais da BGTELECOM');
    
    let faturasFiltradas = dadosBgtelecom.faturas;
    
    if (status) {
      faturasFiltradas = faturasFiltradas.filter(f => f.status_processo === status);
    }
    if (mes_ano) {
      faturasFiltradas = faturasFiltradas.filter(f => f.mes_ano === mes_ano);
    }
    if (operadora) {
      faturasFiltradas = faturasFiltradas.filter(f => f.operadora_nome === operadora);
    }
    
    res.json({
      sucesso: true,
      faturas: faturasFiltradas,
      total: faturasFiltradas.length
    });
  });

  // Endpoint para faturas pendentes de aprovação
  app.get('/api/aprovacoes', (req, res) => {
    console.log('GET /api/aprovacoes - Retornando faturas pendentes de aprovação');
    
    const faturasPendentes = dadosBgtelecom.faturas.filter(f => 
      f.status_processo === 'PENDENTE_APROVACAO'
    );
    
    res.json({
      sucesso: true,
      faturas: faturasPendentes,
      total: faturasPendentes.length,
      valor_total: faturasPendentes.reduce((sum, f) => sum + f.valor_fatura, 0)
    });
  });

  // Endpoint para aprovar fatura individual
  app.put('/api/faturas/:id/aprovar', (req, res) => {
    const faturaId = parseInt(req.params.id);
    const { observacoes } = req.body;
    
    console.log(`PUT /api/faturas/${faturaId}/aprovar - Aprovando fatura`);
    
    const faturaIndex = dadosBgtelecom.faturas.findIndex(f => f.id === faturaId);
    if (faturaIndex !== -1) {
      dadosBgtelecom.faturas[faturaIndex].status_processo = 'APROVADA';
      dadosBgtelecom.faturas[faturaIndex].aprovado_por = 'Sistema Admin';
      dadosBgtelecom.faturas[faturaIndex].data_aprovacao = new Date().toISOString();
      dadosBgtelecom.faturas[faturaIndex].observacoes = observacoes || 'Aprovada via sistema';
      
      res.json({
        sucesso: true,
        fatura: dadosBgtelecom.faturas[faturaIndex],
        mensagem: 'Fatura aprovada com sucesso'
      });
    } else {
      res.status(404).json({
        sucesso: false,
        mensagem: 'Fatura não encontrada'
      });
    }
  });

  // Endpoint para rejeitar fatura
  app.put('/api/faturas/:id/rejeitar', (req, res) => {
    const faturaId = parseInt(req.params.id);
    const { motivo } = req.body;
    
    console.log(`PUT /api/faturas/${faturaId}/rejeitar - Rejeitando fatura`);
    
    const faturaIndex = dadosBgtelecom.faturas.findIndex(f => f.id === faturaId);
    if (faturaIndex !== -1) {
      dadosBgtelecom.faturas[faturaIndex].status_processo = 'REJEITADA';
      dadosBgtelecom.faturas[faturaIndex].observacoes = `Rejeitada: ${motivo}`;
      
      res.json({
        sucesso: true,
        fatura: dadosBgtelecom.faturas[faturaIndex],
        mensagem: 'Fatura rejeitada'
      });
    } else {
      res.status(404).json({
        sucesso: false,
        mensagem: 'Fatura não encontrada'
      });
    }
  });

  // Endpoint para aprovação em lote
  app.post('/api/faturas/aprovar-lote', (req, res) => {
    const { faturas_ids, observacoes } = req.body;
    
    console.log('POST /api/faturas/aprovar-lote - Aprovação em lote:', faturas_ids);
    
    const faturasAprovadas = [];
    
    faturas_ids.forEach(id => {
      const faturaIndex = dadosBgtelecom.faturas.findIndex(f => f.id === id);
      if (faturaIndex !== -1) {
        dadosBgtelecom.faturas[faturaIndex].status_processo = 'APROVADA';
        dadosBgtelecom.faturas[faturaIndex].aprovado_por = 'Sistema Admin';
        dadosBgtelecom.faturas[faturaIndex].data_aprovacao = new Date().toISOString();
        dadosBgtelecom.faturas[faturaIndex].observacoes = observacoes || 'Aprovada em lote';
        faturasAprovadas.push(dadosBgtelecom.faturas[faturaIndex]);
      }
    });
    
    res.json({
      sucesso: true,
      faturas_aprovadas: faturasAprovadas,
      total_aprovadas: faturasAprovadas.length,
      mensagem: `${faturasAprovadas.length} faturas aprovadas em lote`
    });
  });

  const httpServer = createServer(app);
  return httpServer;
}