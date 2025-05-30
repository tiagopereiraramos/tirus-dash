import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
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
  Activity, 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  RefreshCw,
  Monitor,
  BarChart3
} from "lucide-react";

type LogEntry = {
  id: number;
  timestamp: string;
  nivel: string;
  operadora: string;
  processo: string;
  mensagem: string;
  detalhes?: string;
};

type Metrica = {
  nome: string;
  valor: number;
  unidade: string;
  tendencia: "up" | "down" | "stable";
  percentual_mudanca: number;
};

export default function Monitoramento() {
  const [filterNivel, setFilterNivel] = useState<string>("all");
  const [filterOperadora, setFilterOperadora] = useState<string>("all");
  const [autoRefresh, setAutoRefresh] = useState(false);

  // Query para buscar logs do sistema
  const { data: logs = [], isLoading: logsLoading, refetch: refetchLogs } = useQuery({
    queryKey: ["/api/logs"],
    refetchInterval: autoRefresh ? 5000 : false,
  });

  // Query para buscar métricas do sistema
  const { data: metricas = [], isLoading: metricasLoading, refetch: refetchMetricas } = useQuery({
    queryKey: ["/api/metricas"],
    refetchInterval: autoRefresh ? 10000 : false,
  });

  // Query para buscar status dos processos
  const { data: statusProcessos = [], isLoading: statusLoading } = useQuery({
    queryKey: ["/api/processos/status"],
    refetchInterval: autoRefresh ? 3000 : false,
  });

  // Filtrar logs
  const logsFiltrados = logs.filter((log: LogEntry) => {
    const passaNivel = filterNivel === "all" || log.nivel === filterNivel;
    const passaOperadora = filterOperadora === "all" || log.operadora === filterOperadora;
    return passaNivel && passaOperadora;
  });

  const handleRefresh = () => {
    refetchLogs();
    refetchMetricas();
  };

  const getNivelBadge = (nivel: string) => {
    const config = {
      INFO: { variant: "default" as const, className: "bg-blue-100 text-blue-700 border-blue-200" },
      SUCCESS: { variant: "default" as const, className: "bg-green-100 text-green-700 border-green-200" },
      WARNING: { variant: "secondary" as const, className: "bg-yellow-100 text-yellow-700 border-yellow-200" },
      ERROR: { variant: "destructive" as const, className: "bg-red-100 text-red-700 border-red-200" },
    };
    
    const badgeConfig = config[nivel as keyof typeof config] || config.INFO;
    return (
      <Badge variant={badgeConfig.variant} className={badgeConfig.className}>
        {nivel}
      </Badge>
    );
  };

  const getTendenciaIcon = (tendencia: string) => {
    switch (tendencia) {
      case "up":
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case "down":
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <BarChart3 className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "executando":
        return <Activity className="h-4 w-4 text-blue-600 animate-pulse" />;
      case "concluido":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "erro":
        return <XCircle className="h-4 w-4 text-red-600" />;
      case "agendado":
        return <Clock className="h-4 w-4 text-yellow-600" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className="p-6 space-y-6 bg-slate-50 min-h-screen">
      {/* Header com gradiente laranja */}
      <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Monitoramento</h1>
            <p className="text-orange-100 mt-2">Acompanhe o desempenho e logs do sistema RPA em tempo real</p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              onClick={() => setAutoRefresh(!autoRefresh)}
              variant={autoRefresh ? "default" : "outline"}
              className={autoRefresh 
                ? "bg-green-600 hover:bg-green-700" 
                : "bg-white text-orange-600 hover:bg-orange-50"
              }
            >
              <Monitor className="h-4 w-4 mr-2" />
              {autoRefresh ? "Auto-refresh ON" : "Auto-refresh OFF"}
            </Button>
            <Button 
              onClick={handleRefresh}
              className="bg-white text-orange-600 hover:bg-orange-50 font-semibold"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Atualizar
            </Button>
          </div>
        </div>
      </div>

      {/* Métricas principais */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {metricasLoading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <Card key={i} className="border-0 shadow-lg">
              <CardContent className="p-6">
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-1/2"></div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          metricas.slice(0, 4).map((metrica: Metrica, index: number) => {
            const cores = [
              "from-orange-500 to-orange-600",
              "from-blue-500 to-blue-600", 
              "from-green-500 to-green-600",
              "from-purple-500 to-purple-600"
            ];
            return (
              <Card key={index} className={`border-0 shadow-lg bg-gradient-to-br ${cores[index]}`}>
                <CardContent className="p-6 text-center">
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-sm text-white opacity-90">{metrica.nome}</div>
                    {getTendenciaIcon(metrica.tendencia)}
                  </div>
                  <div className="text-3xl font-bold text-white">
                    {metrica.valor} {metrica.unidade}
                  </div>
                  <div className="text-sm text-white opacity-75 mt-1">
                    {metrica.percentual_mudanca > 0 ? "+" : ""}{metrica.percentual_mudanca}% vs. anterior
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>

      {/* Status dos Processos */}
      <Card className="border-0 shadow-lg bg-white">
        <CardHeader className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-lg">
          <CardTitle className="flex items-center text-slate-800">
            <Activity className="h-5 w-5 mr-2 text-orange-600" />
            Status dos Processos em Tempo Real
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          {statusLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {statusProcessos.map((processo: any) => (
                <Card key={processo.id} className="border border-slate-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-sm">{processo.nome}</h4>
                      {getStatusIcon(processo.status)}
                    </div>
                    <div className="text-xs text-slate-600 mb-2">{processo.operadora}</div>
                    <Progress value={processo.progresso || 0} className="h-2 mb-2" />
                    <div className="text-xs text-slate-500">
                      {processo.ultima_atualizacao ? 
                        `Atualizado: ${new Date(processo.ultima_atualizacao).toLocaleTimeString('pt-BR')}` :
                        "Aguardando execução"
                      }
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Filtros para logs */}
      <Card className="border-0 shadow-lg bg-white">
        <CardContent className="p-4">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-slate-600" />
              <span className="font-medium">Filtros:</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm">Nível:</span>
              <Select value={filterNivel} onValueChange={setFilterNivel}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Todos</SelectItem>
                  <SelectItem value="INFO">Info</SelectItem>
                  <SelectItem value="SUCCESS">Sucesso</SelectItem>
                  <SelectItem value="WARNING">Aviso</SelectItem>
                  <SelectItem value="ERROR">Erro</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm">Operadora:</span>
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

      {/* Logs do sistema */}
      <Card className="border-0 shadow-lg bg-white">
        <CardHeader className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-lg">
          <CardTitle className="flex items-center text-slate-800">
            <Monitor className="h-5 w-5 mr-2 text-orange-600" />
            Logs do Sistema ({logsFiltrados.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {logsLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
            </div>
          ) : (
            <div className="max-h-96 overflow-y-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Nível</TableHead>
                    <TableHead>Operadora</TableHead>
                    <TableHead>Processo</TableHead>
                    <TableHead>Mensagem</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {logsFiltrados.length > 0 ? logsFiltrados.map((log: LogEntry) => (
                    <TableRow key={log.id} className="hover:bg-slate-50/50 transition-colors">
                      <TableCell className="text-sm text-slate-600">
                        {new Date(log.timestamp).toLocaleString('pt-BR')}
                      </TableCell>
                      <TableCell>{getNivelBadge(log.nivel)}</TableCell>
                      <TableCell className="text-sm text-slate-600">{log.operadora}</TableCell>
                      <TableCell className="text-sm text-slate-600">{log.processo}</TableCell>
                      <TableCell className="text-sm text-slate-900 max-w-md truncate">
                        {log.mensagem}
                      </TableCell>
                    </TableRow>
                  )) : (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-slate-500">
                        Nenhum log encontrado com os filtros atuais
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}