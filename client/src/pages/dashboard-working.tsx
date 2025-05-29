import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Building2, Users, Clock, Activity, CheckCircle, AlertCircle } from "lucide-react";

export default function Dashboard() {
  const { data: metrics, isLoading: loadingMetrics } = useQuery({ 
    queryKey: ["/api/dashboard/metrics"] 
  });
  const { data: execucoes, isLoading: loadingExecucoes } = useQuery({ 
    queryKey: ["/api/execucoes"] 
  });
  const { data: operadoras, isLoading: loadingOperadoras } = useQuery({ 
    queryKey: ["/api/operadoras"] 
  });
  const { data: clientes, isLoading: loadingClientes } = useQuery({ 
    queryKey: ["/api/clientes"] 
  });

  if (loadingMetrics || loadingExecucoes || loadingOperadoras || loadingClientes) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Carregando dashboard...</div>
      </div>
    );
  }

  // Dados das métricas do backend
  const metricsData = metrics || {};
  const execucoesData = Array.isArray(execucoes) ? execucoes : [];
  const operadorasData = Array.isArray(operadoras) ? operadoras : [];
  const clientesData = Array.isArray(clientes) ? clientes : [];

  return (
    <div className="space-y-8 p-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">Visão geral do sistema de orquestração RPA</p>
      </div>

      {/* Métricas principais */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Operadoras</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricsData?.totalOperadoras || operadorasData.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Clientes</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricsData?.totalClientes || clientesData.length}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Processos Pendentes</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricsData?.processosPendentes || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Execuções Ativas</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metricsData?.execucoesAtivas || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Seção de Operadoras */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Operadoras Ativas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {operadorasData.length > 0 ? (
                operadorasData.map((operadora: any) => (
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
                ))
              ) : (
                <p className="text-muted-foreground">Nenhuma operadora encontrada</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Execuções Recentes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {execucoesData.length > 0 ? (
                execucoesData.slice(0, 5).map((execucao: any) => (
                  <div key={execucao.id} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <Activity className="h-4 w-4" />
                      <div>
                        <span className="font-medium">{execucao.nome_sat}</span>
                        <p className="text-sm text-muted-foreground">{execucao.operadora_nome}</p>
                      </div>
                    </div>
                    <Badge variant={execucao.status_ativo ? "default" : "secondary"}>
                      {execucao.status_ativo ? "Ativo" : "Inativo"}
                    </Badge>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground">Nenhuma execução encontrada</p>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Distribuição por Operadora */}
      <Card>
        <CardHeader>
          <CardTitle>Clientes por Operadora</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {operadorasData.map((operadora: any) => {
              const clientesOperadora = clientesData.filter((cliente: any) => 
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
  );
}