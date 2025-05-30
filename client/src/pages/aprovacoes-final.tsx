import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { CheckCircle, XCircle, Clock, Search, Filter } from "lucide-react";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

interface Aprovacao {
  id: number;
  nome_sat: string;
  cnpj: string;
  operadora_nome: string;
  unidade: string;
  status_aprovacao?: string;
  valor?: number;
  data_vencimento?: string;
}

export default function Aprovacoes() {
  const [filtroOperadora, setFiltroOperadora] = useState("todas");
  const [filtroStatus, setFiltroStatus] = useState("pendente");
  const [termoBusca, setTermoBusca] = useState("");
  const [observacoes, setObservacoes] = useState<{[key: number]: string}>({});
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: aprovacoes, isLoading: loadingAprovacoes } = useQuery({ 
    queryKey: ["/api/aprovacoes"] 
  });
  const { data: operadoras, isLoading: loadingOperadoras } = useQuery({ 
    queryKey: ["/api/operadoras"] 
  });

  const aprovarMutation = useMutation({
    mutationFn: ({ id, observacao }: { id: number; observacao?: string }) => 
      apiRequest(`/api/aprovacoes/${id}/aprovar`, {
        method: "POST",
        body: JSON.stringify({ observacao }),
      }),
    onSuccess: () => {
      toast({
        title: "Aprovação realizada",
        description: "A fatura foi aprovada com sucesso.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/aprovacoes"] });
    },
    onError: () => {
      toast({
        title: "Erro",
        description: "Erro ao aprovar a fatura.",
        variant: "destructive",
      });
    },
  });

  const rejeitarMutation = useMutation({
    mutationFn: ({ id, motivo }: { id: number; motivo: string }) => 
      apiRequest(`/api/aprovacoes/${id}/rejeitar`, {
        method: "POST",
        body: JSON.stringify({ motivo }),
      }),
    onSuccess: () => {
      toast({
        title: "Rejeição realizada",
        description: "A fatura foi rejeitada com sucesso.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/aprovacoes"] });
    },
    onError: () => {
      toast({
        title: "Erro",
        description: "Erro ao rejeitar a fatura.",
        variant: "destructive",
      });
    },
  });

  if (loadingAprovacoes || loadingOperadoras) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Carregando aprovações...</div>
      </div>
    );
  }

  const aprovacoesData = aprovacoes?.data || [];
  const operadorasData = operadoras || [];

  const aprovacoesFiltradas = aprovacoesData.filter((aprovacao: Aprovacao) => {
    const filtroOperadoraMatch = filtroOperadora === "todas" || aprovacao.operadora_nome === filtroOperadora;
    const filtroStatusMatch = filtroStatus === "todos" || aprovacao.status_aprovacao === filtroStatus;
    const termoBuscaMatch = termoBusca === "" || 
      aprovacao.nome_sat.toLowerCase().includes(termoBusca.toLowerCase()) ||
      aprovacao.cnpj.includes(termoBusca);
    
    return filtroOperadoraMatch && filtroStatusMatch && termoBuscaMatch;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "aprovado":
        return <Badge className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">Aprovado</Badge>;
      case "rejeitado":
        return <Badge variant="destructive">Rejeitado</Badge>;
      case "pendente":
      default:
        return <Badge variant="secondary">Pendente</Badge>;
    }
  };

  const handleAprovar = (id: number) => {
    aprovarMutation.mutate({ 
      id, 
      observacao: observacoes[id] || undefined 
    });
  };

  const handleRejeitar = (id: number) => {
    const motivo = observacoes[id];
    if (!motivo?.trim()) {
      toast({
        title: "Motivo obrigatório",
        description: "Por favor, informe o motivo da rejeição.",
        variant: "destructive",
      });
      return;
    }
    rejeitarMutation.mutate({ id, motivo });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Aprovações</h1>
        <p className="text-muted-foreground">
          Gerencie e aprove faturas pendentes de validação
        </p>
      </div>

      {/* Métricas */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pendentes</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {aprovacoesData.filter((a: Aprovacao) => a.status_aprovacao === "pendente" || !a.status_aprovacao).length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Aprovadas</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {aprovacoesData.filter((a: Aprovacao) => a.status_aprovacao === "aprovado").length}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rejeitadas</CardTitle>
            <XCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {aprovacoesData.filter((a: Aprovacao) => a.status_aprovacao === "rejeitado").length}
            </div>
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
                <SelectItem value="pendente">Pendente</SelectItem>
                <SelectItem value="aprovado">Aprovado</SelectItem>
                <SelectItem value="rejeitado">Rejeitado</SelectItem>
              </SelectContent>
            </Select>

            <Button variant="outline" onClick={() => {
              setFiltroOperadora("todas");
              setFiltroStatus("pendente");
              setTermoBusca("");
            }}>
              Limpar Filtros
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Aprovações */}
      <div className="grid gap-6">
        {aprovacoesFiltradas.map((aprovacao: Aprovacao) => (
          <Card key={aprovacao.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-lg">{aprovacao.nome_sat}</CardTitle>
                  <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                    <span>CNPJ: {aprovacao.cnpj}</span>
                    <span>•</span>
                    <span>{aprovacao.unidade}</span>
                  </div>
                </div>
                {getStatusBadge(aprovacao.status_aprovacao || "pendente")}
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4 mb-4">
                <div>
                  <p className="text-sm font-medium">Operadora</p>
                  <p className="text-sm text-muted-foreground">{aprovacao.operadora_nome}</p>
                </div>
                <div>
                  <p className="text-sm font-medium">Valor</p>
                  <p className="text-sm text-muted-foreground">
                    {aprovacao.valor ? `R$ ${aprovacao.valor.toLocaleString('pt-BR')}` : "N/A"}
                  </p>
                </div>
                <div>
                  <p className="text-sm font-medium">Vencimento</p>
                  <p className="text-sm text-muted-foreground">
                    {aprovacao.data_vencimento ? 
                      new Date(aprovacao.data_vencimento).toLocaleDateString('pt-BR') : 
                      "N/A"
                    }
                  </p>
                </div>
              </div>

              {(!aprovacao.status_aprovacao || aprovacao.status_aprovacao === "pendente") && (
                <div className="space-y-4 pt-4 border-t">
                  <div>
                    <label className="text-sm font-medium mb-2 block">
                      Observações {aprovacao.status_aprovacao === "pendente" ? "(Motivo obrigatório para rejeição)" : "(Opcional)"}
                    </label>
                    <Textarea
                      placeholder="Digite suas observações ou motivo da rejeição..."
                      value={observacoes[aprovacao.id] || ""}
                      onChange={(e) => setObservacoes(prev => ({
                        ...prev,
                        [aprovacao.id]: e.target.value
                      }))}
                      className="resize-none"
                      rows={3}
                    />
                  </div>
                  <div className="flex justify-end space-x-2">
                    <Button
                      variant="outline"
                      onClick={() => handleRejeitar(aprovacao.id)}
                      disabled={rejeitarMutation.isPending}
                      className="text-red-600 border-red-200 hover:bg-red-50"
                    >
                      <XCircle className="mr-1 h-4 w-4" />
                      Rejeitar
                    </Button>
                    <Button
                      onClick={() => handleAprovar(aprovacao.id)}
                      disabled={aprovarMutation.isPending}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="mr-1 h-4 w-4" />
                      Aprovar
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {aprovacoesFiltradas.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <CheckCircle className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Nenhuma aprovação encontrada</h3>
            <p className="text-muted-foreground text-center">
              Não há aprovações que correspondam aos filtros aplicados.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}