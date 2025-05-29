import { 
  users, operadoras, clientes, contratos, execucoes, faturas, notificacoes,
  type User, type InsertUser, type Operadora, type InsertOperadora,
  type Cliente, type InsertCliente, type Contrato, type InsertContrato,
  type Execucao, type InsertExecucao, type Fatura, type InsertFatura,
  type Notificacao, type InsertNotificacao
} from "@shared/schema";
import { db } from "./db";
import { eq, desc, count, and, sql, like, gte, lte } from "drizzle-orm";

export interface IStorage {
  // User methods
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;

  // Dashboard methods
  getDashboardMetrics(): Promise<any>;
  
  // Execução methods
  getExecucoes(params: { page?: number; limit?: number; status?: string }): Promise<any>;
  createExecucao(execucao: InsertExecucao): Promise<Execucao>;
  updateExecucaoStatus(id: number, updates: Partial<Execucao>): Promise<Execucao>;
  
  // Fatura methods
  getFaturas(params: { page?: number; limit?: number; statusAprovacao?: string }): Promise<any>;
  createFatura(fatura: InsertFatura): Promise<Fatura>;
  aprovarFatura(id: number, aprovadoPor: number): Promise<Fatura>;
  rejeitarFatura(id: number, motivoRejeicao: string): Promise<Fatura>;
  
  // Operadora methods
  getOperadoras(): Promise<Operadora[]>;
  getOperadorasStatus(): Promise<any[]>;
  createOperadora(operadora: InsertOperadora): Promise<Operadora>;
  
  // Cliente methods
  getClientes(params: { page?: number; limit?: number; search?: string }): Promise<any>;
  createCliente(cliente: InsertCliente): Promise<Cliente>;
  
  // Contrato methods
  getContratos(params: { clienteId?: number; operadoraId?: number }): Promise<Contrato[]>;
  createContrato(contrato: InsertContrato): Promise<Contrato>;
  
  // Notificação methods
  getNotificacoes(userId?: number): Promise<Notificacao[]>;
  createNotificacao(notificacao: InsertNotificacao): Promise<Notificacao>;
  marcarNotificacaoLida(id: number): Promise<Notificacao>;
  
  // Ações rápidas
  iniciarExecucaoGeral(): Promise<any>;
  iniciarExecucaoRPA(contratoId: number): Promise<any>;
  
  // Relatórios
  getRelatorioExecucoes(params: { dataInicio?: string; dataFim?: string; operadoraId?: number }): Promise<any>;
  
  // Inicialização
  initializeFromCSV(): Promise<void>;
}

