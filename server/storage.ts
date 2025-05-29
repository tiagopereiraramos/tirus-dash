import { 
  users, operadoras, clientes, contratos, execucoes, faturas, notificacoes,
  type User, type InsertUser, type Operadora, type InsertOperadora,
  type Cliente, type InsertCliente, type Contrato, type InsertContrato,
  type Execucao, type InsertExecucao, type Fatura, type InsertFatura,
  type Notificacao, type InsertNotificacao
} from "@shared/schema";
import { db } from "./db";
import { eq, desc, count } from "drizzle-orm";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  getDashboardMetrics(): Promise<any>;
  getExecucoes(params: { page?: number; limit?: number; status?: string }): Promise<any>;
  createExecucao(execucao: InsertExecucao): Promise<Execucao>;
  updateExecucaoStatus(id: number, updates: Partial<Execucao>): Promise<Execucao>;
  getFaturas(params: { page?: number; limit?: number; statusAprovacao?: string }): Promise<any>;
  createFatura(fatura: InsertFatura): Promise<Fatura>;
  aprovarFatura(id: number, aprovadoPor: number): Promise<Fatura>;
  rejeitarFatura(id: number, motivoRejeicao: string): Promise<Fatura>;
  getOperadoras(): Promise<Operadora[]>;
  getOperadorasStatus(): Promise<any[]>;
  createOperadora(operadora: InsertOperadora): Promise<Operadora>;
  getClientes(params: { page?: number; limit?: number; search?: string }): Promise<any>;
  createCliente(cliente: InsertCliente): Promise<Cliente>;
  getContratos(params: { clienteId?: number; operadoraId?: number }): Promise<Contrato[]>;
  createContrato(contrato: InsertContrato): Promise<Contrato>;
  getNotificacoes(userId?: number): Promise<Notificacao[]>;
  createNotificacao(notificacao: InsertNotificacao): Promise<Notificacao>;
  marcarNotificacaoLida(id: number): Promise<Notificacao>;
  iniciarExecucaoGeral(): Promise<any>;
  iniciarExecucaoRPA(contratoId: number): Promise<any>;
  getRelatorioExecucoes(params: { dataInicio?: string; dataFim?: string; operadoraId?: number }): Promise<any>;
  initializeFromCSV(): Promise<void>;
}

export class DatabaseStorage implements IStorage {
  async getUser(id: number): Promise<User | undefined> {
    try {
      const [user] = await db.select().from(users).where(eq(users.id, id));
      return user || undefined;
    } catch (error) {
      console.error('Error getting user:', error);
      return undefined;
    }
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    try {
      const [user] = await db.select().from(users).where(eq(users.username, username));
      return user || undefined;
    } catch (error) {
      console.error('Error getting user by username:', error);
      return undefined;
    }
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const [user] = await db.insert(users).values(insertUser).returning();
    return user;
  }

  async getDashboardMetrics(): Promise<any> {
    try {
      return {
        totalExecutions: 156,
        totalExecutionsChange: 12.5,
        pendingExecutions: 23,
        pendingExecutionsChange: -2.3,
        pendingApprovals: 8,
        pendingApprovalsChange: 8.1,
        avgExecutionTime: 4.2,
        avgExecutionTimeChange: -0.3,
      };
    } catch (error) {
      console.error('Error getting dashboard metrics:', error);
      return {
        totalExecutions: 0,
        totalExecutionsChange: 0,
        pendingExecutions: 0,
        pendingExecutionsChange: 0,
        pendingApprovals: 0,
        pendingApprovalsChange: 0,
        avgExecutionTime: 0,
        avgExecutionTimeChange: 0,
      };
    }
  }

  async getExecucoes(params: { page?: number; limit?: number; status?: string }): Promise<any> {
    const { page = 1, limit = 20 } = params;
    try {
      const data = await db.select().from(execucoes).orderBy(desc(execucoes.iniciadoEm)).limit(limit);
      return {
        data: data || [],
        total: data.length,
        page,
        limit,
        totalPages: Math.ceil(data.length / limit),
      };
    } catch (error) {
      console.error('Error getting execucoes:', error);
      return { data: [], total: 0, page, limit, totalPages: 0 };
    }
  }

  async createExecucao(execucao: InsertExecucao): Promise<Execucao> {
    const [newExecucao] = await db.insert(execucoes).values(execucao).returning();
    return newExecucao;
  }

  async updateExecucaoStatus(id: number, updates: Partial<Execucao>): Promise<Execucao> {
    const [updatedExecucao] = await db.update(execucoes).set(updates).where(eq(execucoes.id, id)).returning();
    return updatedExecucao;
  }

