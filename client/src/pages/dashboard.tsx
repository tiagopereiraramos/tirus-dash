import { useQuery } from "@tanstack/react-query";
import MetricsCards from "@/components/dashboard/metrics-cards";
import ExecutionChart from "@/components/charts/execution-chart";
import RecentExecutions from "@/components/dashboard/recent-executions";
import PendingApprovals from "@/components/dashboard/pending-approvals";
import OperatorStatus from "@/components/dashboard/operator-status";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Play, SquareCheck, Download, Activity } from "lucide-react";
import { useWebSocket } from "@/lib/websocket";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";

export default function Dashboard() {
  const { toast } = useToast();
  const { lastMessage } = useWebSocket();

  const { data: metrics, refetch: refetchMetrics } = useQuery({
    queryKey: ["/api/dashboard/metrics"],
  });

  // Handle WebSocket messages
  if (lastMessage) {
    const message = lastMessage;
    switch (message.type) {
      case "execucao_criada":
        toast({
          title: "Nova Execução Iniciada",
          description: `RPA iniciado para ${message.data.contrato?.cliente?.nomeSat || 'cliente'}`,
        });
        refetchMetrics();
        break;
      case "execucao_atualizada":
        if (message.data.status === "concluido") {
          toast({
            title: "Execução Concluída",
            description: `RPA finalizado com sucesso`,
          });
        } else if (message.data.status === "falha") {
          toast({
            title: "Execução Falhou",
            description: `Erro na execução: ${message.data.erro}`,
            variant: "destructive",
          });
        }
        refetchMetrics();
        break;
      case "fatura_aprovada":
        toast({
          title: "Fatura Aprovada",
          description: "Fatura aprovada e seguirá para pagamento",
        });
        refetchMetrics();
        break;
    }
  }

  const handleExecuteAllRPAs = async () => {
    try {
      await apiRequest("POST", "/api/acoes/executar-todos-rpas");
      toast({
        title: "Execução Geral Iniciada",
        description: "Todos os RPAs foram colocados na fila de execução",
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Falha ao iniciar execução geral",
        variant: "destructive",
      });
    }
  };

  const handleExportReport = async () => {
    try {
      const response = await apiRequest("GET", "/api/relatorios/execucoes");
      toast({
        title: "Relatório Gerado",
        description: "Relatório de execuções baixado com sucesso",
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Falha ao gerar relatório",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-foreground">Dashboard de Processos</h2>
        <p className="text-muted-foreground">
          Visão geral das execuções e métricas do sistema RPA
        </p>
      </div>

      {/* Metrics Cards */}
      <MetricsCards metrics={metrics} />

      {/* Charts and Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Execution Chart */}
        <div className="lg:col-span-2">
          <ExecutionChart />
        </div>

        {/* Operator Status */}
        <div className="lg:col-span-1">
          <OperatorStatus />
        </div>
      </div>

      {/* Recent Executions and Pending Approvals */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentExecutions />
        <PendingApprovals />
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Ações Rápidas
          </CardTitle>
          <CardDescription>
            Execute operações comuns do sistema RPA
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Button
              onClick={handleExecuteAllRPAs}
              className="h-auto p-4 flex flex-col items-start space-y-2"
              variant="outline"
            >
              <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                <Play className="h-5 w-5 text-primary" />
              </div>
              <div className="text-left">
                <p className="font-medium">Executar Todos os RPAs</p>
                <p className="text-xs text-muted-foreground">
                  Inicia execução para todas as operadoras
                </p>
              </div>
            </Button>

            <Button
              className="h-auto p-4 flex flex-col items-start space-y-2"
              variant="outline"
            >
              <div className="w-10 h-10 bg-secondary/10 rounded-lg flex items-center justify-center">
                <SquareCheck className="h-5 w-5 text-secondary" />
              </div>
              <div className="text-left">
                <p className="font-medium">Aprovação em Lote</p>
                <p className="text-xs text-muted-foreground">
                  Aprovar múltiplas faturas
                </p>
              </div>
            </Button>

            <Button
              onClick={handleExportReport}
              className="h-auto p-4 flex flex-col items-start space-y-2"
              variant="outline"
            >
              <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                <Download className="h-5 w-5 text-accent" />
              </div>
              <div className="text-left">
                <p className="font-medium">Exportar Relatório</p>
                <p className="text-xs text-muted-foreground">
                  Baixar dados em Excel
                </p>
              </div>
            </Button>

            <Button
              className="h-auto p-4 flex flex-col items-start space-y-2"
              variant="outline"
            >
              <div className="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center">
                <Activity className="h-5 w-5 text-purple-500" />
              </div>
              <div className="text-left">
                <p className="font-medium">Status do Sistema</p>
                <p className="text-xs text-muted-foreground">
                  Verificar saúde dos RPAs
                </p>
              </div>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle>Status dos Serviços</CardTitle>
          <CardDescription>
            Monitoramento em tempo real dos componentes do sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-secondary rounded-full animate-pulse-soft"></div>
                <span className="text-sm font-medium">Celery Worker</span>
              </div>
              <Badge variant="outline" className="text-secondary border-secondary">
                Online
              </Badge>
            </div>

            <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-secondary rounded-full animate-pulse-soft"></div>
                <span className="text-sm font-medium">Redis Queue</span>
              </div>
              <Badge variant="outline" className="text-secondary border-secondary">
                5 jobs na fila
              </Badge>
            </div>

            <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-secondary rounded-full animate-pulse-soft"></div>
                <span className="text-sm font-medium">MinIO Storage</span>
              </div>
              <Badge variant="outline" className="text-secondary border-secondary">
                78% disponível
              </Badge>
            </div>

            <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-primary rounded-full animate-pulse-soft"></div>
                <span className="text-sm font-medium">WebSocket</span>
              </div>
              <Badge variant="outline" className="text-primary border-primary">
                Conectado
              </Badge>
            </div>

            <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-secondary rounded-full animate-pulse-soft"></div>
                <span className="text-sm font-medium">Email Service</span>
              </div>
              <Badge variant="outline" className="text-secondary border-secondary">
                Operacional
              </Badge>
            </div>

            <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 bg-secondary rounded-full animate-pulse-soft"></div>
                <span className="text-sm font-medium">WhatsApp API</span>
              </div>
              <Badge variant="outline" className="text-secondary border-secondary">
                Conectado
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
