import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Users, Building2, Clock, CheckCircle, PlayCircle, AlertTriangle } from "lucide-react";

interface DashboardMetrics {
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

interface Execucao {
  id: number;
  nome_sat: string;
  operadora_nome: string;
  tipo_execucao: string;
  status_execucao: string;
  data_inicio: string;
  tentativas: number;
}

export default function Dashboard() {
  const { data: metricas, isLoading: loadingMetricas } = useQuery<DashboardMetrics>({
    queryKey: ["/api/dashboard/metrics"]
  });

  const { data: operadoras, isLoading: loadingOperadoras } = useQuery<Operadora[]>({
    queryKey: ["/api/operadoras"]
  });

  const { data: execucoes, isLoading: loadingExecucoes } = useQuery<Execucao[]>({
    queryKey: ["/api/execucoes"]
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "EXECUTANDO": return "bg-blue-100 text-blue-800";
      case "CONCLUIDO": return "bg-green-100 text-green-800";
      case "FALHOU": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "EXECUTANDO": return <PlayCircle className="h-4 w-4" />;
      case "CONCLUIDO": return <CheckCircle className="h-4 w-4" />;
      case "FALHOU": return <AlertTriangle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  if (loadingMetricas || loadingOperadoras || loadingExecucoes) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Carregando dashboard...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Visão geral do sistema de orquestração RPA
          </p>
        </div>
      </div>

      {/* Cards de métricas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Building2 className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Operadoras</p>
                <p className="text-2xl font-bold">{metricas?.totalOperadoras || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Clientes</p>
                <p className="text-2xl font-bold">{metricas?.totalClientes || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Pendentes</p>
                <p className="text-2xl font-bold">{metricas?.processosPendentes || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <PlayCircle className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Executando</p>
                <p className="text-2xl font-bold">{metricas?.execucoesAtivas || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Lista de Operadoras */}
      <Card>
        <CardHeader>
          <CardTitle>Operadoras ({(operadoras || []).length})</CardTitle>
          <CardDescription>
            Status das operadoras do sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {(operadoras || []).map((operadora) => (
              <div key={operadora.id} className="flex items-center space-x-2 p-3 border rounded-lg">
                <div className={`w-3 h-3 rounded-full ${operadora.status_ativo ? 'bg-green-500' : 'bg-red-500'}`} />
                <div>
                  <div className="font-medium">{operadora.nome}</div>
                  <div className="text-sm text-muted-foreground">
                    {operadora.possui_rpa ? 'RPA Ativo' : 'RPA Inativo'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Execuções Recentes */}
      <Card>
        <CardHeader>
          <CardTitle>Execuções Recentes ({(execucoes || []).length})</CardTitle>
          <CardDescription>
            Últimas execuções dos RPAs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cliente</TableHead>
                <TableHead>Operadora</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Data/Hora</TableHead>
                <TableHead>Tentativas</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {(execucoes || []).map((execucao) => (
                <TableRow key={execucao.id}>
                  <TableCell>{execucao.nome_sat}</TableCell>
                  <TableCell>{execucao.operadora_nome}</TableCell>
                  <TableCell>{execucao.tipo_execucao}</TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(execucao.status_execucao)}>
                      <div className="flex items-center gap-1">
                        {getStatusIcon(execucao.status_execucao)}
                        {execucao.status_execucao}
                      </div>
                    </Badge>
                  </TableCell>
                  <TableCell>{new Date(execucao.data_inicio).toLocaleString('pt-BR')}</TableCell>
                  <TableCell>{execucao.tentativas}</TableCell>
                </TableRow>
              ))}
              {(!execucoes || execucoes.length === 0) && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                    Nenhuma execução encontrada
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}