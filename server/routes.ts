import type { Express } from "express";
import { createServer, type Server } from "http";
import { WebSocketServer, WebSocket } from "ws";
import { storage } from "./storage";
import { insertExecucaoSchema, insertFaturaSchema, insertNotificacaoSchema } from "@shared/schema";
import { z } from "zod";

export async function registerRoutes(app: Express): Promise<Server> {
  // Dashboard metrics
  app.get("/api/dashboard/metrics", async (req, res) => {
    try {
      const metrics = await storage.getDashboardMetrics();
      res.json(metrics);
    } catch (error) {
      res.status(500).json({ error: "Erro ao buscar métricas do dashboard" });
    }
  });

  // Execuções
  app.get("/api/execucoes", async (req, res) => {
    try {
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 20;
      const status = req.query.status as string;

      const execucoes = await storage.getExecucoes({ page, limit, status });
      res.json(execucoes);
    } catch (error) {
      res.status(500).json({ error: "Erro ao buscar execuções" });
    }
  });

  app.post("/api/execucoes", async (req, res) => {
    try {
      const data = insertExecucaoSchema.parse(req.body);
      const execucao = await storage.createExecucao(data);
      
      // Broadcast via WebSocket
      broadcastToClients({
        type: "execucao_criada",
        data: execucao
      });

      res.json(execucao);
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({ error: error.errors });
      } else {
        res.status(500).json({ error: "Erro ao criar execução" });
      }
    }
  });

  app.patch("/api/execucoes/:id/status", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const { status, erro, arquivoPath, tempoExecucao } = req.body;

      const execucao = await storage.updateExecucaoStatus(id, {
        status,
        erro,
        arquivoPath,
        tempoExecucao,
        finalizadoEm: status === "concluido" || status === "falha" ? new Date() : undefined
      });

      // Broadcast via WebSocket
      broadcastToClients({
        type: "execucao_atualizada",
        data: execucao
      });

      res.json(execucao);
    } catch (error) {
      res.status(500).json({ error: "Erro ao atualizar status da execução" });
    }
  });

  // Faturas e Aprovações
  app.get("/api/faturas", async (req, res) => {
    try {
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 20;
      const statusAprovacao = req.query.statusAprovacao as string;

      const faturas = await storage.getFaturas({ page, limit, statusAprovacao });
      res.json(faturas);
    } catch (error) {
      res.status(500).json({ error: "Erro ao buscar faturas" });
    }
  });

  app.post("/api/faturas", async (req, res) => {
    try {
      const data = insertFaturaSchema.parse(req.body);
      const fatura = await storage.createFatura(data);

      // Criar notificação de nova fatura
      await storage.createNotificacao({
        tipo: "nova_fatura",
        titulo: "Nova Fatura Disponível",
        mensagem: `Fatura de ${data.valor} aguardando aprovação`,
        dados: { faturaId: fatura.id }
      });

      res.json(fatura);
    } catch (error) {
      if (error instanceof z.ZodError) {
        res.status(400).json({ error: error.errors });
      } else {
        res.status(500).json({ error: "Erro ao criar fatura" });
      }
    }
  });

  app.patch("/api/faturas/:id/aprovar", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const { aprovadoPor } = req.body;

      const fatura = await storage.aprovarFatura(id, aprovadoPor);

      // Broadcast via WebSocket
      broadcastToClients({
        type: "fatura_aprovada",
        data: fatura
      });

      res.json(fatura);
    } catch (error) {
      res.status(500).json({ error: "Erro ao aprovar fatura" });
    }
  });

  app.patch("/api/faturas/:id/rejeitar", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const { motivoRejeicao } = req.body;

      const fatura = await storage.rejeitarFatura(id, motivoRejeicao);

      // Broadcast via WebSocket
      broadcastToClients({
        type: "fatura_rejeitada",
        data: fatura
      });

      res.json(fatura);
    } catch (error) {
      res.status(500).json({ error: "Erro ao rejeitar fatura" });
    }
  });

  // Operadoras
  app.get("/api/operadoras", async (req, res) => {
    try {
      const operadoras = await storage.getOperadoras();
      res.json(operadoras);
    } catch (error) {
      res.status(500).json({ error: "Erro ao buscar operadoras" });
    }
  });

  app.get("/api/operadoras/status", async (req, res) => {
    try {
      const status = await storage.getOperadorasStatus();
      res.json(status);
    } catch (error) {
      res.status(500).json({ error: "Erro ao buscar status das operadoras" });
    }
  });

  // Clientes
  app.get("/api/clientes", async (req, res) => {
    try {
      const page = parseInt(req.query.page as string) || 1;
      const limit = parseInt(req.query.limit as string) || 20;
      const search = req.query.search as string;

      const clientes = await storage.getClientes({ page, limit, search });
      res.json(clientes);
    } catch (error) {
      res.status(500).json({ error: "Erro ao buscar clientes" });
    }
  });

  // Contratos
  app.get("/api/contratos", async (req, res) => {
    try {
      const clienteId = req.query.clienteId ? parseInt(req.query.clienteId as string) : undefined;
      const operadoraId = req.query.operadoraId ? parseInt(req.query.operadoraId as string) : undefined;

      const contratos = await storage.getContratos({ clienteId, operadoraId });
      res.json(contratos);
    } catch (error) {
      res.status(500).json({ error: "Erro ao buscar contratos" });
    }
  });

  // Notificações
  app.get("/api/notificacoes", async (req, res) => {
    try {
      const userId = req.query.userId ? parseInt(req.query.userId as string) : undefined;
      const notificacoes = await storage.getNotificacoes(userId);
      res.json(notificacoes);
    } catch (error) {
      res.status(500).json({ error: "Erro ao buscar notificações" });
    }
  });

  // Inicializar dados do CSV
  app.post('/api/initialize-data', async (req, res) => {
    try {
      await storage.initializeFromCSV();
      res.json({ message: 'Dados inicializados com sucesso' });
    } catch (error) {
      console.error('Error initializing data:', error);
      res.status(500).json({ message: 'Failed to initialize data' });
    }
  });

  app.patch("/api/notificacoes/:id/marcar-lida", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const notificacao = await storage.marcarNotificacaoLida(id);
      res.json(notificacao);
    } catch (error) {
      res.status(500).json({ error: "Erro ao marcar notificação como lida" });
    }
  });

  // Ações rápidas
  app.post("/api/acoes/executar-todos-rpas", async (req, res) => {
    try {
      // Aqui seria integrado com o sistema de filas (Celery/Redis)
      const result = await storage.iniciarExecucaoGeral();

      // Broadcast via WebSocket
      broadcastToClients({
        type: "execucao_geral_iniciada",
        data: result
      });

      res.json({ message: "Execução geral iniciada com sucesso", data: result });
    } catch (error) {
      res.status(500).json({ error: "Erro ao iniciar execução geral" });
    }
  });

  app.post("/api/acoes/executar-rpa", async (req, res) => {
    try {
      const { contratoId } = req.body;
      const result = await storage.iniciarExecucaoRPA(contratoId);

      // Broadcast via WebSocket
      broadcastToClients({
        type: "execucao_rpa_iniciada",
        data: result
      });

      res.json({ message: "Execução RPA iniciada com sucesso", data: result });
    } catch (error) {
      res.status(500).json({ error: "Erro ao iniciar execução RPA" });
    }
  });

  // Relatórios
  app.get("/api/relatorios/execucoes", async (req, res) => {
    try {
      const { dataInicio, dataFim, operadoraId } = req.query;
      const relatorio = await storage.getRelatorioExecucoes({
        dataInicio: dataInicio as string,
        dataFim: dataFim as string,
        operadoraId: operadoraId ? parseInt(operadoraId as string) : undefined
      });
      res.json(relatorio);
    } catch (error) {
      res.status(500).json({ error: "Erro ao gerar relatório de execuções" });
    }
  });

  // Inicializar dados do CSV
  app.post("/api/init/csv-data", async (req, res) => {
    try {
      await storage.initializeFromCSV();
      res.json({ message: "Dados do CSV inicializados com sucesso" });
    } catch (error) {
      res.status(500).json({ error: "Erro ao inicializar dados do CSV" });
    }
  });

  const httpServer = createServer(app);

  // WebSocket setup
  const wss = new WebSocketServer({ server: httpServer, path: '/ws' });
  const clients = new Set<WebSocket>();

  wss.on('connection', (ws: WebSocket) => {
    clients.add(ws);
    console.log('Cliente WebSocket conectado');

    ws.on('close', () => {
      clients.delete(ws);
      console.log('Cliente WebSocket desconectado');
    });

    ws.on('error', (error) => {
      console.error('Erro WebSocket:', error);
      clients.delete(ws);
    });
  });

  // Function to broadcast to all connected clients
  function broadcastToClients(message: any) {
    const messageStr = JSON.stringify(message);
    clients.forEach((client) => {
      if (client.readyState === WebSocket.OPEN) {
        client.send(messageStr);
      }
    });
  }

  // Make broadcast function available globally
  (global as any).broadcastToClients = broadcastToClients;

  return httpServer;
}
