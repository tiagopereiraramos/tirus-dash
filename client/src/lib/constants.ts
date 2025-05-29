// API endpoints
export const API_ENDPOINTS = {
  DASHBOARD: {
    METRICS: "/api/dashboard/metrics",
  },
  EXECUCOES: {
    LIST: "/api/execucoes",
    CREATE: "/api/execucoes",
    UPDATE_STATUS: (id: number) => `/api/execucoes/${id}/status`,
  },
  FATURAS: {
    LIST: "/api/faturas",
    CREATE: "/api/faturas",
    APROVAR: (id: number) => `/api/faturas/${id}/aprovar`,
    REJEITAR: (id: number) => `/api/faturas/${id}/rejeitar`,
  },
  OPERADORAS: {
    LIST: "/api/operadoras",
    STATUS: "/api/operadoras/status",
    CREATE: "/api/operadoras",
  },
  CLIENTES: {
    LIST: "/api/clientes",
    CREATE: "/api/clientes",
  },
  CONTRATOS: {
    LIST: "/api/contratos",
    CREATE: "/api/contratos",
  },
  NOTIFICACOES: {
    LIST: "/api/notificacoes",
    MARCAR_LIDA: (id: number) => `/api/notificacoes/${id}/marcar-lida`,
  },
  ACOES: {
    EXECUTAR_TODOS_RPAS: "/api/acoes/executar-todos-rpas",
    EXECUTAR_RPA: "/api/acoes/executar-rpa",
  },
  RELATORIOS: {
    EXECUCOES: "/api/relatorios/execucoes",
  },
  INIT: {
    CSV_DATA: "/api/init/csv-data",
  },
} as const;

// Status types
export const STATUS_EXECUCAO = {
  PENDENTE: "pendente",
  EXECUTANDO: "executando",
  CONCLUIDO: "concluido",
  FALHA: "falha",
} as const;

export const STATUS_APROVACAO = {
  PENDENTE: "pendente",
  APROVADA: "aprovada",
  REJEITADA: "rejeitada",
} as const;

export const STATUS_OPERADORA = {
  ATIVO: "ativo",
  INATIVO: "inativo",
  MANUTENCAO: "manutencao",
} as const;

export const STATUS_CLIENTE = {
  ATIVO: "ativo",
  INATIVO: "inativo",
  SUSPENSO: "suspenso",
} as const;

// Operadora configuration
export const OPERADORAS_CONFIG = {
  EMBRATEL: {
    nome: "EMBRATEL",
    codigo: "EMBRATEL",
    cor: "#3366FF",
    sigla: "EM",
  },
  VIVO: {
    nome: "VIVO",
    codigo: "VIVO",
    cor: "#8B5CF6",
    sigla: "VI",
  },
  DIGITALNET: {
    nome: "DIGITALNET",
    codigo: "DIGITALNET",
    cor: "#00D68F",
    sigla: "DN",
  },
  AZUTON: {
    nome: "AZUTON",
    codigo: "AZUTON",
    cor: "#FFAA00",
    sigla: "AZ",
  },
  OI: {
    nome: "OI",
    codigo: "OI",
    cor: "#EF4444",
    sigla: "OI",
  },
} as const;

// Chart colors
export const CHART_COLORS = {
  PRIMARY: "#3366FF",
  SECONDARY: "#00D68F",
  ACCENT: "#FFAA00",
  WARNING: "#EF4444",
  SUCCESS: "#10B981",
  INFO: "#06B6D4",
} as const;

// Pagination defaults
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 20,
  MAX_LIMIT: 100,
} as const;

// WebSocket message types
export const WS_MESSAGE_TYPES = {
  EXECUCAO_CRIADA: "execucao_criada",
  EXECUCAO_ATUALIZADA: "execucao_atualizada",
  EXECUCAO_GERAL_INICIADA: "execucao_geral_iniciada",
  EXECUCAO_RPA_INICIADA: "execucao_rpa_iniciada",
  FATURA_APROVADA: "fatura_aprovada",
  FATURA_REJEITADA: "fatura_rejeitada",
  NOVA_FATURA: "nova_fatura",
  SISTEMA_STATUS: "sistema_status",
} as const;

