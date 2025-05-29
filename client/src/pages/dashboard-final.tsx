import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Building2, Users, Clock, Activity, CheckCircle, AlertCircle } from "lucide-react";

interface Metrics {
  totalOperadoras: number;
  totalClientes: number;
  processosPendentes: number;
  execucoesAtivas: number;
}

interface Operadora {
  id: number;
  nome: string;
  codigo: string;
  possui_rpa: boolean;
  status_ativo: boolean;
}

interface Cliente {
  id: number;
  nome_sat: string;
  cnpj: string;
  unidade: string;
  operadora_nome: string;
  status_ativo: boolean;
}

interface Execucao {
  id: number;
  nome_sat: string;
  cnpj: string;
  operadora_nome: string;
  unidade: string;
  status_ativo: boolean;
}

export default function Dashboard() {
  const { data: metrics, isLoading: loadingMetrics } = useQuery<Metrics>({ 
    queryKey: ["/api/dashboard/metrics"] 
  });
  const { data: execucoes, isLoading: loadingExecucoes } = useQuery<Execucao[]>({ 
    queryKey: ["/api/execucoes"] 
  });
  const { data: operadoras, isLoading: loadingOperadoras } = useQuery<Operadora[]>({ 
    queryKey: ["/api/operadoras"] 
  });
  const { data: clientes, isLoading: loadingClientes } = useQuery<Cliente[]>({ 
    queryKey: ["/api/clientes"] 
  });

  if (loadingMetrics || loadingExecucoes || loadingOperadoras || loadingClientes) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Carregando dashboard...</div>
      </div>
    );
  }

  const metricsData = metrics || { totalOperadoras: 0, totalClientes: 0, processosPendentes: 0, execucoesAtivas: 0 };
  const execucoesData = execucoes || [];
  const operadorasData = operadoras || [];
  const clientesData = clientes || [];

  return (
    <div className="space-y-8 p-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Visão geral do sistema de orquestração RPA - BGTELECOM</p>
      </div>

      {/* Métricas principais */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Operadoras</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricsData.totalOperadoras}</div>
            <p className="text-xs text-muted-foreground">
              {operadorasData.filter(op => op.status_ativo).length} ativas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Clientes</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricsData.totalClientes}</div>
            <p className="text-xs text-muted-foreground">
              {clientesData.filter(cl => cl.status_ativo).length} ativos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Processos Pendentes</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricsData.processosPendentes}</div>
            <p className="text-xs text-muted-foreground">Aguardando aprovação</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Execuções Ativas</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricsData.execucoesAtivas}</div>
            <p className="text-xs text-muted-foreground">RPAs em execução</p>
          </CardContent>
        </Card>
      </div>

      {/* Seção de Operadoras */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Operadoras Disponíveis</CardTitle>
            <p className="text-sm text-muted-foreground">
              {operadorasData.length} operadoras configuradas
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {operadorasData.slice(0, 6).map((operadora) => (
                <div key={operadora.id} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <Building2 className="h-4 w-4" />
                    <span className="font-medium">{operadora.nome}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    {operadora.possui_rpa && (
                      <Badge variant="secondary">RPA</Badge>
                    )}
                    {operadora.status_ativo ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-red-500" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Clientes por Operadora</CardTitle>
            <p className="text-sm text-muted-foreground">
              Distribuição dos {clientesData.length} clientes
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {operadorasData.map((operadora) => {
                const clientesOperadora = clientesData.filter((cliente) => 
                  cliente.operadora_nome === operadora.nome
                );
                
                return (
                  <div key={operadora.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Building2 className="h-4 w-4" />
                      <span className="font-medium">{operadora.nome}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-sm text-muted-foreground">
                        {clientesOperadora.length} clientes
                      </span>
                      <Badge variant="outline">
                        {operadora.codigo}
                      </Badge>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Lista de Clientes Principais */}
      <Card>
        <CardHeader>
          <CardTitle>Clientes Ativos</CardTitle>
          <p className="text-sm text-muted-foreground">
            Principais clientes da BGTELECOM
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {clientesData.slice(0, 8).map((cliente) => (
              <div key={cliente.id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-start space-x-3">
                  <Users className="h-5 w-5 mt-0.5" />
                  <div>
                    <p className="font-medium">{cliente.nome_sat}</p>
                    <p className="text-sm text-muted-foreground">
                      CNPJ: {cliente.cnpj} • {cliente.unidade}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <Badge variant="outline">{cliente.operadora_nome}</Badge>
                  <Badge variant={cliente.status_ativo ? "default" : "secondary"}>
                    {cliente.status_ativo ? "Ativo" : "Inativo"}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}