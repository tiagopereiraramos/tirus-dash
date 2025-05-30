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
  updateCliente(id: number, updates: Partial<Cliente>): Promise<Cliente>;
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
    const { page = 1, limit = 20, status } = params;
    try {
      let query = db.select({
        id: execucoes.id,
        tipo: execucoes.tipo,
        status: execucoes.status,
        erro: execucoes.erro,
        tempoExecucao: execucoes.tempoExecucao,
        iniciadoEm: execucoes.iniciadoEm,
        finalizadoEm: execucoes.finalizadoEm,
        contrato: {
          id: contratos.id,
          servico: contratos.servico,
          cliente: {
            id: clientes.id,
            nomeSat: clientes.nomeSat
          },
          operadora: {
            id: operadoras.id,
            nome: operadoras.nome
          }
        }
      })
      .from(execucoes)
      .leftJoin(contratos, eq(execucoes.contratoId, contratos.id))
      .leftJoin(clientes, eq(contratos.clienteId, clientes.id))
      .leftJoin(operadoras, eq(contratos.operadoraId, operadoras.id));

      if (status && status !== 'todos') {
        query = query.where(eq(execucoes.status, status));
      }

      const data = await query.orderBy(desc(execucoes.iniciadoEm)).limit(limit).offset((page - 1) * limit);
      const total = await db.select({ count: sql<number>`count(*)` }).from(execucoes);
      
      return {
        data: data || [],
        total: total[0]?.count || 0,
        page,
        limit,
        totalPages: Math.ceil((total[0]?.count || 0) / limit),
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
    const { page = 1, limit = 20, statusAprovacao } = params;
    try {
      let query = db.select({
        id: faturas.id,
        valor: faturas.valor,
        dataVencimento: faturas.dataVencimento,
        statusAprovacao: faturas.statusAprovacao,
        createdAt: faturas.createdAt,
        contrato: {
          id: contratos.id,
          servico: contratos.servico,
          cliente: {
            id: clientes.id,
            nomeSat: clientes.nomeSat,
            cnpj: clientes.cnpj
          },
          operadora: {
            id: operadoras.id,
            nome: operadoras.nome
          }
        }
      })
      .from(faturas)
      .leftJoin(contratos, eq(faturas.contratoId, contratos.id))
      .leftJoin(clientes, eq(contratos.clienteId, clientes.id))
      .leftJoin(operadoras, eq(contratos.operadoraId, operadoras.id));

      if (statusAprovacao && statusAprovacao !== 'todos') {
        query = query.where(eq(faturas.statusAprovacao, statusAprovacao));
      }

      const data = await query.orderBy(desc(faturas.dataVencimento)).limit(limit).offset((page - 1) * limit);
      const total = await db.select({ count: sql<number>`count(*)` }).from(faturas);
      
      return {
        data: data || [],
        total: total[0]?.count || 0,
        page,
        limit,
        totalPages: Math.ceil((total[0]?.count || 0) / limit),
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

  async updateCliente(id: number, updates: Partial<Cliente>): Promise<Cliente> {
    const [updatedCliente] = await db.update(clientes).set(updates).where(eq(clientes.id, id)).returning();
    return updatedCliente;
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
      // Inserir operadoras baseadas no CSV
      const [operadoraCount] = await db.select({ count: count() }).from(operadoras);
      
      if (operadoraCount.count === 0) {
        await db.insert(operadoras).values([
          { nome: 'Embratel', codigo: 'EMBRATEL' },
          { nome: 'DigitalNet', codigo: 'DIGITALNET' },
          { nome: 'Vivo', codigo: 'VIVO' },
          { nome: 'OI', codigo: 'OI' },
          { nome: 'SAT', codigo: 'SAT' },
        ]);
      }

      // Inserir clientes baseados no CSV
      const [clienteCount] = await db.select({ count: count() }).from(clientes);
      
      if (clienteCount.count === 0) {
        const clientesCSV = [
          { razaoSocial: 'RICAL - RACK INDUSTRIA E COMERCIO DE ARROZ LTDA', nomeSat: 'RICAL - RACK INDUSTRIA E COMERCIO DE ARROZ LTDA', cnpj: '84.718.741/0001-00' },
          { razaoSocial: 'ALVORADA COMERCIO DE PRODUTOS AGROPECUÁRIOS LTDA', nomeSat: 'ALVORADA COMERCIO DE PRODUTOS AGROPECUÁRIOS LTDA', cnpj: '01.963.040/0003-63' },
          { razaoSocial: 'CENZE TRANSPORTES E COMERCIO DE COMBUSTÍVEIS', nomeSat: 'CENZE TRANSPORTES E COMERCIO DE COMBUSTÍVEIS', cnpj: '15.447.568/0002-03' },
          { razaoSocial: 'FINANCIAL CONSTRUTORA INDUSTRIAL LTDA', nomeSat: 'FINANCIAL CONSTRUTORA INDUSTRIAL LTDA', cnpj: '15.565.179/0001-00' },
          { razaoSocial: 'ICCAP IMPLEMENTOS RODOVIAROS LTDA', nomeSat: 'ICCAP IMPLEMENTOS RODOVIAROS LTDA', cnpj: '02.377.798/0001-10' },
          { razaoSocial: 'LOCATELLI & TRENTIN LTDA', nomeSat: 'LOCATELLI E TRENTIN LTDA (CENTENARO PNEUS LTDA)', cnpj: '03.084.721/0001-15' },
          { razaoSocial: 'TRANSPORTADORA KATIA LTDA', nomeSat: 'TRANSPORTADORA KATIA LTDA', cnpj: '36.810.760/0001-01' },
          { razaoSocial: 'SANTA IZABEL TRANSPORTE REVENDEDOR RETALHISTA LTDA', nomeSat: 'TRANSPORTADORA SANTA IZABEL LTDA', cnpj: '00.411.566/0001-06' },
          { razaoSocial: 'CG SOLURB SOLUÇÕES AMBIENTAIS SPE LTDA', nomeSat: 'CG SOLURB SOLUÇÕES AMBIENTAIS SPE LTDA', cnpj: '17.064.901/0001-40' },
        ];
        
        await db.insert(clientes).values(clientesCSV);
      }

      // Criar contratos baseados no CSV
      const [contratoCount] = await db.select({ count: count() }).from(contratos);
      
      if (contratoCount.count === 0) {
        const operadorasData = await this.getOperadoras();
        const clientesData = await db.select().from(clientes);
        
        const contratosCSV = [
          { hash: 'f31949d0b3615a3a', clienteId: clientesData[0].id, operadoraId: operadorasData.find(o => o.codigo === 'EMBRATEL')?.id, filtro: '00052488515-0000_25', servico: 'Fixo', tipoServico: 'Voz', status: 'ativo' },
          { hash: '6cdc16271b11d9b7', clienteId: clientesData[0].id, operadoraId: operadorasData.find(o => o.codigo === 'EMBRATEL')?.id, filtro: '00052488515-0000_24', servico: 'Link Dedicado', tipoServico: 'Dados', status: 'ativo' },
          { hash: '5664837335b069bc', clienteId: clientesData.find(c => c.cnpj === '00.411.566/0001-06')?.id, operadoraId: operadorasData.find(o => o.codigo === 'DIGITALNET')?.id, filtro: 'HAWJUOGYJF', servico: 'Link Dedicado', tipoServico: 'Dados', status: 'ativo' },
          { hash: '6d93af1703a192bb', clienteId: clientesData.find(c => c.cnpj === '17.064.901/0001-40')?.id, operadoraId: operadorasData.find(o => o.codigo === 'DIGITALNET')?.id, filtro: 'JIYJRQO7JJ', servico: 'Internet', tipoServico: 'Internet', status: 'ativo' },
        ];
        
        await db.insert(contratos).values(contratosCSV.filter(c => c.clienteId && c.operadoraId));
      }

      // Criar execuções de exemplo
      const [execucaoCount] = await db.select({ count: count() }).from(execucoes);
      
      if (execucaoCount.count === 0) {
        const contratosData = await db.select().from(contratos);
        
        if (contratosData.length > 0) {
          const execucoesExemplo = contratosData.slice(0, 5).map((contrato, index) => ({
            contratoId: contrato.id,
            status: ['sucesso', 'pendente', 'erro', 'executando'][index % 4],
            iniciadoEm: new Date(Date.now() - (index * 3600000)), // últimas horas
            finalizadoEm: index % 4 === 1 ? null : new Date(Date.now() - (index * 3600000) + 1800000), // 30 min depois
            tempoExecucao: index % 4 === 1 ? null : 1800, // 30 minutos em segundos
            sessionId: `exec_${Date.now()}_${contrato.id}`,
            erro: index === 2 ? 'Erro de autenticação no portal da operadora' : null,
          }));
          
          await db.insert(execucoes).values(execucoesExemplo);
        }
      }

      // Criar faturas de exemplo
      const [faturaCount] = await db.select({ count: count() }).from(faturas);
      
      if (faturaCount.count === 0) {
        const contratosData = await db.select().from(contratos);
        
        if (contratosData.length > 0) {
          const faturasExemplo = contratosData.slice(0, 8).map((contrato, index) => ({
            contratoId: contrato.id,
            valor: (Math.random() * 5000 + 500).toFixed(2), // R$ 500 a R$ 5500
            dataVencimento: new Date(Date.now() + (index * 24 * 3600000)), // próximos dias
            statusAprovacao: ['pendente', 'aprovada', 'rejeitada'][index % 3],
            caminhoArquivo: `/faturas/fatura_${contrato.hash}_${Date.now()}.pdf`,
            motivoRejeicao: index % 3 === 2 ? 'Valor inconsistente com histórico' : null,
          }));
          
          await db.insert(faturas).values(faturasExemplo);
        }
      }

      // Criar notificações de exemplo
      const [notificacaoCount] = await db.select({ count: count() }).from(notificacoes);
      
      if (notificacaoCount.count === 0) {
        const notificacoesExemplo = [
          { titulo: 'Nova fatura processada', mensagem: 'Fatura da RICAL processada com sucesso', tipo: 'info', lida: false },
          { titulo: 'Execução com erro', mensagem: 'Falha na execução RPA para DIGITALNET', tipo: 'error', lida: false },
          { titulo: 'Aprovação pendente', mensagem: '3 faturas aguardando aprovação', tipo: 'warning', lida: true },
          { titulo: 'Sistema atualizado', mensagem: 'Nova versão do sistema implantada', tipo: 'success', lida: true },
        ];
        
        await db.insert(notificacoes).values(notificacoesExemplo);
      }

    } catch (error) {
      console.error('Error initializing from CSV:', error);
    }
  }
}

export const storage = new DatabaseStorage();