// Notification types
export const NOTIFICATION_TYPES = {
  SUCCESS: "success",
  ERROR: "error",
  WARNING: "warning",
  INFO: "info",
} as const;

// Date formats
export const DATE_FORMATS = {
  DISPLAY: "dd/MM/yyyy",
  DISPLAY_WITH_TIME: "dd/MM/yyyy HH:mm",
  ISO: "yyyy-MM-dd",
  TIME_ONLY: "HH:mm",
} as const;

// File types
export const ALLOWED_FILE_TYPES = {
  PDF: "application/pdf",
  EXCEL: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  CSV: "text/csv",
} as const;

// RPA Configuration
export const RPA_CONFIG = {
  TIMEOUT_DEFAULT: 30000, // 30 seconds
  RETRY_ATTEMPTS: 3,
  THREAD_POOL_SIZE: 2,
  BATCH_SIZE: 50,
} as const;

// System status
export const SYSTEM_STATUS = {
  ONLINE: "online",
  OFFLINE: "offline",
  MAINTENANCE: "maintenance",
  ERROR: "error",
} as const;

// Service names for system monitoring
export const SERVICES = {
  CELERY_WORKER: "Celery Worker",
  REDIS_QUEUE: "Redis Queue",
  MINIO_STORAGE: "MinIO Storage",
  WEBSOCKET: "WebSocket",
  EMAIL_SERVICE: "Email Service",
  WHATSAPP_API: "WhatsApp API",
  DATABASE: "Database",
} as const;

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: "Erro de conexão. Verifique sua internet.",
  UNAUTHORIZED: "Sessão expirada. Faça login novamente.",
  FORBIDDEN: "Você não tem permissão para esta ação.",
  NOT_FOUND: "Recurso não encontrado.",
  VALIDATION_ERROR: "Dados inválidos. Verifique os campos.",
  SERVER_ERROR: "Erro interno do servidor. Tente novamente.",
  TIMEOUT: "Timeout na operação. Tente novamente.",
} as const;

// Success messages
export const SUCCESS_MESSAGES = {
  EXECUCAO_INICIADA: "Execução iniciada com sucesso",
  FATURA_APROVADA: "Fatura aprovada com sucesso",
  FATURA_REJEITADA: "Fatura rejeitada com sucesso",
  DADOS_SALVOS: "Dados salvos com sucesso",
  OPERACAO_CONCLUIDA: "Operação concluída com sucesso",
} as const;

// LocalStorage keys
export const STORAGE_KEYS = {
  USER_PREFERENCES: "rpa_user_preferences",
  THEME: "rpa_theme",
  DASHBOARD_LAYOUT: "rpa_dashboard_layout",
  FILTERS: "rpa_filters",
} as const;

// Animation durations (in ms)
export const ANIMATION_DURATION = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500,
} as const;

// Breakpoints (matching Tailwind CSS)
export const BREAKPOINTS = {
  SM: 640,
  MD: 768,
  LG: 1024,
  XL: 1280,
  "2XL": 1536,
} as const;

export type StatusExecucao = typeof STATUS_EXECUCAO[keyof typeof STATUS_EXECUCAO];
export type StatusAprovacao = typeof STATUS_APROVACAO[keyof typeof STATUS_APROVACAO];
export type StatusOperadora = typeof STATUS_OPERADORA[keyof typeof STATUS_OPERADORA];
export type StatusCliente = typeof STATUS_CLIENTE[keyof typeof STATUS_CLIENTE];
export type WSMessageType = typeof WS_MESSAGE_TYPES[keyof typeof WS_MESSAGE_TYPES];
export type NotificationType = typeof NOTIFICATION_TYPES[keyof typeof NOTIFICATION_TYPES];
