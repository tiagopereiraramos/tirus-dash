import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { FileText, Download, Eye, Search, Filter } from "lucide-react";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

interface Fatura {
  id: number;
  nome_sat: string;
  cnpj: string;
  operadora_nome: string;
  unidade: string;
  status_ativo: boolean;
  valor?: number;
  data_vencimento?: string;
  status_fatura?: string;
}

export default function Faturas() {
  const [filtroOperadora, setFiltroOperadora] = useState("todas");
  const [filtroStatus, setFiltroStatus] = useState("todos");
  const [termoBusca, setTermoBusca] = useState("");
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: faturas, isLoading: loadingFaturas } = useQuery({ 
    queryKey: ["/api/faturas"] 
  });
  const { data: operadoras, isLoading: loadingOperadoras } = useQuery({ 
    queryKey: ["/api/operadoras"] 
  });

  const downloadMutation = useMutation({
    mutationFn: (faturaId: number) => apiRequest(`/api/faturas/${faturaId}/download`, {
      method: "POST",
    }),
    onSuccess: () => {
      toast({
        title: "Download iniciado",
        description: "O download da fatura foi iniciado com sucesso.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
    },
    onError: () => {
      toast({
        title: "Erro",
        description: "Erro ao iniciar download da fatura.",
        variant: "destructive",
      });
    },
  });

  if (loadingFaturas || loadingOperadoras) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Carregando faturas...</div>
      </div>
    );
  }

  const faturasData = faturas?.data || [];
  const operadorasData = operadoras || [];
  const totalFaturas = faturasData.length;

  const faturasFiltradas = faturasData.filter((fatura: Fatura) => {
    const filtroOperadoraMatch = filtroOperadora === "todas" || fatura.operadora_nome === filtroOperadora;
    const filtroStatusMatch = filtroStatus === "todos" || fatura.status_fatura === filtroStatus;
    const termoBuscaMatch = termoBusca === "" || 
      fatura.nome_sat.toLowerCase().includes(termoBusca.toLowerCase()) ||
      fatura.cnpj.includes(termoBusca);
    
    return filtroOperadoraMatch && filtroStatusMatch && termoBuscaMatch;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "baixada":
        return <Badge className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">Baixada</Badge>;
      case "pendente":
        return <Badge variant="secondary">Pendente</Badge>;
      case "erro":
        return <Badge variant="destructive">Erro</Badge>;
      default:
        return <Badge variant="outline">{status || "N/A"}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Faturas</h1>
        <p className="text-muted-foreground">
          Gerencie e visualize todas as faturas de telecomunicações
        </p>
      </div>

      {/* Métricas */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Faturas</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalFaturas}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-4">
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Buscar por cliente ou CNPJ..."
                value={termoBusca}
                onChange={(e) => setTermoBusca(e.target.value)}
                className="pl-8"
              />
            </div>
            
            <Select value={filtroOperadora} onValueChange={setFiltroOperadora}>
              <SelectTrigger>
                <SelectValue placeholder="Filtrar por operadora" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todas">Todas as operadoras</SelectItem>
                {operadorasData.map((operadora: any) => (
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
                <SelectItem value="baixada">Baixada</SelectItem>
                <SelectItem value="pendente">Pendente</SelectItem>
                <SelectItem value="erro">Erro</SelectItem>
              </SelectContent>
            </Select>

            <Button variant="outline" onClick={() => {
              setFiltroOperadora("todas");
              setFiltroStatus("todos");
              setTermoBusca("");
            }}>
              Limpar Filtros
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Faturas */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Faturas ({faturasFiltradas.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cliente</TableHead>
                <TableHead>Operadora</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Vencimento</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {faturasFiltradas.map((fatura: Fatura) => (
                <TableRow key={fatura.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div>
                      <div className="font-medium text-sm">
                        {fatura.nome_sat}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        CNPJ: {fatura.cnpj} • {fatura.unidade}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{fatura.operadora_nome}</Badge>
                  </TableCell>
                  <TableCell>
                    {fatura.valor ? `R$ ${fatura.valor.toLocaleString('pt-BR')}` : "N/A"}
                  </TableCell>
                  <TableCell>
                    {fatura.data_vencimento ? 
                      new Date(fatura.data_vencimento).toLocaleDateString('pt-BR') : 
                      "N/A"
                    }
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(fatura.status_fatura || "pendente")}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => downloadMutation.mutate(fatura.id)}
                        disabled={downloadMutation.isPending}
                      >
                        <Download className="mr-1 h-3 w-3" />
                        Download
                      </Button>
                      <Button variant="outline" size="sm">
                        <Eye className="mr-1 h-3 w-3" />
                        Visualizar
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {faturasFiltradas.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <FileText className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Nenhuma fatura encontrada</h3>
            <p className="text-muted-foreground text-center">
              Não há faturas que correspondam aos filtros aplicados.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}