import type { Express } from "express";
import { createServer, type Server } from "http";
import { WebSocketServer, WebSocket } from "ws";
import { storage } from "./storage";
import { insertExecucaoSchema, insertFaturaSchema, insertNotificacaoSchema } from "@shared/schema";
import { z } from "zod";
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET || "your-secret-key-here";

// Middleware para verificar autenticação
const authenticateToken = (req: any, res: any, next: any) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    return res.status(401).json({ message: 'Token de acesso requerido' });
  }

  jwt.verify(token, JWT_SECRET, (err: any, user: any) => {
    if (err) {
      return res.status(403).json({ message: 'Token inválido' });
    }
    req.user = user;
    next();
  });
};

export async function registerRoutes(app: Express): Promise<Server> {
  
  // ===== ROTAS COM DADOS REAIS BGTELECOM =====
  
  // Dashboard com dados reais
  app.get("/api/dashboard/metrics", async (req, res) => {
    try {
      const operadoras = await pgClient.query("SELECT COUNT(*) as total FROM operadoras WHERE status_ativo = true");
      const clientes = await pgClient.query("SELECT COUNT(*) as total FROM clientes WHERE status_ativo = true");
      const processos_pendentes = await pgClient.query("SELECT COUNT(*) as total FROM processos WHERE status_processo = 'PENDENTE_APROVACAO'");
      const execucoes_ativas = await pgClient.query("SELECT COUNT(*) as total FROM execucoes WHERE status_execucao = 'EXECUTANDO'");
      
      res.json({
        sucesso: true,
        timestamp: new Date().toISOString(),
        metricas: {
          total_operadoras: parseInt(operadoras.rows[0].total),
          total_clientes: parseInt(clientes.rows[0].total),
          processos_pendentes: parseInt(processos_pendentes.rows[0].total),
          execucoes_ativas: parseInt(execucoes_ativas.rows[0].total)
        }
      });
    } catch (error) {
      console.error('Erro no dashboard:', error);
      res.status(500).json({ erro: "Erro interno do servidor" });
    }
  });

  // Operadoras reais
  app.get("/api/operadoras", async (req, res) => {
    try {
      const result = await pgClient.query(`
        SELECT * FROM operadoras 
        WHERE status_ativo = true 
        ORDER BY nome
      `);
      
      res.json({
        sucesso: true,
        operadoras: result.rows,
        total: result.rows.length
      });
    } catch (error) {
      console.error('Erro ao buscar operadoras:', error);
      res.status(500).json({ erro: "Erro interno do servidor" });
    }
  });

  // Clientes reais da BGTELECOM
  app.get("/api/clientes", async (req, res) => {
    try {
      const { operadora_id, ativo, termo_busca } = req.query;
      
      let query = `
        SELECT 
          c.*,
          o.nome as operadora_nome,
          o.codigo as operadora_codigo
        FROM clientes c
        JOIN operadoras o ON c.operadora_id = o.id
        WHERE 1=1
      `;
      const params: any[] = [];
      
      if (operadora_id) {
        query += ` AND c.operadora_id = $${params.length + 1}`;
        params.push(operadora_id);
      }
      
      if (ativo !== undefined) {
        query += ` AND c.status_ativo = $${params.length + 1}`;
        params.push(ativo);
      }
      
      if (termo_busca) {
        query += ` AND (c.nome_sat ILIKE $${params.length + 1} OR c.razao_social ILIKE $${params.length + 2})`;
        params.push(`%${termo_busca}%`, `%${termo_busca}%`);
      }
      
      query += ` ORDER BY c.nome_sat`;
      
      const result = await pgClient.query(query, params);
      
      res.json({
        sucesso: true,
        clientes: result.rows,
        total: result.rows.length
      });
    } catch (error) {
      console.error('Erro ao buscar clientes:', error);
      res.status(500).json({ erro: "Erro interno do servidor" });
    }
  });

  // Faturas/Processos com dados reais
  app.get("/api/faturas", async (req, res) => {
    try {
      const { statusAprovacao, operadora_id, mes_ano } = req.query;
      
      let query = `
        SELECT 
          p.*,
          c.nome_sat,
          c.razao_social,
          o.nome as operadora_nome,
          o.codigo as operadora_codigo
        FROM processos p
        JOIN clientes c ON p.cliente_id = c.id
        JOIN operadoras o ON c.operadora_id = o.id
        WHERE 1=1
      `;
      const params: any[] = [];
      
      if (statusAprovacao === 'pendente') {
        query += ` AND p.status_processo = 'PENDENTE_APROVACAO'`;
      } else if (statusAprovacao === 'aprovada') {
        query += ` AND p.status_processo = 'APROVADA'`;
      }
      
      if (operadora_id) {
        query += ` AND o.id = $${params.length + 1}`;
        params.push(operadora_id);
      }
      
      if (mes_ano) {
        query += ` AND p.mes_ano = $${params.length + 1}`;
        params.push(mes_ano);
      }
      
      query += ` ORDER BY p.created_at DESC`;
      
      const result = await pgClient.query(query, params);
      
      res.json({
        sucesso: true,
        data: result.rows,
        total: result.rows.length
      });
    } catch (error) {
      console.error('Erro ao buscar faturas:', error);
      res.status(500).json({ erro: "Erro interno do servidor" });
    }
  });

  // Aprovar fatura real
  app.patch("/api/faturas/:faturaId/aprovar", async (req, res) => {
    try {
      const { faturaId } = req.params;
      const { aprovadoPor, observacoes } = req.body;
      
      const result = await pgClient.query(`
        UPDATE processos 
        SET status_processo = 'APROVADA',
            data_aprovacao = NOW(),
            aprovado_por = $1,
            observacoes = COALESCE($2, observacoes)
        WHERE id = $3
        RETURNING *
      `, [aprovadoPor, observacoes, faturaId]);
      
      if (result.rows.length > 0) {
        res.json({
          sucesso: true,
          mensagem: "Processo aprovado com sucesso",
          processo: result.rows[0]
        });
      } else {
        res.status(404).json({ erro: "Processo não encontrado" });
      }
    } catch (error) {
      console.error('Erro ao aprovar fatura:', error);
      res.status(500).json({ erro: "Erro interno do servidor" });
    }
  });

  // Rejeitar fatura real
  app.patch("/api/faturas/:faturaId/rejeitar", async (req, res) => {
    try {
      const { faturaId } = req.params;
      const { motivoRejeicao } = req.body;
      
      const result = await pgClient.query(`
        UPDATE processos 
        SET status_processo = 'REJEITADA',
            data_rejeicao = NOW(),
            motivo_rejeicao = $1
        WHERE id = $2
        RETURNING *
      `, [motivoRejeicao, faturaId]);
      
      if (result.rows.length > 0) {
        res.json({
          sucesso: true,
          mensagem: "Processo rejeitado com sucesso",
          processo: result.rows[0]
        });
      } else {
        res.status(404).json({ erro: "Processo não encontrado" });
      }
    } catch (error) {
      console.error('Erro ao rejeitar fatura:', error);
      res.status(500).json({ erro: "Erro interno do servidor" });
    }
  });

  // Execuções reais
  app.get("/api/execucoes", async (req, res) => {
    try {
      const { status, operadora } = req.query;
      
      let query = `
        SELECT 
          e.*,
          p.mes_ano,
          c.nome_sat,
          o.nome as operadora_nome,
          o.codigo as operadora_codigo
        FROM execucoes e
        JOIN processos p ON e.processo_id = p.id
        JOIN clientes c ON p.cliente_id = c.id
        JOIN operadoras o ON c.operadora_id = o.id
        WHERE 1=1
      `;
      const params: any[] = [];
      
      if (status) {
        query += ` AND e.status_execucao = $${params.length + 1}`;
        params.push(status);
      }
      
      if (operadora) {
        query += ` AND o.codigo = $${params.length + 1}`;
        params.push(operadora);
      }
      
      query += ` ORDER BY e.created_at DESC`;
      
      const result = await pgClient.query(query, params);
      
      res.json({
        sucesso: true,
        data: result.rows,
        total: result.rows.length
      });
    } catch (error) {
      console.error('Erro ao buscar execuções:', error);
      res.status(500).json({ erro: "Erro interno do servidor" });
    }
  });

  // Execuções ativas
  app.get("/api/execucoes/ativas", async (req, res) => {
    try {
      const result = await pgClient.query(`
        SELECT 
          e.*,
          p.mes_ano,
          c.nome_sat,
          o.nome as operadora_nome,
          o.codigo as operadora_codigo
        FROM execucoes e
        JOIN processos p ON e.processo_id = p.id
        JOIN clientes c ON p.cliente_id = c.id
        JOIN operadoras o ON c.operadora_id = o.id
        WHERE e.status_execucao = 'EXECUTANDO'
        ORDER BY e.data_inicio DESC
      `);
      
      res.json({
        sucesso: true,
        execucoes_ativas: result.rows,
        total: result.rows.length
      });
    } catch (error) {
      console.error('Erro ao buscar execuções ativas:', error);
      res.status(500).json({ erro: "Erro interno do servidor" });
    }
  });

  // Cancelar execução
  app.post("/api/execucoes/:execucaoId/cancel", async (req, res) => {
    try {
      const { execucaoId } = req.params;
      
      const result = await pgClient.query(`
        UPDATE execucoes 
        SET status_execucao = 'CANCELADO',
            data_fim = NOW(),
            erro_detalhes = 'Cancelado pelo usuário'
        WHERE id = $1 AND status_execucao = 'EXECUTANDO'
        RETURNING *
      `, [execucaoId]);
      
      if (result.rows.length > 0) {
        res.json({
          sucesso: true,
          mensagem: "Execução cancelada com sucesso",
          execucao: result.rows[0]
        });
      } else {
        res.status(404).json({ erro: "Execução não encontrada ou não está em execução" });
      }
    } catch (error) {
      console.error('Erro ao cancelar execução:', error);
      res.status(500).json({ erro: "Erro interno do servidor" });
    }
  });

  // Status dos RPAs
  app.get("/api/rpa/status", async (req, res) => {
    try {
      const result = await pgClient.query(`
        SELECT 
          o.id,
          o.nome,
          o.codigo,
          o.possui_rpa,
          COUNT(e.id) as execucoes_ativas
        FROM operadoras o
        LEFT JOIN clientes c ON c.operadora_id = o.id
        LEFT JOIN processos p ON p.cliente_id = c.id
        LEFT JOIN execucoes e ON e.processo_id = p.id AND e.status_execucao = 'EXECUTANDO'
        WHERE o.status_ativo = true
        GROUP BY o.id, o.nome, o.codigo, o.possui_rpa
        ORDER BY o.nome
      `);
      
      const status_por_operadora: any = {};
      result.rows.forEach((op: any) => {
        status_por_operadora[op.codigo] = {
          operadora: op.nome,
          codigo: op.codigo,
          possui_rpa: op.possui_rpa,
          execucoes_ativas: parseInt(op.execucoes_ativas),
          disponivel: op.possui_rpa && parseInt(op.execucoes_ativas) === 0
        };
      });
      
      res.json({
        status: "success",
        operadoras: status_por_operadora,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error('Erro ao obter status dos RPAs:', error);
      res.status(500).json({ erro: "Erro interno do servidor" });
    }
  });

  // Notificações baseadas em alertas do sistema
  app.get("/api/notificacoes", async (req, res) => {
    try {
      const alertas = await pgClient.query(`
        SELECT 
          'PROCESSOS_PENDENTES' as tipo,
          'Faturas Pendentes' as titulo,
          CONCAT(COUNT(*), ' faturas aguardando aprovação') as descricao,
          NOW() as data
        FROM processos 
        WHERE status_processo = 'PENDENTE_APROVACAO'
        
        UNION ALL
        
        SELECT 
          'EXECUCOES_ATIVAS' as tipo,
          'RPAs em Execução' as titulo,
          CONCAT(COUNT(*), ' execuções RPA ativas') as descricao,
          NOW() as data
        FROM execucoes 
        WHERE status_execucao = 'EXECUTANDO'
      `);
      
      const notificacoes = alertas.rows.map((alerta: any, index: number) => ({
        id: `alert_${index}`,
        tipo: alerta.tipo,
        titulo: alerta.titulo,
        mensagem: alerta.descricao,
        data: alerta.data,
        lida: false
      }));
      
      res.json(notificacoes);
    } catch (error) {
      console.error('Erro ao buscar notificações:', error);
      res.status(500).json({ erro: "Erro interno do servidor" });
    }
  });

  // ===== ROTAS DE AUTENTICAÇÃO EXISTENTES =====
  
  app.post("/api/auth/register", async (req, res) => {
    try {
      const { username, email, password } = req.body;

      if (!username || !email || !password) {
        return res.status(400).json({ message: "Todos os campos são obrigatórios" });
      }

      // Verifica se usuário já existe
      const existingUser = await storage.getUserByUsername(username);
      if (existingUser) {
        return res.status(400).json({ message: "Usuário já existe" });
      }

      // Hash da senha
      const saltRounds = 10;
      const hashedPassword = await bcrypt.hash(password, saltRounds);

      // Cria o usuário
      const newUser = await storage.createUser({
        username,
        email,
        password: hashedPassword
      });

      res.status(201).json({ 
        message: "Usuário criado com sucesso",
        user: { id: newUser.id, username: newUser.username, email: newUser.email }
      });
    } catch (error) {
      console.error("Erro no cadastro:", error);
      res.status(500).json({ message: "Erro interno do servidor" });
    }
  });

  app.post("/api/auth/login", async (req, res) => {
    try {
      const { username, password } = req.body;

      if (!username || !password) {
        return res.status(400).json({ message: "Usuário e senha são obrigatórios" });
      }

      // Busca o usuário
      const user = await storage.getUserByUsername(username);
      if (!user) {
        return res.status(401).json({ message: "Credenciais inválidas" });
      }

      // Verifica a senha
      const isValidPassword = await bcrypt.compare(password, user.password);
      if (!isValidPassword) {
        return res.status(401).json({ message: "Credenciais inválidas" });
      }

      // Gera o token JWT
      const token = jwt.sign(
        { id: user.id, username: user.username },
        JWT_SECRET,
        { expiresIn: '24h' }
      );

      res.json({
        message: "Login realizado com sucesso",
        token,
        user: { id: user.id, username: user.username, email: user.email }
      });
    } catch (error) {
      console.error("Erro no login:", error);
      res.status(500).json({ message: "Erro interno do servidor" });
    }
  });

  app.get("/api/auth/me", authenticateToken, async (req: any, res) => {
    try {
      const user = await storage.getUser(req.user.id);
      if (!user) {
        return res.status(404).json({ message: "Usuário não encontrado" });
      }

      res.json({ id: user.id, username: user.username, email: user.email });
    } catch (error) {
      console.error("Erro ao buscar usuário:", error);
      res.status(500).json({ message: "Erro interno do servidor" });
    }
  });

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