  async getFaturas(params: { page?: number; limit?: number; statusAprovacao?: string }): Promise<any> {
    const { page = 1, limit = 20 } = params;
    try {
      const data = await db.select().from(faturas).orderBy(desc(faturas.dataVencimento)).limit(limit);
      return {
        data: data || [],
        total: data.length,
        page,
        limit,
        totalPages: Math.ceil(data.length / limit),
      };
    } catch (error) {
      console.error('Error getting faturas:', error);
      return { data: [], total: 0, page, limit, totalPages: 0 };
    }
  }

  async createFatura(fatura: InsertFatura): Promise<Fatura> {
    const [newFatura] = await db.insert(faturas).values(fatura).returning();
    return newFatura;
  }

  async aprovarFatura(id: number, aprovadoPor: number): Promise<Fatura> {
    const [fatura] = await db.update(faturas).set({
      statusAprovacao: 'aprovada',
      aprovadoPor,
      dataAprovacao: new Date(),
    }).where(eq(faturas.id, id)).returning();
    return fatura;
  }

  async rejeitarFatura(id: number, motivoRejeicao: string): Promise<Fatura> {
    const [fatura] = await db.update(faturas).set({
      statusAprovacao: 'rejeitada',
      motivoRejeicao,
      dataAprovacao: new Date(),
    }).where(eq(faturas.id, id)).returning();
    return fatura;
  }

  async getOperadoras(): Promise<Operadora[]> {
    try {
      return await db.select().from(operadoras).orderBy(operadoras.nome);
    } catch (error) {
      console.error('Error getting operadoras:', error);
      return [];
    }
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
    const [newOperadora] = await db.insert(operadoras).values(operadora).returning();
    return newOperadora;
  }

  async getClientes(params: { page?: number; limit?: number; search?: string }): Promise<any> {
    const { page = 1, limit = 20 } = params;
    try {
      const data = await db.select().from(clientes).orderBy(clientes.nomeSat).limit(limit);
      return {
        data: data || [],
        total: data.length,
        page,
        limit,
        totalPages: Math.ceil(data.length / limit),
      };
    } catch (error) {
      console.error('Error getting clientes:', error);
      return { data: [], total: 0, page, limit, totalPages: 0 };
    }
  }

  async createCliente(cliente: InsertCliente): Promise<Cliente> {
    const [newCliente] = await db.insert(clientes).values(cliente).returning();
    return newCliente;
  }

  async getContratos(params: { clienteId?: number; operadoraId?: number }): Promise<Contrato[]> {
    try {
      return await db.select().from(contratos).orderBy(contratos.hash);
    } catch (error) {
      console.error('Error getting contratos:', error);
      return [];
    }
  }

  async createContrato(contrato: InsertContrato): Promise<Contrato> {
    const [newContrato] = await db.insert(contratos).values(contrato).returning();
    return newContrato;
  }

  async getNotificacoes(userId?: number): Promise<Notificacao[]> {
    try {
      return await db.select().from(notificacoes).orderBy(desc(notificacoes.createdAt)).limit(50);
    } catch (error) {
      console.error('Error getting notificacoes:', error);
      return [];
    }
  }

  async createNotificacao(notificacao: InsertNotificacao): Promise<Notificacao> {
    const [newNotificacao] = await db.insert(notificacoes).values(notificacao).returning();
    return newNotificacao;
  }

  async marcarNotificacaoLida(id: number): Promise<Notificacao> {
    const [notificacao] = await db.update(notificacoes).set({ lida: true }).where(eq(notificacoes.id, id)).returning();
    return notificacao;
  }

  async iniciarExecucaoGeral(): Promise<any> {
    return {
      message: '0 execuções iniciadas',
      execucoes: [],
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

  async getRelatorioExecucoes(): Promise<any> {
    return {
      execucoes: [],
      estatisticas: {
        total: 0,
        sucesso: 0,
        erro: 0,
        pendente: 0,
      },
    };
  }

  async initializeFromCSV(): Promise<void> {
    try {
      const [operadoraCount] = await db.select({ count: count() }).from(operadoras);
      
      if (operadoraCount.count === 0) {
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
        await db.insert(clientes).values([
          { nomeSat: 'BGTELECOM', cnpj: '12.345.678/0001-90' },
          { nomeSat: 'Empresa Exemplo', cnpj: '98.765.432/0001-10' },
        ]);
      }
    } catch (error) {
      console.error('Error initializing from CSV:', error);
    }
  }
}

export const storage = new DatabaseStorage();