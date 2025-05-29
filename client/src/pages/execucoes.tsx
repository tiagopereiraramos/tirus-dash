import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Progress } from "@/components/ui/progress";
import { Play, Square, Eye, RefreshCw, Search } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

export default function Execucoes() {
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [searchTerm, setSearchTerm] = useState("");

  const { data: execucoes, isLoading } = useQuery({
    queryKey: ["/api/execucoes", { page, status: statusFilter, search: searchTerm }],
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "concluido":
        return <Badge className="status-success">Concluído</Badge>;
      case "executando":
        return <Badge className="status-info">Executando</Badge>;
      case "falha":
        return <Badge className="status-error">Falha</Badge>;
      case "pendente":
        return <Badge className="status-warning">Pendente</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getProgress = (status: string, tempoExecucao?: number) => {
    switch (status) {
      case "concluido":
        return 100;
      case "executando":
        return Math.random() * 80 + 10; // Simulando progresso
      case "falha":
        return Math.random() * 50;
      default:
        return 0;
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return "-";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-foreground">Execuções RPA</h2>
        <p className="text-muted-foreground">
          Monitoramento e controle das execuções dos robôs
        </p>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Filtros e Busca
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Buscar por cliente, CNPJ ou operadora..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos os Status</SelectItem>
                <SelectItem value="pendente">Pendente</SelectItem>
                <SelectItem value="executando">Executando</SelectItem>
                <SelectItem value="concluido">Concluído</SelectItem>
                <SelectItem value="falha">Falha</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Atualizar
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Executions Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Execuções Recentes</CardTitle>
            <Button className="btn-primary">
              <Play className="h-4 w-4 mr-2" />
              Nova Execução
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Operadora</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Progresso</TableHead>
                  <TableHead>Iniciado</TableHead>
                  <TableHead>Duração</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {execucoes?.data?.map((execucao: any) => (
                  <TableRow key={execucao.id} className="hover:bg-muted/50">
                    <TableCell>
                      <div>
                        <div className="font-medium text-sm">
                          {execucao.contrato?.cliente?.nomeSat || "Cliente"}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {execucao.contrato?.cliente?.cnpj}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {execucao.contrato?.operadora?.nome || "N/A"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(execucao.status)}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Progress 
                          value={getProgress(execucao.status, execucao.tempoExecucao)} 
                          className="w-16 h-2"
                        />
                        <span className="text-xs text-muted-foreground">
                          {getProgress(execucao.status, execucao.tempoExecucao).toFixed(0)}%
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {execucao.iniciadoEm 
                          ? format(new Date(execucao.iniciadoEm), "dd/MM HH:mm", { locale: ptBR })
                          : "-"
                        }
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {formatDuration(execucao.tempoExecucao)}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        {execucao.status === "executando" && (
                          <Button variant="ghost" size="sm">
                            <Square className="h-4 w-4" />
                          </Button>
                        )}
                        {execucao.status === "falha" && (
                          <Button variant="ghost" size="sm">
                            <RefreshCw className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
