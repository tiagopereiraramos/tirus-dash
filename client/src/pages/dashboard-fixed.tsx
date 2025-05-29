import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Play, Activity, Users, Building2, Clock, CheckCircle } from "lucide-react";

export default function Dashboard() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ["/api/dashboard/metrics"],
  });

  const { data: execucoes } = useQuery({
    queryKey: ["/api/execucoes"],
  });

  const { data: operadoras } = useQuery({
    queryKey: ["/api/operadoras"],
  });

  const { data: clientes } = useQuery({
    queryKey: ["/api/clientes"],
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const metricsData = metrics || { totalOperadoras: 0, totalClientes: 0, processosPendentes: 0, execucoesAtivas: 0 };
  const execucoesData = Array.isArray(execucoes) ? execucoes : [];
  const operadorasData = Array.isArray(operadoras) ? operadoras : [];
  const clientesData = Array.isArray(clientes) ? clientes : [];

  return (
    <div className="space-y-8 p-8">
      <div>
        <h1 className="text-3xl font-bold">Dashboard RPA BGTELECOM</h1>
        <p className="text-muted-foreground">Sistema de Orquestração e Monitoramento</p>
      </div>

      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Operadoras</p>
                <p className="text-2xl font-bold">{metricsData.totalOperadoras || 0}</p>
              </div>
              <Building2 className="h-8 w-8 text-primary" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Clientes</p>
                <p className="text-2xl font-bold">{metricsData.totalClientes || 0}</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Processos Pendentes</p>
                <p className="text-2xl font-bold">{metricsData.processosPendentes || 0}</p>
              </div>
              <Clock className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Execuções Ativas</p>
                <p className="text-2xl font-bold">{metricsData.execucoesAtivas || 0}</p>
              </div>
              <Activity className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Execuções Recentes */}
      <Card>
        <CardHeader>
          <CardTitle>Execuções RPA em Tempo Real</CardTitle>
          <CardDescription>Monitoramento das operações automatizadas</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {execucoesData.length > 0 ? (
              execucoesData.map((execucao: any) => (
                <div
                  key={execucao.id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      execucao.status_execucao === 'EXECUTANDO' ? 'bg-yellow-500 animate-pulse' :
                      execucao.status_execucao === 'CONCLUIDO' ? 'bg-green-500' : 'bg-red-500'
                    }`} />
                    <div>
                      <p className="font-medium">{execucao.nome_sat}</p>
                      <p className="text-sm text-muted-foreground">
                        {execucao.operadora_nome} - {execucao.tipo_execucao}
                      </p>
                    </div>
                  </div>
                  <Badge variant={
                    execucao.status_execucao === 'EXECUTANDO' ? 'default' :
                    execucao.status_execucao === 'CONCLUIDO' ? 'secondary' : 'destructive'
                  }>
                    {execucao.status_execucao}
                  </Badge>
                </div>
              ))
            ) : (
              <p className="text-muted-foreground text-center py-4">
                Nenhuma execução em andamento
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Operadoras Ativas */}
      <Card>
        <CardHeader>
          <CardTitle>Operadoras Disponíveis</CardTitle>
          <CardDescription>Status das operadoras integradas ao sistema</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {operadorasData.map((operadora: any) => (
              <div key={operadora.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <p className="font-medium">{operadora.nome}</p>
                  <p className="text-sm text-muted-foreground">
                    {operadora.possui_rpa ? 'RPA Disponível' : 'RPA Indisponível'}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  {operadora.possui_rpa && (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  )}
                  <Badge variant={operadora.status_ativo ? 'secondary' : 'outline'}>
                    {operadora.status_ativo ? 'Ativo' : 'Inativo'}
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