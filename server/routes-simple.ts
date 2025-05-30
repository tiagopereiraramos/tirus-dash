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

  const httpServer = createServer(app);
  return httpServer;
}