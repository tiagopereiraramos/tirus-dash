import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { apiRequest, queryClient } from "@/lib/queryClient";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Search, FileText, Calendar, DollarSign, Filter, Eye, CheckCircle, XCircle } from "lucide-react";

interface Fatura {
  id: string;
  cliente_id: string;
  mes_ano: string;
  valor_fatura: number;
  data_vencimento: string;
  status_processo: string;
  url_fatura?: string;
  cliente: {
    nome_sat: string;
    operadora: {
      nome: string;
    };
  };
  observacoes?: string;
  aprovado_por?: string;
  data_aprovacao?: string;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'PENDENTE_APROVACAO':
      return 'bg-yellow-100 text-yellow-800';
    case 'APROVADA':
      return 'bg-green-100 text-green-800';
    case 'REJEITADA':
      return 'bg-red-100 text-red-800';
    case 'ENVIADA_SAT':
      return 'bg-blue-100 text-blue-800';
    case 'FATURA_BAIXADA':
      return 'bg-purple-100 text-purple-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('pt-BR');
};

export default function Faturas() {
  const { toast } = useToast();
  const [busca, setBusca] = useState("");
  const [filtroStatus, setFiltroStatus] = useState("todos");
  const [filtroMesAno, setFiltroMesAno] = useState("");
  const [detalheFatura, setDetalheFatura] = useState<Fatura | null>(null);
  const [dialogDetalheAberto, setDialogDetalheAberto] = useState(false);
  const [observacoesAprovacao, setObservacoesAprovacao] = useState("");

  // Buscar faturas do FastAPI
  const { data: responseFaturas, isLoading: loadingFaturas, error: errorFaturas } = useQuery({
    queryKey: ["/api/processos"],
    retry: false,
  });

  // Mutation para aprovar fatura
  const mutationAprovar = useMutation({
    mutationFn: async ({ faturaId, observacoes }: { faturaId: string; observacoes?: string }) => {
      return await apiRequest(`/api/processos/${faturaId}/aprovar`, {
        method: "PUT",
        body: JSON.stringify({ observacoes }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/processos"] });
      setDialogDetalheAberto(false);
      setObservacoesAprovacao("");
      toast({
        title: "Fatura aprovada",
        description: "A fatura foi aprovada com sucesso.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Erro ao aprovar fatura",
        description: error?.message || "Ocorreu um erro ao aprovar a fatura.",
        variant: "destructive",
      });
    },
  });

  // Mutation para rejeitar fatura
  const mutationRejeitar = useMutation({
    mutationFn: async ({ faturaId, motivo }: { faturaId: string; motivo: string }) => {
      return await apiRequest(`/api/processos/${faturaId}/rejeitar`, {
        method: "PUT",
        body: JSON.stringify({ motivo }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/processos"] });
      setDialogDetalheAberto(false);
      toast({
        title: "Fatura rejeitada",
        description: "A fatura foi rejeitada.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Erro ao rejeitar fatura",
        description: error?.message || "Ocorreu um erro ao rejeitar a fatura.",
        variant: "destructive",
      });
    },
  });

  if (loadingFaturas) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Carregando faturas...</div>
        </div>
      </div>
    );
  }

  if (errorFaturas) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg text-red-600">Erro ao carregar faturas: {(errorFaturas as Error).message}</div>
        </div>
      </div>
    );
  }

  const faturas = responseFaturas?.processos || [];

  // Filtrar faturas
  const faturasFiltradas = faturas.filter((fatura: Fatura) => {
    const matchBusca = !busca || 
      fatura.cliente?.nome_sat?.toLowerCase().includes(busca.toLowerCase()) ||
      fatura.cliente?.operadora?.nome?.toLowerCase().includes(busca.toLowerCase()) ||
      fatura.mes_ano.includes(busca);
    
    const matchStatus = filtroStatus === "todos" || fatura.status_processo === filtroStatus;
    const matchMesAno = !filtroMesAno || fatura.mes_ano === filtroMesAno;
    
    return matchBusca && matchStatus && matchMesAno;
  });

  const totalFaturas = faturasFiltradas.length;
  const valorTotal = faturasFiltradas.reduce((sum: number, f: Fatura) => sum + (f.valor_fatura || 0), 0);

  const handleVerDetalhes = (fatura: Fatura) => {
    setDetalheFatura(fatura);
    setDialogDetalheAberto(true);
  };

  const handleAprovar = () => {
    if (detalheFatura) {
      mutationAprovar.mutate({
        faturaId: detalheFatura.id,
        observacoes: observacoesAprovacao
      });
    }
  };

  const handleRejeitar = () => {
    if (detalheFatura && observacoesAprovacao) {
      mutationRejeitar.mutate({
        faturaId: detalheFatura.id,
        motivo: observacoesAprovacao
      });
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Faturas</h1>
          <p className="text-muted-foreground mt-2">
            Gerencie todas as faturas do sistema RPA
          </p>
        </div>
      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Total de Faturas</p>
                <p className="text-2xl font-bold">{totalFaturas}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <DollarSign className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Valor Total</p>
                <p className="text-2xl font-bold">{formatCurrency(valorTotal)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Calendar className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Pendentes</p>
                <p className="text-2xl font-bold">
                  {faturas.filter((f: Fatura) => f.status_processo === 'PENDENTE_APROVACAO').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Aprovadas</p>
                <p className="text-2xl font-bold">
                  {faturas.filter((f: Fatura) => f.status_processo === 'APROVADA').length}
                </p>
              </div>
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
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label>Buscar</Label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Cliente, operadora ou mês/ano..."
                  value={busca}
                  onChange={(e) => setBusca(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Status</Label>
              <Select value={filtroStatus} onValueChange={setFiltroStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos os status</SelectItem>
                  <SelectItem value="PENDENTE_APROVACAO">Pendente Aprovação</SelectItem>
                  <SelectItem value="APROVADA">Aprovada</SelectItem>
                  <SelectItem value="REJEITADA">Rejeitada</SelectItem>
                  <SelectItem value="ENVIADA_SAT">Enviada SAT</SelectItem>
                  <SelectItem value="FATURA_BAIXADA">Fatura Baixada</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Mês/Ano</Label>
              <Input
                placeholder="2024-05"
                value={filtroMesAno}
                onChange={(e) => setFiltroMesAno(e.target.value)}
              />
            </div>

            <div className="space-y-2 flex items-end">
              <Button 
                variant="outline" 
                onClick={() => {
                  setBusca("");
                  setFiltroStatus("todos");
                  setFiltroMesAno("");
                }}
                className="w-full"
              >
                Limpar Filtros
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de faturas */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Faturas ({faturasFiltradas.length})</CardTitle>
          <CardDescription>
            Faturas processadas pelo sistema RPA da BGTELECOM
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cliente</TableHead>
                <TableHead>Operadora</TableHead>
                <TableHead>Mês/Ano</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Vencimento</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {faturasFiltradas.map((fatura: Fatura) => (
                <TableRow key={fatura.id}>
                  <TableCell className="font-medium">
                    {fatura.cliente?.nome_sat || 'N/A'}
                  </TableCell>
                  <TableCell>
                    {fatura.cliente?.operadora?.nome || 'N/A'}
                  </TableCell>
                  <TableCell>{fatura.mes_ano}</TableCell>
                  <TableCell>{formatCurrency(fatura.valor_fatura || 0)}</TableCell>
                  <TableCell>{fatura.data_vencimento ? formatDate(fatura.data_vencimento) : 'N/A'}</TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(fatura.status_processo)}>
                      {fatura.status_processo.replace('_', ' ')}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleVerDetalhes(fatura)}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      Ver
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          
          {faturasFiltradas.length === 0 && (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">Nenhuma fatura encontrada com os filtros aplicados</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dialog de detalhes da fatura */}
      <Dialog open={dialogDetalheAberto} onOpenChange={setDialogDetalheAberto}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Detalhes da Fatura</DialogTitle>
            <DialogDescription>
              Informações completas e ações disponíveis
            </DialogDescription>
          </DialogHeader>
          
          {detalheFatura && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="font-semibold">Cliente</Label>
                  <p>{detalheFatura.cliente?.nome_sat}</p>
                </div>
                <div>
                  <Label className="font-semibold">Operadora</Label>
                  <p>{detalheFatura.cliente?.operadora?.nome}</p>
                </div>
                <div>
                  <Label className="font-semibold">Mês/Ano</Label>
                  <p>{detalheFatura.mes_ano}</p>
                </div>
                <div>
                  <Label className="font-semibold">Valor</Label>
                  <p>{formatCurrency(detalheFatura.valor_fatura || 0)}</p>
                </div>
                <div>
                  <Label className="font-semibold">Vencimento</Label>
                  <p>{detalheFatura.data_vencimento ? formatDate(detalheFatura.data_vencimento) : 'N/A'}</p>
                </div>
                <div>
                  <Label className="font-semibold">Status</Label>
                  <Badge className={getStatusColor(detalheFatura.status_processo)}>
                    {detalheFatura.status_processo.replace('_', ' ')}
                  </Badge>
                </div>
              </div>

              {detalheFatura.observacoes && (
                <div>
                  <Label className="font-semibold">Observações</Label>
                  <p className="text-sm text-muted-foreground">{detalheFatura.observacoes}</p>
                </div>
              )}

              {detalheFatura.status_processo === 'PENDENTE_APROVACAO' && (
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="observacoes">Observações (opcional)</Label>
                    <Textarea
                      id="observacoes"
                      placeholder="Adicione observações sobre a aprovação/rejeição..."
                      value={observacoesAprovacao}
                      onChange={(e) => setObservacoesAprovacao(e.target.value)}
                    />
                  </div>

                  <div className="flex gap-3">
                    <Button
                      onClick={handleAprovar}
                      disabled={mutationAprovar.isPending}
                      className="flex-1"
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Aprovar
                    </Button>
                    <Button
                      variant="destructive"
                      onClick={handleRejeitar}
                      disabled={mutationRejeitar.isPending || !observacoesAprovacao}
                      className="flex-1"
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Rejeitar
                    </Button>
                  </div>
                </div>
              )}

              {detalheFatura.url_fatura && (
                <div>
                  <Button variant="outline" asChild className="w-full">
                    <a href={detalheFatura.url_fatura} target="_blank" rel="noopener noreferrer">
                      <FileText className="h-4 w-4 mr-2" />
                      Visualizar Fatura
                    </a>
                  </Button>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}