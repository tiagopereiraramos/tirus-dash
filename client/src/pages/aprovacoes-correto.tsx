import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { CheckCircle, XCircle, Clock } from "lucide-react";
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
}

interface FaturasResponse {
  success: boolean;
  data: Fatura[];
  total: number;
}

interface Operadora {
  id: number;
  nome: string;
  codigo: string;
  possui_rpa: boolean;
  status_ativo: boolean;
}

export default function Aprovacoes() {
  const { toast } = useToast();
  const [filtroOperadora, setFiltroOperadora] = useState<string>("");
  const [filtroStatus, setFiltroStatus] = useState<string>("PENDENTE_APROVACAO");
  const [busca, setBusca] = useState<string>("");
  const [observacao, setObservacao] = useState<string>("");
  const [motivo, setMotivo] = useState<string>("");

  const { data: aprovacoesResponse, isLoading: loadingAprovacoes } = useQuery<FaturasResponse>({ 
    queryKey: ["/api/faturas"] 
  });

  const { data: operadoras, isLoading: loadingOperadoras } = useQuery<Operadora[]>({ 
    queryKey: ["/api/operadoras"] 
  });

  const aprovarMutation = useMutation({
    mutationFn: ({ id, observacao }: { id: number; observacao?: string }) => 
      apiRequest(`/api/aprovacoes/${id}/aprovar`, "POST", { observacao }),
    onSuccess: () => {
      toast({
        title: "Aprovação realizada",
        description: "A fatura foi aprovada com sucesso.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
      setObservacao("");
    },
    onError: () => {
      toast({
        title: "Erro na aprovação",
        description: "Ocorreu um erro ao aprovar a fatura.",
        variant: "destructive",
      });
    },
  });

  const rejeitarMutation = useMutation({
    mutationFn: ({ id, motivo }: { id: number; motivo: string }) => 
      apiRequest(`/api/aprovacoes/${id}/rejeitar`, "POST", { motivo }),
    onSuccess: () => {
      toast({
        title: "Rejeição realizada",
        description: "A fatura foi rejeitada com sucesso.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
      setMotivo("");
    },
    onError: () => {
      toast({
        title: "Erro na rejeição",
        description: "Ocorreu um erro ao rejeitar a fatura.",
        variant: "destructive",
      });
    },
  });

  const aprovacoesData = aprovacoesResponse?.data || [];

  const aprovacoesFiltradas = aprovacoesData.filter((aprovacao) => {
    const matchOperadora = !filtroOperadora || aprovacao.operadora_nome === filtroOperadora;
    const matchStatus = !filtroStatus || aprovacao.status_processo === filtroStatus;
    const matchBusca = !busca || 
      aprovacao.nome_sat.toLowerCase().includes(busca.toLowerCase()) ||
      aprovacao.mes_ano.includes(busca);
    
    return matchOperadora && matchStatus && matchBusca;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "PENDENTE_APROVACAO": return "bg-yellow-100 text-yellow-800";
      case "APROVADA": return "bg-green-100 text-green-800";
      case "REJEITADA": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "PENDENTE_APROVACAO": return <Clock className="h-4 w-4" />;
      case "APROVADA": return <CheckCircle className="h-4 w-4" />;
      case "REJEITADA": return <XCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  if (loadingAprovacoes || loadingOperadoras) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Carregando aprovações...</div>
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
            Gerencie as aprovações de faturas pendentes
          </p>
        </div>
      </div>

      {/* Cards de resumo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-yellow-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Pendentes</p>
                <p className="text-2xl font-bold">
                  {aprovacoesData.filter((a) => a.status_processo === "PENDENTE_APROVACAO").length}
                </p>
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
                <p className="text-2xl font-bold">
                  {aprovacoesData.filter((a) => a.status_processo === "APROVADA").length}
                </p>
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
                <p className="text-2xl font-bold">
                  {aprovacoesData.filter((a) => a.status_processo === "REJEITADA").length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Buscar</label>
              <Input
                placeholder="Nome ou mês/ano..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Operadora</label>
              <Select value={filtroOperadora} onValueChange={setFiltroOperadora}>
                <SelectTrigger>
                  <SelectValue placeholder="Todas as operadoras" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todas as operadoras</SelectItem>
                  {(operadoras || []).map((operadora) => (
                    <SelectItem key={operadora.id} value={operadora.nome}>
                      {operadora.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Status</label>
              <Select value={filtroStatus} onValueChange={setFiltroStatus}>
                <SelectTrigger>
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="PENDENTE_APROVACAO">Pendentes</SelectItem>
                  <SelectItem value="APROVADA">Aprovadas</SelectItem>
                  <SelectItem value="REJEITADA">Rejeitadas</SelectItem>
                  <SelectItem value="todos">Todos</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Aprovações */}
      <Card>
        <CardHeader>
          <CardTitle>Aprovações ({aprovacoesFiltradas.length})</CardTitle>
          <CardDescription>
            Lista de faturas para aprovação
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
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {aprovacoesFiltradas.map((aprovacao) => (
                <TableRow key={aprovacao.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{aprovacao.nome_sat}</div>
                      {aprovacao.observacoes && (
                        <div className="text-sm text-muted-foreground">{aprovacao.observacoes}</div>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>{aprovacao.operadora_nome}</TableCell>
                  <TableCell>{aprovacao.mes_ano}</TableCell>
                  <TableCell>
                    R$ {aprovacao.valor_fatura.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(aprovacao.status_processo)}>
                      <div className="flex items-center gap-1">
                        {getStatusIcon(aprovacao.status_processo)}
                        {aprovacao.status_processo.replace(/_/g, ' ')}
                      </div>
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {aprovacao.status_processo === "PENDENTE_APROVACAO" && (
                      <div className="flex gap-2">
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button size="sm" variant="default">
                              <CheckCircle className="h-4 w-4 mr-1" />
                              Aprovar
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Aprovar Fatura</DialogTitle>
                              <DialogDescription>
                                Confirme a aprovação da fatura de {aprovacao.nome_sat}
                              </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4">
                              <div>
                                <label className="text-sm font-medium">Observação (opcional)</label>
                                <Textarea
                                  placeholder="Adicione uma observação..."
                                  value={observacao}
                                  onChange={(e) => setObservacao(e.target.value)}
                                />
                              </div>
                            </div>
                            <DialogFooter>
                              <Button
                                onClick={() => aprovarMutation.mutate({ id: aprovacao.id, observacao })}
                                disabled={aprovarMutation.isPending}
                              >
                                Confirmar Aprovação
                              </Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>

                        <Dialog>
                          <DialogTrigger asChild>
                            <Button size="sm" variant="destructive">
                              <XCircle className="h-4 w-4 mr-1" />
                              Rejeitar
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Rejeitar Fatura</DialogTitle>
                              <DialogDescription>
                                Informe o motivo da rejeição da fatura de {aprovacao.nome_sat}
                              </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4">
                              <div>
                                <label className="text-sm font-medium">Motivo da rejeição *</label>
                                <Textarea
                                  placeholder="Informe o motivo da rejeição..."
                                  value={motivo}
                                  onChange={(e) => setMotivo(e.target.value)}
                                  required
                                />
                              </div>
                            </div>
                            <DialogFooter>
                              <Button
                                variant="destructive"
                                onClick={() => rejeitarMutation.mutate({ id: aprovacao.id, motivo })}
                                disabled={rejeitarMutation.isPending || !motivo.trim()}
                              >
                                Confirmar Rejeição
                              </Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))}
              {aprovacoesFiltradas.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                    Nenhuma aprovação encontrada
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