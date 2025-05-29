import { 
  users, operadoras, clientes, contratos, execucoes, faturas, notificacoes,
  type User, type InsertUser, type Operadora, type InsertOperadora,
  type Cliente, type InsertCliente, type Contrato, type InsertContrato,
  type Execucao, type InsertExecucao, type Fatura, type InsertFatura,
  type Notificacao, type InsertNotificacao
} from "@shared/schema";
import { db } from "./db";
import { eq, desc, and, like, sql, count } from "drizzle-orm";
import fs from "fs";
import path from "path";

// Interface expandida para incluir todos os métodos necessários
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
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    // Execuções de hoje
    const [execucoesToday] = await db
      .select({ count: count() })
      .from(execucoes)
      .where(sql`${execucoes.iniciadoEm} >= ${today}`);

    // Taxa de sucesso
    const [totalExecucoes] = await db
      .select({ count: count() })
      .from(execucoes);

    const [execucoesSucesso] = await db
      .select({ count: count() })
      .from(execucoes)
      .where(eq(execucoes.status, "concluido"));

    // Aprovações pendentes
    const [aprovacoesPendentes] = await db
      .select({ count: count() })
      .from(faturas)
      .where(eq(faturas.statusAprovacao, "pendente"));

    // Tempo médio de execução
    const [tempoMedio] = await db
      .select({ avg: sql<number>`AVG(${execucoes.tempoExecucao})` })
      .from(execucoes)
      .where(eq(execucoes.status, "concluido"));

    const successRate = totalExecucoes.count > 0 
      ? (execucoesSucesso.count / totalExecucoes.count) * 100 
      : 0;

    return {
      execucoesToday: execucoesToday.count,
      execucoesTodayChange: 12, // Mock para comparação
      successRate: Number(successRate.toFixed(1)),
      successRateChange: 2.1, // Mock para comparação
      pendingApprovals: aprovacoesPendentes.count,
      pendingApprovalsChange: -5, // Mock para comparação
      avgExecutionTime: tempoMedio.avg ? Number((tempoMedio.avg / 60).toFixed(1)) : 0,
      avgExecutionTimeChange: -0.3, // Mock para comparação
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
      .leftJoin(contratos, eq(execucoes.contratoId, contratos.id))
      .leftJoin(clientes, eq(contratos.clienteId, clientes.id))
      .leftJoin(operadoras, eq(contratos.operadoraId, operadoras.id))
      .where(whereConditions.length > 0 ? and(...whereConditions) : undefined)
      .orderBy(desc(execucoes.iniciadoEm))
      .limit(limit)
      .offset(offset);

    const [totalResult] = await db
      .select({ count: count() })
      .from(execucoes)
      .where(status ? eq(execucoes.status, status) : undefined);

    return {
      data,
      total: totalResult.count,
      page,
      limit,
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

    let query = db
      .select({
        id: faturas.id,
        valor: faturas.valor,
        dataVencimento: faturas.dataVencimento,
        dataCompetencia: faturas.dataCompetencia,
        statusAprovacao: faturas.statusAprovacao,
        aprovadoEm: faturas.aprovadoEm,
        motivoRejeicao: faturas.motivoRejeicao,
        createdAt: faturas.createdAt,
        contrato: {
          id: contratos.id,
          hash: contratos.hash,
          servico: contratos.servico,
          cliente: {
            id: clientes.id,
            nomeSat: clientes.nomeSat,
            cnpj: clientes.cnpj,
          },
          operadora: {
            id: operadoras.id,
            nome: operadoras.nome,
            codigo: operadoras.codigo,
          },
        },
      })
      .from(faturas)
      .leftJoin(contratos, eq(faturas.contratoId, contratos.id))
      .leftJoin(clientes, eq(contratos.clienteId, clientes.id))
      .leftJoin(operadoras, eq(contratos.operadoraId, operadoras.id))
      .orderBy(desc(faturas.createdAt))
      .limit(limit)
      .offset(offset);

    if (statusAprovacao) {
      query = query.where(eq(faturas.statusAprovacao, statusAprovacao));
    }

    const data = await query;

    const [totalResult] = await db
      .select({ count: count() })
      .from(faturas)
      .where(statusAprovacao ? eq(faturas.statusAprovacao, statusAprovacao) : undefined);

    return {
      data,
      total: totalResult.count,
      page,
      limit,
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
    const [updatedFatura] = await db
      .update(faturas)
      .set({
        statusAprovacao: "aprovada",
        aprovadoPor,
        aprovadoEm: new Date(),
      })
      .where(eq(faturas.id, id))
      .returning();
    return updatedFatura;
  }

  async rejeitarFatura(id: number, motivoRejeicao: string): Promise<Fatura> {
    const [updatedFatura] = await db
      .update(faturas)
      .set({
        statusAprovacao: "rejeitada",
        motivoRejeicao,
      })
      .where(eq(faturas.id, id))
      .returning();
    return updatedFatura;
  }

  async getOperadoras(): Promise<Operadora[]> {
    return await db.select().from(operadoras);
  }

  async getOperadorasStatus(): Promise<any[]> {
    // Buscar operadoras com estatísticas
    const operadorasData = await db
      .select({
        id: operadoras.id,
        nome: operadoras.nome,
        codigo: operadoras.codigo,
        status: operadoras.status,
      })
      .from(operadoras);

    // Para cada operadora, calcular estatísticas
    const result = await Promise.all(
      operadorasData.map(async (operadora) => {
        // Total de execuções
        const [totalExecucoes] = await db
          .select({ count: count() })
          .from(execucoes)
          .leftJoin(contratos, eq(execucoes.contratoId, contratos.id))
          .where(eq(contratos.operadoraId, operadora.id));

        // Execuções com sucesso
        const [execucoesSucesso] = await db
          .select({ count: count() })
          .from(execucoes)
          .leftJoin(contratos, eq(execucoes.contratoId, contratos.id))
          .where(
            and(
              eq(contratos.operadoraId, operadora.id),
              eq(execucoes.status, "concluido")
            )
          );

        // Última execução
        const [ultimaExecucao] = await db
          .select({ iniciadoEm: execucoes.iniciadoEm })
          .from(execucoes)
          .leftJoin(contratos, eq(execucoes.contratoId, contratos.id))
          .where(eq(contratos.operadoraId, operadora.id))
          .orderBy(desc(execucoes.iniciadoEm))
          .limit(1);

        const taxaSucesso = totalExecucoes.count > 0 
          ? (execucoesSucesso.count / totalExecucoes.count) * 100 
          : 0;

        return {
          ...operadora,
          taxaSucesso: Number(taxaSucesso.toFixed(1)),
          totalExecucoes: totalExecucoes.count,
          ultimaExecucao: ultimaExecucao?.iniciadoEm || null,
        };
      })
    );

    return result;
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

    let query = db
      .select({
        id: clientes.id,
        razaoSocial: clientes.razaoSocial,
        nomeSat: clientes.nomeSat,
        cnpj: clientes.cnpj,
        status: clientes.status,
        createdAt: clientes.createdAt,
      })
      .from(clientes)
      .orderBy(desc(clientes.createdAt))
      .limit(limit)
      .offset(offset);

    if (search) {
      query = query.where(
        sql`${clientes.razaoSocial} ILIKE ${'%' + search + '%'} OR ${clientes.nomeSat} ILIKE ${'%' + search + '%'} OR ${clientes.cnpj} ILIKE ${'%' + search + '%'}`
      );
    }

    const data = await query;

    // Adicionar contagem de contratos para cada cliente
    const clientesComContratos = await Promise.all(
      data.map(async (cliente) => {
        const [contratos] = await db
          .select({ count: count() })
          .from(contratos)
          .where(eq(contratos.clienteId, cliente.id));

        return {
          ...cliente,
          totalContratos: contratos.count,
        };
      })
    );

    const [totalResult] = await db
      .select({ count: count() })
      .from(clientes)
      .where(search ? sql`${clientes.razaoSocial} ILIKE ${'%' + search + '%'} OR ${clientes.nomeSat} ILIKE ${'%' + search + '%'} OR ${clientes.cnpj} ILIKE ${'%' + search + '%'}` : undefined);

    const [ativosResult] = await db
      .select({ count: count() })
      .from(clientes)
      .where(eq(clientes.status, "ativo"));

    const [totalContratosResult] = await db
      .select({ count: count() })
      .from(contratos);

    return {
      data: clientesComContratos,
      total: totalResult.count,
      ativos: ativosResult.count,
      totalContratos: totalContratosResult.count,
      page,
      limit,
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

    let query = db
      .select({
        id: contratos.id,
        hash: contratos.hash,
        filtro: contratos.filtro,
        servico: contratos.servico,
        tipoServico: contratos.tipoServico,
        status: contratos.status,
        cliente: {
          id: clientes.id,
          nomeSat: clientes.nomeSat,
          cnpj: clientes.cnpj,
        },
        operadora: {
          id: operadoras.id,
          nome: operadoras.nome,
          codigo: operadoras.codigo,
        },
      })
      .from(contratos)
      .leftJoin(clientes, eq(contratos.clienteId, clientes.id))
      .leftJoin(operadoras, eq(contratos.operadoraId, operadoras.id));

    if (clienteId) {
      query = query.where(eq(contratos.clienteId, clienteId));
    }

    if (operadoraId) {
      query = query.where(eq(contratos.operadoraId, operadoraId));
    }

    return await query;
  }

  async createContrato(contrato: InsertContrato): Promise<Contrato> {
    const [newContrato] = await db
      .insert(contratos)
      .values(contrato)
      .returning();
    return newContrato;
  }

  async getNotificacoes(userId?: number): Promise<Notificacao[]> {
    let query = db
      .select()
      .from(notificacoes)
      .orderBy(desc(notificacoes.createdAt))
      .limit(50);

    if (userId) {
      query = query.where(eq(notificacoes.userId, userId));
    }

    return await query;
  }

  async createNotificacao(notificacao: InsertNotificacao): Promise<Notificacao> {
    const [newNotificacao] = await db
      .insert(notificacoes)
      .values(notificacao)
      .returning();
    return newNotificacao;
  }

  async marcarNotificacaoLida(id: number): Promise<Notificacao> {
    const [updatedNotificacao] = await db
      .update(notificacoes)
      .set({ lida: true })
      .where(eq(notificacoes.id, id))
      .returning();
    return updatedNotificacao;
  }

  async iniciarExecucaoGeral(): Promise<any> {
    // Buscar todos os contratos ativos
    const contratosAtivos = await db
      .select()
      .from(contratos)
      .where(eq(contratos.status, "ativo"));

    // Criar execuções para todos os contratos
    const execucoesPromises = contratosAtivos.map(async (contrato) => {
      return await this.createExecucao({
        contratoId: contrato.id,
        sessionId: `bulk_${Date.now()}_${contrato.id}`,
        status: "pendente",
      });
    });

    const novasExecucoes = await Promise.all(execucoesPromises);

    return {
      message: "Execução geral iniciada",
      totalContratos: contratosAtivos.length,
      execucoesCriadas: novasExecucoes.length,
    };
  }

  async iniciarExecucaoRPA(contratoId: number): Promise<any> {
    const execucao = await this.createExecucao({
      contratoId,
      sessionId: `manual_${Date.now()}_${contratoId}`,
      status: "pendente",
    });

    return {
      message: "Execução RPA iniciada",
      execucao,
    };
  }

  async getRelatorioExecucoes(params: { dataInicio?: string; dataFim?: string; operadoraId?: number }): Promise<any> {
    const { dataInicio, dataFim, operadoraId } = params;

    let query = db
      .select({
        id: execucoes.id,
        status: execucoes.status,
        iniciadoEm: execucoes.iniciadoEm,
        tempoExecucao: execucoes.tempoExecucao,
        operadora: operadoras.nome,
        cliente: clientes.nomeSat,
      })
      .from(execucoes)
      .leftJoin(contratos, eq(execucoes.contratoId, contratos.id))
      .leftJoin(clientes, eq(contratos.clienteId, clientes.id))
      .leftJoin(operadoras, eq(contratos.operadoraId, operadoras.id));

    if (dataInicio && dataFim) {
      query = query.where(
        and(
          sql`${execucoes.iniciadoEm} >= ${new Date(dataInicio)}`,
          sql`${execucoes.iniciadoEm} <= ${new Date(dataFim)}`
        )
      );
    }

    if (operadoraId) {
      query = query.where(eq(contratos.operadoraId, operadoraId));
    }

    const data = await query;

    return {
      data,
      summary: {
        total: data.length,
        concluidas: data.filter(e => e.status === "concluido").length,
        falharam: data.filter(e => e.status === "falha").length,
        executando: data.filter(e => e.status === "executando").length,
      },
    };
  }

  async initializeFromCSV(): Promise<void> {
    try {
      const csvPath = path.join(process.cwd(), "attached_assets", "DADOS SAT - BGTELECOM - BGTELECOM .csv");
      
      if (!fs.existsSync(csvPath)) {
        console.log("Arquivo CSV não encontrado para inicialização");
        return;
      }

      const csvContent = fs.readFileSync(csvPath, "utf-8");
      const lines = csvContent.split("\n");
      const headers = lines[0].split(",");

      // Processar linhas do CSV (pular header)
      for (let i = 1; i < lines.length && lines[i].trim(); i++) {
        const values = lines[i].split(",");
        
        if (values.length < headers.length) continue;

        const razaoSocial = values[1]?.trim();
        const nomeSat = values[2]?.trim();
        const cnpj = values[3]?.trim();
        const operadoraNome = values[4]?.trim();
        const filtro = values[5]?.trim();
        const servico = values[6]?.trim();
        const tipoServico = values[7]?.trim();
        const url = values[10]?.trim();
        const login = values[11]?.trim();
        const senha = values[12]?.trim();
        const cpf = values[13]?.trim();

        if (!razaoSocial || !cnpj || !operadoraNome) continue;

        // Criar ou buscar operadora
        let operadora = await db
          .select()
          .from(operadoras)
          .where(eq(operadoras.nome, operadoraNome))
          .limit(1);

        if (operadora.length === 0) {
          const [novaOperadora] = await db
            .insert(operadoras)
            .values({
              nome: operadoraNome,
              codigo: operadoraNome.toUpperCase(),
              url: url || null,
              status: "ativo",
            })
            .returning();
          operadora = [novaOperadora];
        }

        // Criar ou buscar cliente
        let cliente = await db
          .select()
          .from(clientes)
          .where(eq(clientes.cnpj, cnpj))
          .limit(1);

        if (cliente.length === 0) {
          const [novoCliente] = await db
            .insert(clientes)
            .values({
              razaoSocial,
              nomeSat,
              cnpj,
              status: "ativo",
            })
            .returning();
          cliente = [novoCliente];
        }

        // Criar contrato
        const hash = values[0]?.trim();
        if (hash) {
          const existingContract = await db
            .select()
            .from(contratos)
            .where(eq(contratos.hash, hash))
            .limit(1);

          if (existingContract.length === 0) {
            await db.insert(contratos).values({
              clienteId: cliente[0].id,
              operadoraId: operadora[0].id,
              hash,
              filtro,
              servico,
              tipoServico,
              login,
              senha,
              cpf,
              status: "ativo",
            });
          }
        }
      }

      console.log("Dados CSV inicializados com sucesso");
    } catch (error) {
      console.error("Erro ao inicializar dados do CSV:", error);
      throw error;
    }
  }
}

export const storage = new DatabaseStorage();
