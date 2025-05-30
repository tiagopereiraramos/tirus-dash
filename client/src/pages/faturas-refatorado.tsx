import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Download, Clock, CheckCircle, XCircle, AlertTriangle, Search, Filter } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

interface Fatura {
  id: number;
  cliente: string;
  operadora: string;
  valor: number;
  vencimento: string;
  status: string;
  observacoes?: string;
}

interface Operadora {
  id: number;
  nome: string;
  codigo: string;
  possui_rpa: boolean;
  status_ativo: boolean;
}

export default function Faturas() {
  const { toast } = useToast();
  const [filtroOperadora, setFiltroOperadora] = useState<string>("");
  const [filtroStatus, setFiltroStatus] = useState<string>("");
  const [busca, setBusca] = useState<string>("");

  const { data: faturasResponse, isLoading: loadingFaturas } = useQuery({ 
    queryKey: ["/api/faturas"] 
  });

  const { data: operadorasResponse, isLoading: loadingOperadoras } = useQuery({ 
    queryKey: ["/api/operadoras"] 
  });

  const downloadMutation = useMutation({
    mutationFn: (faturaId: number) => 
      apiRequest(`/api/faturas/${faturaId}/download`, { method: "POST" }),
    onSuccess: () => {
      toast({
        title: "Download iniciado",
        description: "O download da fatura foi iniciado com sucesso.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
    },
    onError: () => {
      toast({
        title: "Erro no download",
        description: "Ocorreu um erro ao iniciar o download da fatura.",
        variant: "destructive",
      });
    },
  });

  const faturas = Array.isArray(faturasResponse) ? faturasResponse : [];
  const operadoras = Array.isArray(operadorasResponse) ? operadorasResponse : [];

  const faturasFiltradas = faturas.filter((fatura) => {
    const matchOperadora = !filtroOperadora || filtroOperadora === "todas" || fatura.operadora === filtroOperadora;
    const matchStatus = !filtroStatus || filtroStatus === "todos" || fatura.status === filtroStatus;
    const matchBusca = !busca || 
      fatura.cliente.toLowerCase().includes(busca.toLowerCase()) ||
      fatura.operadora.toLowerCase().includes(busca.toLowerCase());
    
    return matchOperadora && matchStatus && matchBusca;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "pendente": return "bg-yellow-100 text-yellow-800";
      case "aprovada": return "bg-green-100 text-green-800";
      case "processando": return "bg-blue-100 text-blue-800";
      case "rejeitada": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "pendente": return <Clock className="h-4 w-4" />;
      case "aprovada": return <CheckCircle className="h-4 w-4" />;
      case "processando": return <AlertTriangle className="h-4 w-4" />;
      case "rejeitada": return <XCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  if (loadingFaturas) {
    return (
      <div className="container mx-auto p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-20 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestão de Faturas</h1>
          <p className="text-muted-foreground">
            Visualize e gerencie todas as faturas do sistema
          </p>
        </div>
      </div>

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filtros
          </CardTitle>
          <CardDescription>
            Use os filtros abaixo para encontrar faturas específicas
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Buscar por cliente ou operadora..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={filtroOperadora} onValueChange={setFiltroOperadora}>
              <SelectTrigger>
                <SelectValue placeholder="Filtrar por operadora" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todas as operadoras</SelectItem>
                {operadoras.map((operadora) => (
                  <SelectItem key={operadora.id} value={operadora.nome}>
                    {operadora.nome}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filtroStatus} onValueChange={setFiltroStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Filtrar por status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos os status</SelectItem>
                <SelectItem value="pendente">Pendente</SelectItem>
                <SelectItem value="aprovada">Aprovada</SelectItem>
                <SelectItem value="processando">Processando</SelectItem>
                <SelectItem value="rejeitada">Rejeitada</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Faturas */}
      <Card>
        <CardHeader>
          <CardTitle>
            Lista de Faturas ({faturasFiltradas.length})
          </CardTitle>
          <CardDescription>
            {faturasFiltradas.length === 0 ? "Nenhuma fatura encontrada com os filtros aplicados" : 
             `Mostrando ${faturasFiltradas.length} de ${faturas.length} faturas`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Operadora</TableHead>
                  <TableHead>Valor</TableHead>
                  <TableHead>Vencimento</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {faturasFiltradas.map((fatura) => (
                  <TableRow key={fatura.id}>
                    <TableCell className="font-medium">{fatura.cliente}</TableCell>
                    <TableCell>
                      <Badge variant="secondary">{fatura.operadora}</Badge>
                    </TableCell>
                    <TableCell>
                      R$ {fatura.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </TableCell>
                    <TableCell>{fatura.vencimento}</TableCell>
                    <TableCell>
                      <Badge className={getStatusColor(fatura.status)}>
                        <div className="flex items-center gap-1">
                          {getStatusIcon(fatura.status)}
                          {fatura.status.charAt(0).toUpperCase() + fatura.status.slice(1)}
                        </div>
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => downloadMutation.mutate(fatura.id)}
                        disabled={downloadMutation.isPending}
                      >
                        <Download className="h-4 w-4 mr-2" />
                        {downloadMutation.isPending ? "Baixando..." : "Download"}
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {faturasFiltradas.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                      Nenhuma fatura encontrada
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}