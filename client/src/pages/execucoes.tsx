import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  Eye, 
  Download,
  Activity,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Filter
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

type Execucao = {
  id: number;
  processo_nome: string;
  operadora_nome: string;
  cliente_nome: string;
  tipo: string;
  status: "executando" | "concluido" | "erro" | "cancelado" | "agendado";
  progresso: number;
  inicio: string;
  fim?: string;
  duracao?: string;
  detalhes: string;
  logs_url?: string;
  resultado?: {
    faturas_processadas?: number;
    arquivos_baixados?: number;
    erros_encontrados?: number;
  };
};

export default function Execucoes() {
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterOperadora, setFilterOperadora] = useState<string>("all");
  const { toast } = useToast();

  // Query para buscar execuções
  const { data: execucoes = [], isLoading, refetch } = useQuery({
    queryKey: ["/api/execucoes"],
    refetchInterval: 5000, // Auto-refresh a cada 5 segundos
  });

  // Filtrar execuções
  const execucoesFiltradas = execucoes.filter((exec: Execucao) => {
    const passaStatus = filterStatus === "all" || exec.status === filterStatus;
    const passaOperadora = filterOperadora === "all" || exec.operadora_nome === filterOperadora;
    return passaStatus && passaOperadora;
  });

  // Mutations para controle de execução
  const pararMutation = useMutation({
    mutationFn: (id: number) =>
      apiRequest(`/api/execucoes/${id}/parar`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/execucoes"] });
      toast({
        title: "Sucesso",
        description: "Execução interrompida",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao parar execução",
        variant: "destructive",
      });
    },
  });

  const reexecutarMutation = useMutation({
    mutationFn: (id: number) =>
      apiRequest(`/api/execucoes/${id}/reexecutar`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/execucoes"] });
      toast({
        title: "Sucesso",
        description: "Processo reexecutado com sucesso",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao reexecutar processo",
        variant: "destructive",
      });
    },
  });

  // Handlers
  const handleParar = (id: number) => {
    if (confirm("Tem certeza que deseja parar esta execução?")) {
      pararMutation.mutate(id);
    }
  };

  const handleReexecutar = (id: number) => {
    if (confirm("Tem certeza que deseja reexecutar este processo?")) {
      reexecutarMutation.mutate(id);
    }
  };

  const getStatusBadge = (status: string) => {
    const config = {
      executando: { 
        variant: "default" as const, 
        className: "bg-blue-100 text-blue-700 border-blue-200",
        icon: <Activity className="h-3 w-3 mr-1 animate-pulse" />
      },
      concluido: { 
        variant: "default" as const, 
        className: "bg-green-100 text-green-700 border-green-200",
        icon: <CheckCircle className="h-3 w-3 mr-1" />
      },
      erro: { 
        variant: "destructive" as const, 
        className: "bg-red-100 text-red-700 border-red-200",
        icon: <XCircle className="h-3 w-3 mr-1" />
      },
      cancelado: { 
        variant: "secondary" as const, 
        className: "bg-gray-100 text-gray-700 border-gray-200",
        icon: <Square className="h-3 w-3 mr-1" />
      },
      agendado: { 
        variant: "secondary" as const, 
        className: "bg-yellow-100 text-yellow-700 border-yellow-200",
        icon: <Clock className="h-3 w-3 mr-1" />
      },
    };
    
    const badgeConfig = config[status as keyof typeof config] || config.agendado;
    return (
      <Badge variant={badgeConfig.variant} className={badgeConfig.className}>
        {badgeConfig.icon}
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const formatDuracao = (inicio: string, fim?: string) => {
    const inicioDate = new Date(inicio);
    const fimDate = fim ? new Date(fim) : new Date();
    const diffMs = fimDate.getTime() - inicioDate.getTime();
    const diffMinutes = Math.floor(diffMs / 60000);
    const diffSeconds = Math.floor((diffMs % 60000) / 1000);
    
    if (diffMinutes > 0) {
      return `${diffMinutes}m ${diffSeconds}s`;
    }
    return `${diffSeconds}s`;
  };

  return (
    <div className="p-6 space-y-6 bg-slate-50 min-h-screen">
      {/* Header com gradiente indigo */}
      <div className="bg-gradient-to-r from-indigo-500 to-indigo-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Execuções</h1>
            <p className="text-indigo-100 mt-2">Monitore e controle as execuções dos processos RPA em tempo real</p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              onClick={() => refetch()}
              className="bg-white text-indigo-600 hover:bg-indigo-50 font-semibold"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Atualizar
            </Button>
          </div>
        </div>
      </div>

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-indigo-500 to-indigo-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">{execucoes.length}</div>
            <div className="text-sm text-indigo-100 mt-1">Total de Execuções</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-500 to-blue-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {execucoes.filter((e: Execucao) => e.status === "executando").length}
            </div>
            <div className="text-sm text-blue-100 mt-1">Em Execução</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-500 to-green-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {execucoes.filter((e: Execucao) => e.status === "concluido").length}
            </div>
            <div className="text-sm text-green-100 mt-1">Concluídas</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-red-500 to-red-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {execucoes.filter((e: Execucao) => e.status === "erro").length}
            </div>
            <div className="text-sm text-red-100 mt-1">Com Erro</div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card className="border-0 shadow-lg bg-white">
        <CardContent className="p-4">
          <div className="flex items-center gap-4 flex-wrap">
            <Filter className="h-5 w-5 text-slate-600" />
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Status:</span>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  <SelectItem value="executando">Executando</SelectItem>
                  <SelectItem value="concluido">Concluídas</SelectItem>
                  <SelectItem value="erro">Com Erro</SelectItem>
                  <SelectItem value="cancelado">Canceladas</SelectItem>
                  <SelectItem value="agendado">Agendadas</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Operadora:</span>
              <Select value={filterOperadora} onValueChange={setFilterOperadora}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todas</SelectItem>
                  <SelectItem value="EMBRATEL">EMBRATEL</SelectItem>
                  <SelectItem value="VIVO">VIVO</SelectItem>
                  <SelectItem value="OI">OI</SelectItem>
                  <SelectItem value="AZUTON">AZUTON</SelectItem>
                  <SelectItem value="DIGITALNET">DIGITALNET</SelectItem>
                  <SelectItem value="SAT">SAT</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de execuções */}
      <Card className="border-0 shadow-lg bg-white">
        <CardHeader className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-lg">
          <CardTitle className="flex items-center text-slate-800">
            <Activity className="h-5 w-5 mr-2 text-indigo-600" />
            Histórico de Execuções ({execucoesFiltradas.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Processo</TableHead>
                  <TableHead>Operadora</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Progresso</TableHead>
                  <TableHead>Duração</TableHead>
                  <TableHead>Resultado</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {execucoesFiltradas.length > 0 ? execucoesFiltradas.map((execucao: Execucao) => (
                  <TableRow key={execucao.id} className="hover:bg-slate-50/50 transition-colors">
                    <TableCell className="font-medium text-slate-600">#{execucao.id}</TableCell>
                    <TableCell className="font-semibold text-slate-900 max-w-xs truncate">
                      {execucao.processo_nome}
                    </TableCell>
                    <TableCell className="text-sm text-slate-600">{execucao.operadora_nome}</TableCell>
                    <TableCell className="text-sm text-slate-600">{execucao.cliente_nome}</TableCell>
                    <TableCell>{getStatusBadge(execucao.status)}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2 min-w-24">
                        <Progress value={execucao.progresso} className="h-2 flex-1" />
                        <span className="text-xs font-medium w-8">{execucao.progresso}%</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-slate-600">
                      {formatDuracao(execucao.inicio, execucao.fim)}
                    </TableCell>
                    <TableCell className="text-sm">
                      {execucao.resultado && (
                        <div className="space-y-1">
                          {execucao.resultado.faturas_processadas && (
                            <div className="text-green-600">✓ {execucao.resultado.faturas_processadas} faturas</div>
                          )}
                          {execucao.resultado.erros_encontrados && execucao.resultado.erros_encontrados > 0 && (
                            <div className="text-red-600">✗ {execucao.resultado.erros_encontrados} erros</div>
                          )}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-1">
                        {execucao.status === "executando" && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleParar(execucao.id)}
                            disabled={pararMutation.isPending}
                            className="h-8 px-2 text-red-600 border-red-200 hover:bg-red-50"
                          >
                            <Square className="h-3 w-3" />
                          </Button>
                        )}
                        
                        {(execucao.status === "erro" || execucao.status === "cancelado") && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleReexecutar(execucao.id)}
                            disabled={reexecutarMutation.isPending}
                            className="h-8 px-2 text-blue-600 border-blue-200 hover:bg-blue-50"
                          >
                            <RotateCcw className="h-3 w-3" />
                          </Button>
                        )}

                        <Button
                          variant="outline"
                          size="sm"
                          className="h-8 px-2 text-slate-600 border-slate-200 hover:bg-slate-50"
                        >
                          <Eye className="h-3 w-3" />
                        </Button>

                        {execucao.logs_url && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="h-8 px-2 text-slate-600 border-slate-200 hover:bg-slate-50"
                          >
                            <Download className="h-3 w-3" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-slate-500">
                      Nenhuma execução encontrada com os filtros atuais
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}