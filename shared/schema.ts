import { pgTable, text, serial, integer, boolean, timestamp, decimal, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";
import { relations } from "drizzle-orm";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
  email: text("email").notNull(),
  role: text("role").notNull().default("user"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const operadoras = pgTable("operadoras", {
  id: serial("id").primaryKey(),
  nome: text("nome").notNull(),
  codigo: text("codigo").notNull().unique(),
  url: text("url"),
  status: text("status").notNull().default("ativo"),
  configuracao: jsonb("configuracao"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const clientes = pgTable("clientes", {
  id: serial("id").primaryKey(),
  razaoSocial: text("razao_social").notNull(),
  nomeSat: text("nome_sat").notNull(),
  cnpj: text("cnpj").notNull(),
  status: text("status").notNull().default("ativo"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const contratos = pgTable("contratos", {
  id: serial("id").primaryKey(),
  clienteId: integer("cliente_id").references(() => clientes.id),
  operadoraId: integer("operadora_id").references(() => operadoras.id),
  hash: text("hash").notNull().unique(),
  filtro: text("filtro"),
  servico: text("servico"),
  tipoServico: text("tipo_servico"),
  unidade: text("unidade"),
  login: text("login"),
  senha: text("senha"),
  cpf: text("cpf"),
  observacoes: text("observacoes"),
  patchDownload: text("patch_download"),
  atualizaCria: text("atualiza_cria"),
  status: text("status").notNull().default("ativo"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const execucoes = pgTable("execucoes", {
  id: serial("id").primaryKey(),
  contratoId: integer("contrato_id").references(() => contratos.id),
  sessionId: text("session_id").notNull(),
  status: text("status").notNull().default("pendente"),
  iniciadoEm: timestamp("iniciado_em").defaultNow(),
  finalizadoEm: timestamp("finalizado_em"),
  tempoExecucao: integer("tempo_execucao"),
  logs: jsonb("logs"),
  erro: text("erro"),
  arquivoPath: text("arquivo_path"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const faturas = pgTable("faturas", {
  id: serial("id").primaryKey(),
  execucaoId: integer("execucao_id").references(() => execucoes.id),
  contratoId: integer("contrato_id").references(() => contratos.id),
  valor: decimal("valor", { precision: 10, scale: 2 }),
  dataVencimento: timestamp("data_vencimento"),
  dataCompetencia: text("data_competencia"),
  statusAprovacao: text("status_aprovacao").notNull().default("pendente"),
  aprovadoPor: integer("aprovado_por").references(() => users.id),
  aprovadoEm: timestamp("aprovado_em"),
  motivoRejeicao: text("motivo_rejeicao"),
  arquivoPath: text("arquivo_path"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const notificacoes = pgTable("notificacoes", {
  id: serial("id").primaryKey(),
  tipo: text("tipo").notNull(),
  titulo: text("titulo").notNull(),
  mensagem: text("mensagem").notNull(),
  dados: jsonb("dados"),
  lida: boolean("lida").notNull().default(false),
  userId: integer("user_id").references(() => users.id),
  createdAt: timestamp("created_at").defaultNow(),
});

// Relations
export const clientesRelations = relations(clientes, ({ many }) => ({
  contratos: many(contratos),
}));

export const operadorasRelations = relations(operadoras, ({ many }) => ({
  contratos: many(contratos),
}));

export const contratosRelations = relations(contratos, ({ one, many }) => ({
  cliente: one(clientes, {
    fields: [contratos.clienteId],
    references: [clientes.id],
  }),
  operadora: one(operadoras, {
    fields: [contratos.operadoraId],
    references: [operadoras.id],
  }),
  execucoes: many(execucoes),
  faturas: many(faturas),
}));

export const execucoesRelations = relations(execucoes, ({ one, many }) => ({
  contrato: one(contratos, {
    fields: [execucoes.contratoId],
    references: [contratos.id],
  }),
  faturas: many(faturas),
}));

export const faturasRelations = relations(faturas, ({ one }) => ({
  execucao: one(execucoes, {
    fields: [faturas.execucaoId],
    references: [execucoes.id],
  }),
  contrato: one(contratos, {
    fields: [faturas.contratoId],
    references: [contratos.id],
  }),
  aprovadoPorUser: one(users, {
    fields: [faturas.aprovadoPor],
    references: [users.id],
  }),
}));

export const notificacoesRelations = relations(notificacoes, ({ one }) => ({
  user: one(users, {
    fields: [notificacoes.userId],
    references: [users.id],
  }),
}));

// Insert schemas
export const insertUserSchema = createInsertSchema(users).omit({
  id: true,
  createdAt: true,
});

export const insertOperadoraSchema = createInsertSchema(operadoras).omit({
  id: true,
  createdAt: true,
});

export const insertClienteSchema = createInsertSchema(clientes).omit({
  id: true,
  createdAt: true,
});

export const insertContratoSchema = createInsertSchema(contratos).omit({
  id: true,
  createdAt: true,
});

export const insertExecucaoSchema = createInsertSchema(execucoes).omit({
  id: true,
  createdAt: true,
});

export const insertFaturaSchema = createInsertSchema(faturas).omit({
  id: true,
  createdAt: true,
});

export const insertNotificacaoSchema = createInsertSchema(notificacoes).omit({
  id: true,
  createdAt: true,
});

// Types
export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;

export type InsertOperadora = z.infer<typeof insertOperadoraSchema>;
export type Operadora = typeof operadoras.$inferSelect;

export type InsertCliente = z.infer<typeof insertClienteSchema>;
export type Cliente = typeof clientes.$inferSelect;

export type InsertContrato = z.infer<typeof insertContratoSchema>;
export type Contrato = typeof contratos.$inferSelect;

export type InsertExecucao = z.infer<typeof insertExecucaoSchema>;
export type Execucao = typeof execucoes.$inferSelect;

export type InsertFatura = z.infer<typeof insertFaturaSchema>;
export type Fatura = typeof faturas.$inferSelect;

export type InsertNotificacao = z.infer<typeof insertNotificacaoSchema>;
export type Notificacao = typeof notificacoes.$inferSelect;