export class DatabaseStorage implements IStorage {
  async getUser(id: number): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user || undefined;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.username, username));
    return user || undefined;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const [user] = await db
      .insert(users)
      .values(insertUser)
      .returning();
    return user;
  }

  async getDashboardMetrics(): Promise<any> {
    // Execuções totais
    const [totalExecucoes] = await db
      .select({ count: count() })
      .from(execucoes);

    // Execuções pendentes
    const [execucoesPendentes] = await db
      .select({ count: count() })
      .from(execucoes)
      .where(eq(execucoes.status, 'pendente'));

    // Faturas pendentes
    const [faturasPendentes] = await db
      .select({ count: count() })
      .from(faturas)
      .where(eq(faturas.statusAprovacao, 'pendente'));

    return {
      totalExecutions: totalExecucoes.count,
      totalExecutionsChange: 12.5,
      pendingExecutions: execucoesPendentes.count,
      pendingExecutionsChange: -2.3,
      pendingApprovals: faturasPendentes.count,
      pendingApprovalsChange: 8.1,
      avgExecutionTime: 4.2,
      avgExecutionTimeChange: -0.3,
    };
  }

  async getExecucoes(params: { page?: number; limit?: number; status?: string }): Promise<any> {
    const { page = 1, limit = 20, status } = params;
    const offset = (page - 1) * limit;

    let whereConditions = [];
    if (status) {
      whereConditions.push(eq(execucoes.status, status));
    }

    const data = await db
      .select()
      .from(execucoes)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined)
      .orderBy(desc(execucoes.iniciadoEm))
      .limit(limit)
      .offset(offset);

    const [totalResult] = await db
      .select({ count: count() })
      .from(execucoes)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined);

    return {
      data,
      total: totalResult.count,
      page,
      limit,
      totalPages: Math.ceil(totalResult.count / limit),
    };
  }

  async createExecucao(execucao: InsertExecucao): Promise<Execucao> {
    const [newExecucao] = await db
      .insert(execucoes)
      .values(execucao)
      .returning();
    return newExecucao;
  }

  async updateExecucaoStatus(id: number, updates: Partial<Execucao>): Promise<Execucao> {
    const [updatedExecucao] = await db
      .update(execucoes)
      .set(updates)
      .where(eq(execucoes.id, id))
      .returning();
    return updatedExecucao;
  }

  async getFaturas(params: { page?: number; limit?: number; statusAprovacao?: string }): Promise<any> {
    const { page = 1, limit = 20, statusAprovacao } = params;
    const offset = (page - 1) * limit;

    let whereConditions = [];
    if (statusAprovacao) {
      whereConditions.push(eq(faturas.statusAprovacao, statusAprovacao));
    }

    const data = await db
      .select()
      .from(faturas)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined)
      .orderBy(desc(faturas.dataVencimento))
      .limit(limit)
      .offset(offset);

    const [totalResult] = await db
      .select({ count: count() })
      .from(faturas)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined);

    return {
      data,
      total: totalResult.count,
      page,
      limit,
      totalPages: Math.ceil(totalResult.count / limit),
    };
  }

  async createFatura(fatura: InsertFatura): Promise<Fatura> {
    const [newFatura] = await db
      .insert(faturas)
      .values(fatura)
      .returning();
    return newFatura;
  }

  async aprovarFatura(id: number, aprovadoPor: number): Promise<Fatura> {
    const [fatura] = await db
      .update(faturas)
      .set({
        statusAprovacao: 'aprovada',
        aprovadoPor,
        dataAprovacao: new Date(),
      })
      .where(eq(faturas.id, id))
      .returning();
    return fatura;
  }

  async rejeitarFatura(id: number, motivoRejeicao: string): Promise<Fatura> {
    const [fatura] = await db
      .update(faturas)
      .set({
        statusAprovacao: 'rejeitada',
        motivoRejeicao,
        dataAprovacao: new Date(),
      })
      .where(eq(faturas.id, id))
      .returning();
    return fatura;
  }

  async getOperadoras(): Promise<Operadora[]> {
    return await db.select().from(operadoras).orderBy(operadoras.nome);
  }

  async getOperadorasStatus(): Promise<any[]> {
    const operadorasList = await this.getOperadoras();
    
    return operadorasList.map(operadora => ({
      id: operadora.id,
      nome: operadora.nome,
      codigo: operadora.codigo,
      status: 'ativo',
      ultimaExecucao: new Date(),
      totalExecucoes: Math.floor(Math.random() * 100),
      sucessoRate: Math.floor(Math.random() * 30) + 70,
    }));
  }

  async createOperadora(operadora: InsertOperadora): Promise<Operadora> {
    const [newOperadora] = await db
      .insert(operadoras)
      .values(operadora)
      .returning();
    return newOperadora;
  }

  async getClientes(params: { page?: number; limit?: number; search?: string }): Promise<any> {
    const { page = 1, limit = 20, search } = params;
    const offset = (page - 1) * limit;

    let whereConditions = [];
    if (search) {
      whereConditions.push(
        like(clientes.nomeSat, `%${search}%`)
      );
    }

    const data = await db
      .select()
      .from(clientes)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined)
      .orderBy(clientes.nomeSat)
      .limit(limit)
      .offset(offset);

    const [totalResult] = await db
      .select({ count: count() })
      .from(clientes)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined);

    return {
      data,
      total: totalResult.count,
      page,
      limit,
      totalPages: Math.ceil(totalResult.count / limit),
    };
  }

  async createCliente(cliente: InsertCliente): Promise<Cliente> {
    const [newCliente] = await db
      .insert(clientes)
      .values(cliente)
      .returning();
    return newCliente;
  }

  async getContratos(params: { clienteId?: number; operadoraId?: number }): Promise<Contrato[]> {
    const { clienteId, operadoraId } = params;

    let whereConditions = [];
    if (clienteId) {
      whereConditions.push(eq(contratos.clienteId, clienteId));
    }
    if (operadoraId) {
      whereConditions.push(eq(contratos.operadoraId, operadoraId));
    }

    return await db
      .select()
      .from(contratos)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined)
      .orderBy(contratos.hash);
  }

  async createContrato(contrato: InsertContrato): Promise<Contrato> {
    const [newContrato] = await db
      .insert(contratos)
      .values(contrato)
      .returning();
    return newContrato;
  }

  async getNotificacoes(userId?: number): Promise<Notificacao[]> {
    let whereConditions = [];
    if (userId) {
      whereConditions.push(eq(notificacoes.userId, userId));
    }

    return await db
      .select()
      .from(notificacoes)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined)
      .orderBy(desc(notificacoes.createdAt))
      .limit(50);
  }

  async createNotificacao(notificacao: InsertNotificacao): Promise<Notificacao> {
    const [newNotificacao] = await db
      .insert(notificacoes)
      .values(notificacao)
      .returning();
    return newNotificacao;
  }

  async marcarNotificacaoLida(id: number): Promise<Notificacao> {
    const [notificacao] = await db
      .update(notificacoes)
      .set({ lida: true })
      .where(eq(notificacoes.id, id))
      .returning();
    return notificacao;
  }

  async iniciarExecucaoGeral(): Promise<any> {
    // Buscar todos os contratos ativos
    const contratosAtivos = await db
      .select()
      .from(contratos)
      .where(eq(contratos.status, 'ativo'));

    const execucoesIniciadas = [];

    for (const contrato of contratosAtivos) {
      const execucao = await this.createExecucao({
        contratoId: contrato.id,
        status: 'pendente',
        iniciadoEm: new Date(),
        sessionId: `exec_${Date.now()}_${contrato.id}`,
      });
      execucoesIniciadas.push(execucao);
    }

    return {
      message: `${execucoesIniciadas.length} execuções iniciadas`,
      execucoes: execucoesIniciadas,
    };
  }

  async iniciarExecucaoRPA(contratoId: number): Promise<any> {
    const execucao = await this.createExecucao({
      contratoId,
      status: 'pendente',
      iniciadoEm: new Date(),
      sessionId: `exec_${Date.now()}_${contratoId}`,
    });

    return {
      message: 'Execução RPA iniciada com sucesso',
      execucao,
    };
  }

  async getRelatorioExecucoes(params: { dataInicio?: string; dataFim?: string; operadoraId?: number }): Promise<any> {
    const { dataInicio, dataFim, operadoraId } = params;

    let whereConditions = [];
    if (dataInicio) {
      whereConditions.push(gte(execucoes.iniciadoEm, new Date(dataInicio)));
    }
    if (dataFim) {
      whereConditions.push(lte(execucoes.iniciadoEm, new Date(dataFim)));
    }

    const data = await db
      .select()
      .from(execucoes)
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined)
      .orderBy(desc(execucoes.iniciadoEm))
      .limit(1000);

    return {
      execucoes: data,
      estatisticas: {
        total: data.length,
        sucesso: data.filter(e => e.status === 'sucesso').length,
        erro: data.filter(e => e.status === 'erro').length,
        pendente: data.filter(e => e.status === 'pendente').length,
      },
    };
  }

  async initializeFromCSV(): Promise<void> {
    // Create initial data if tables are empty
    const [operadoraCount] = await db.select({ count: count() }).from(operadoras);
    
    if (operadoraCount.count === 0) {
      // Insert initial operators
      await db.insert(operadoras).values([
        { nome: 'Vivo', codigo: 'VIVO' },
        { nome: 'OI', codigo: 'OI' },
        { nome: 'Embratel', codigo: 'EMBRATEL' },
        { nome: 'SAT', codigo: 'SAT' },
        { nome: 'Azuton', codigo: 'AZUTON' },
        { nome: 'DigitalNet', codigo: 'DIGITALNET' },
      ]);
    }

    const [clienteCount] = await db.select({ count: count() }).from(clientes);
    
    if (clienteCount.count === 0) {
      // Insert sample clients
      await db.insert(clientes).values([
        { nomeSat: 'BGTELECOM', cnpj: '12.345.678/0001-90' },
        { nomeSat: 'Empresa Exemplo', cnpj: '98.765.432/0001-10' },
      ]);
    }
  }
}

export const storage = new DatabaseStorage();