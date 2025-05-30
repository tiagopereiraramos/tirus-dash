import React, { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { CheckCircle, XCircle, Clock, Building, DollarSign, Calendar, Eye } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

interface Fatura {
  id: number;
  nome_sat: string;
  operadora_nome: string;
  mes_ano: string;
  valor_fatura: number;
  status_processo: string;
  observacoes?: string;
  data_vencimento?: string;
  cnpj?: string;
  unidade?: string;
}

interface AprovacaoRequest {
  faturaIds: number[];
  observacoes?: string;
  acao: 'aprovar' | 'rejeitar';
}

export default function Aprovacoes() {
  const { toast } = useToast();
  const [busca, setBusca] = useState<string>("");
  const [filtroOperadora, setFiltroOperadora] = useState<string>("");
  const [filtroStatus, setFiltroStatus] = useState<string>("pendente");
  const [faturasSelecionadas, setFaturasSelecionadas] = useState<number[]>([]);
  const [dialogAcao, setDialogAcao] = useState<{ aberto: boolean; acao: 'aprovar' | 'rejeitar' | null }>({
    aberto: false,
    acao: null
  });
  const [observacoes, setObservacoes] = useState<string>("");

  // Buscar faturas - endpoint retorna formato {success: true, data: [...]}
  const { data: responseFaturas, isLoading, error } = useQuery<{success: boolean, data: Fatura[]}>({
    queryKey: ["/api/faturas"],
    retry: 2
  });

  // Extrair dados do formato de resposta
  const faturas = responseFaturas?.data || [];

  // Mutação para aprovar/rejeitar faturas
  const processarAprovacaoMutation = useMutation({
    mutationFn: async (request: AprovacaoRequest) => {
      const promises = request.faturaIds.map(faturaId => {
        const endpoint = request.acao === 'aprovar' 
          ? `/api/faturas/${faturaId}/aprovar`
          : `/api/faturas/${faturaId}/rejeitar`;
        
        return apiRequest(endpoint, "PATCH", {
          observacoes: request.observacoes,
          aprovadoPor: "Admin RPA"
        });
      });
      
      return Promise.all(promises);
    },
    onSuccess: (_, variables) => {
      const acao = variables.acao === 'aprovar' ? 'aprovadas' : 'rejeitadas';
      toast({
        title: `Faturas ${acao}`,
        description: `${variables.faturaIds.length} fatura(s) foram ${acao} com sucesso.`,
      });
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
      setFaturasSelecionadas([]);
      setDialogAcao({ aberto: false, acao: null });
      setObservacoes("");
    },
    onError: (error: any) => {
      toast({
        title: "Erro ao processar faturas",
        description: error?.message || "Ocorreu um erro ao processar as faturas.",
        variant: "destructive",
      });
    },
  });

  // Filtrar faturas baseado na busca, operadora e status
  const faturasFiltradas = faturas.filter((fatura) => {
    const matchBusca = !busca || 
      fatura.nome_sat.toLowerCase().includes(busca.toLowerCase()) ||
      fatura.mes_ano.includes(busca) ||
      fatura.operadora_nome.toLowerCase().includes(busca.toLowerCase());
    
    const matchOperadora = !filtroOperadora || filtroOperadora === "todas" || fatura.operadora_nome === filtroOperadora;
    
    let matchStatus = true;
    if (filtroStatus === "pendente") {
      matchStatus = fatura.status_processo === "PENDENTE_APROVACAO";
    } else if (filtroStatus === "aprovada") {
      matchStatus = fatura.status_processo === "APROVADA";
    } else if (filtroStatus === "rejeitada") {
      matchStatus = fatura.status_processo === "REJEITADA";
    }
    
    return matchBusca && matchOperadora && matchStatus;
  });

  // Agrupar faturas por operadora para estatísticas
  const faturasPorOperadora = faturas.reduce((acc, fatura) => {
    acc[fatura.operadora_nome] = (acc[fatura.operadora_nome] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const handleSelecionarTodas = (checked: boolean) => {
    if (checked) {
      const faturasPendentes = faturasFiltradas
        .filter(f => f.status_processo === "PENDENTE_APROVACAO")
        .map(f => f.id);
      setFaturasSelecionadas(faturasPendentes);
    } else {
      setFaturasSelecionadas([]);
    }
  };

  const handleSelecionarFatura = (faturaId: number, checked: boolean) => {
    if (checked) {
      setFaturasSelecionadas([...faturasSelecionadas, faturaId]);
    } else {
      setFaturasSelecionadas(faturasSelecionadas.filter(id => id !== faturaId));
    }
  };

  const handleAbrirDialogAcao = (acao: 'aprovar' | 'rejeitar') => {
    setDialogAcao({ aberto: true, acao });
  };

  const handleConfirmarAcao = () => {
    if (!dialogAcao.acao || faturasSelecionadas.length === 0) return;
    
    processarAprovacaoMutation.mutate({
      faturaIds: faturasSelecionadas,
      observacoes: observacoes.trim() || undefined,
      acao: dialogAcao.acao
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "PENDENTE_APROVACAO":
        return <Clock className="h-4 w-4" />;
      case "APROVADA":
        return <CheckCircle className="h-4 w-4" />;
      case "REJEITADA":
        return <XCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "PENDENTE_APROVACAO":
        return "bg-yellow-100 text-yellow-800";
      case "APROVADA":
        return "bg-green-100 text-green-800";
      case "REJEITADA":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case "PENDENTE_APROVACAO":
        return "Pendente";
      case "APROVADA":
        return "Aprovada";
      case "REJEITADA":
        return "Rejeitada";
      default:
        return status;
    }
  };

  const formatValor = (valor: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(valor);
  };

  const faturasPendentes = faturas.filter(f => f.status_processo === "PENDENTE_APROVACAO");
  const faturasAprovadas = faturas.filter(f => f.status_processo === "APROVADA");
  const faturasRejeitadas = faturas.filter(f => f.status_processo === "REJEITADA");
  const valorTotalPendente = faturasPendentes.reduce((acc, f) => acc + (f.valor_fatura || 0), 0);

  if (isLoading) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Carregando faturas...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg text-red-600">Erro ao carregar faturas: {(error as Error).message}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Aprovações</h1>
          <p className="text-muted-foreground mt-2">
            Gerencie a aprovação de faturas de telecomunicações
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => handleAbrirDialogAcao('aprovar')}
            disabled={faturasSelecionadas.length === 0}
            className="bg-green-600 hover:bg-green-700"
          >
            <CheckCircle className="h-4 w-4 mr-2" />
            Aprovar Selecionadas ({faturasSelecionadas.length})
          </Button>
          <Button
            onClick={() => handleAbrirDialogAcao('rejeitar')}
            disabled={faturasSelecionadas.length === 0}
            variant="destructive"
          >
            <XCircle className="h-4 w-4 mr-2" />
            Rejeitar Selecionadas ({faturasSelecionadas.length})
          </Button>
        </div>
      </div>

      {/* Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Pendentes</p>
                <p className="text-2xl font-bold">{faturasPendentes.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Aprovadas</p>
                <p className="text-2xl font-bold">{faturasAprovadas.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <XCircle className="h-8 w-8 text-red-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Rejeitadas</p>
                <p className="text-2xl font-bold">{faturasRejeitadas.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Valor Pendente</p>
                <p className="text-2xl font-bold">{formatValor(valorTotalPendente)}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Buscar por cliente, operadora ou período..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
              />
            </div>
            <div className="w-48">
              <Select onValueChange={setFiltroOperadora} value={filtroOperadora}>
                <SelectTrigger>
                  <SelectValue placeholder="Todas as operadoras" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todas">Todas as operadoras</SelectItem>
                  {Object.keys(faturasPorOperadora).map((operadora) => (
                    <SelectItem key={operadora} value={operadora}>
                      {operadora} ({faturasPorOperadora[operadora]})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="w-48">
              <Select onValueChange={setFiltroStatus} value={filtroStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pendente">Pendentes</SelectItem>
                  <SelectItem value="aprovada">Aprovadas</SelectItem>
                  <SelectItem value="rejeitada">Rejeitadas</SelectItem>
                  <SelectItem value="todas">Todas</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Faturas */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Faturas para Aprovação ({faturasFiltradas.length})</CardTitle>
              <CardDescription>
                Lista de faturas aguardando processamento
              </CardDescription>
            </div>
            {faturasFiltradas.filter(f => f.status_processo === "PENDENTE_APROVACAO").length > 0 && (
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="select-all"
                  checked={faturasSelecionadas.length === faturasFiltradas.filter(f => f.status_processo === "PENDENTE_APROVACAO").length && faturasSelecionadas.length > 0}
                  onCheckedChange={handleSelecionarTodas}
                />
                <Label htmlFor="select-all">Selecionar todas pendentes</Label>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">Sel.</TableHead>
                <TableHead>Cliente</TableHead>
                <TableHead>Operadora</TableHead>
                <TableHead>Período</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Observações</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {faturasFiltradas.map((fatura) => (
                <TableRow key={fatura.id}>
                  <TableCell>
                    {fatura.status_processo === "PENDENTE_APROVACAO" && (
                      <Checkbox
                        checked={faturasSelecionadas.includes(fatura.id)}
                        onCheckedChange={(checked) => handleSelecionarFatura(fatura.id, checked as boolean)}
                      />
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">{fatura.nome_sat}</div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{fatura.operadora_nome}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3 text-muted-foreground" />
                      {fatura.mes_ano}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">{formatValor(fatura.valor_fatura)}</div>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(fatura.status_processo)}>
                      <div className="flex items-center gap-1">
                        {getStatusIcon(fatura.status_processo)}
                        {getStatusText(fatura.status_processo)}
                      </div>
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="max-w-48 truncate text-sm text-muted-foreground">
                      {fatura.observacoes || "-"}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Button size="sm" variant="outline">
                      <Eye className="h-4 w-4 mr-1" />
                      Detalhes
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {faturasFiltradas.length === 0 && (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                    {busca || filtroOperadora ? "Nenhuma fatura encontrada com os filtros aplicados" : "Nenhuma fatura para aprovação"}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Dialog de Confirmação */}
      <Dialog open={dialogAcao.aberto} onOpenChange={(aberto) => setDialogAcao({ aberto, acao: null })}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {dialogAcao.acao === 'aprovar' ? 'Aprovar Faturas' : 'Rejeitar Faturas'}
            </DialogTitle>
            <DialogDescription>
              Você está prestes a {dialogAcao.acao === 'aprovar' ? 'aprovar' : 'rejeitar'} {faturasSelecionadas.length} fatura(s).
              Esta ação não pode ser desfeita.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="observacoes">
                Observações {dialogAcao.acao === 'rejeitar' && '(obrigatório)'}
              </Label>
              <Textarea
                id="observacoes"
                placeholder="Digite suas observações..."
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
                required={dialogAcao.acao === 'rejeitar'}
              />
            </div>
          </div>
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => setDialogAcao({ aberto: false, acao: null })}
            >
              Cancelar
            </Button>
            <Button 
              onClick={handleConfirmarAcao}
              disabled={processarAprovacaoMutation.isPending || (dialogAcao.acao === 'rejeitar' && !observacoes.trim())}
              className={dialogAcao.acao === 'aprovar' ? 'bg-green-600 hover:bg-green-700' : ''}
              variant={dialogAcao.acao === 'rejeitar' ? 'destructive' : 'default'}
            >
              {processarAprovacaoMutation.isPending ? 'Processando...' : 
               dialogAcao.acao === 'aprovar' ? 'Confirmar Aprovação' : 'Confirmar Rejeição'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}