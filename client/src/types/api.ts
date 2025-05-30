// Tipos para as respostas das APIs baseados nos retornos reais dos endpoints

export interface ApiResponse<T> {
  success: boolean;
  data: T;
}

export interface DashboardMetrics {
  totalOperadoras: number;
  totalClientes: number;
  processosPendentes: number;
  execucoesAtivas: number;
}

export interface Operadora {
  id: number;
  nome: string;
  codigo: string;
  possui_rpa: boolean;
  status_ativo: boolean;
}

export interface Cliente {
  id: number;
  nome_sat: string;
  cnpj: string;
  unidade: string;
  operadora_nome: string;
  status_ativo: boolean;
}

export interface Execucao {
  id: number;
  nome_sat: string;
  operadora_nome: string;
  tipo_execucao: string;
  status_execucao: string;
  data_inicio: string;
  tentativas: number;
}

export interface Fatura {
  id: number;
  nome_sat: string;
  operadora_nome: string;
  mes_ano: string;
  valor_fatura: number;
  status_processo: string;
  cnpj?: string;
  unidade?: string;
}

export interface Notificacao {
  id: number;
  tipo: string;
  titulo: string;
  mensagem: string;
  data: string;
  lida: boolean;
}

export interface Aprovacao {
  id: number;
  nome_sat: string;
  operadora_nome: string;
  mes_ano: string;
  valor_fatura: number;
  status_processo: string;
  cnpj?: string;
  unidade?: string;
  status_aprovacao?: string;
}