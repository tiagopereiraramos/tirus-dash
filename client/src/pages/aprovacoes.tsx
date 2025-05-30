import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
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
import { Check, X, Eye, Clock, CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

type Aprovacao = {
  id: number;
  fatura_id: number;
  cliente_nome: string;
  operadora: string;
  valor: number;
  vencimento: string;
  mes_referencia: string;
  status: "pendente" | "aprovada" | "rejeitada";
  data_submissao: string;
  observacoes?: string;
  aprovador?: string;
  data_aprovacao?: string;
};

export default function Aprovacoes() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [aprovacaoSelecionada, setAprovacaoSelecionada] = useState<Aprovacao | null>(null);
  const [observacoes, setObservacoes] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const { toast } = useToast();

  // Query para buscar aprovações
  const { data: aprovacoes = [], isLoading } = useQuery({
    queryKey: ["/api/aprovacoes"],
  });

  // Filtrar aprovações por status
  const aprovacoesFiltradas = filterStatus === "all" 
    ? aprovacoes 
    : aprovacoes.filter((a: Aprovacao) => a.status === filterStatus);

  // Mutations para aprovar/rejeitar
  const aprovarMutation = useMutation({
    mutationFn: ({ id, observacoes }: { id: number; observacoes: string }) =>
      apiRequest(`/api/aprovacoes/${id}/aprovar`, { 
        method: "POST", 
        body: { observacoes } 
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/aprovacoes"] });
      toast({
        title: "Sucesso",
        description: "Fatura aprovada com sucesso",
      });
      setDialogOpen(false);
      setObservacoes("");
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao aprovar fatura",
        variant: "destructive",
      });
    },
  });

  const rejeitarMutation = useMutation({
    mutationFn: ({ id, observacoes }: { id: number; observacoes: string }) =>
      apiRequest(`/api/aprovacoes/${id}/rejeitar`, { 
        method: "POST", 
        body: { observacoes } 
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/aprovacoes"] });
      toast({
        title: "Sucesso",
        description: "Fatura rejeitada",
      });
      setDialogOpen(false);
      setObservacoes("");
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao rejeitar fatura",
        variant: "destructive",
      });
    },
  });

  // Handlers
  const handleViewDetails = (aprovacao: Aprovacao) => {
    setAprovacaoSelecionada(aprovacao);
    setObservacoes(aprovacao.observacoes || "");
    setDialogOpen(true);
  };

  const handleAprovar = () => {
    if (aprovacaoSelecionada) {
      aprovarMutation.mutate({ 
        id: aprovacaoSelecionada.id, 
        observacoes 
      });
    }
  };

  const handleRejeitar = () => {
    if (aprovacaoSelecionada) {
      rejeitarMutation.mutate({ 
        id: aprovacaoSelecionada.id, 
        observacoes 
      });
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pendente: { 
        variant: "secondary" as const, 
        className: "bg-yellow-100 text-yellow-700 border-yellow-200",
        icon: <Clock className="h-3 w-3 mr-1" />
      },
      aprovada: { 
        variant: "default" as const, 
        className: "bg-green-100 text-green-700 border-green-200",
        icon: <CheckCircle className="h-3 w-3 mr-1" />
      },
      rejeitada: { 
        variant: "destructive" as const, 
        className: "bg-red-100 text-red-700 border-red-200",
        icon: <XCircle className="h-3 w-3 mr-1" />
      },
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pendente;
    return (
      <Badge variant={config.variant} className={config.className}>
        {config.icon}
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getUrgenciaColor = (vencimento: string) => {
    const hoje = new Date();
    const dataVencimento = new Date(vencimento);
    const diasRestantes = Math.ceil((dataVencimento.getTime() - hoje.getTime()) / (1000 * 3600 * 24));
    
    if (diasRestantes <= 3) return "text-red-600 font-semibold";
    if (diasRestantes <= 7) return "text-yellow-600 font-medium";
    return "text-slate-600";
  };

  return (
    <div className="p-6 space-y-6 bg-slate-50 min-h-screen">
      {/* Header com gradiente cyan */}
      <div className="bg-gradient-to-r from-cyan-500 to-cyan-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Aprovações</h1>
            <p className="text-cyan-100 mt-2">Analise e aprove faturas pendentes no sistema RPA BGTELECOM</p>
          </div>
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-6 w-6" />
            <span className="text-sm font-medium">
              {aprovacoes.filter((a: Aprovacao) => a.status === "pendente").length} pendentes
            </span>
          </div>
        </div>
      </div>

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-cyan-500 to-cyan-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">{aprovacoes.length}</div>
            <div className="text-sm text-cyan-100 mt-1">Total de Solicitações</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-yellow-500 to-yellow-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {aprovacoes.filter((a: Aprovacao) => a.status === "pendente").length}
            </div>
            <div className="text-sm text-yellow-100 mt-1">Aguardando Análise</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-500 to-green-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {aprovacoes.filter((a: Aprovacao) => a.status === "aprovada").length}
            </div>
            <div className="text-sm text-green-100 mt-1">Aprovadas</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-red-500 to-red-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {aprovacoes.filter((a: Aprovacao) => a.status === "rejeitada").length}
            </div>
            <div className="text-sm text-red-100 mt-1">Rejeitadas</div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card className="border-0 shadow-lg bg-white">
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <CheckCircle className="h-5 w-5 text-slate-600" />
            <Label>Filtrar por status:</Label>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="pendente">Pendentes</SelectItem>
                <SelectItem value="aprovada">Aprovadas</SelectItem>
                <SelectItem value="rejeitada">Rejeitadas</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de aprovações */}
      <Card className="border-0 shadow-lg bg-white">
        <CardHeader className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-lg">
          <CardTitle className="flex items-center text-slate-800">
            <CheckCircle className="h-5 w-5 mr-2 text-cyan-600" />
            Solicitações de Aprovação ({aprovacoesFiltradas.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-600"></div>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Operadora</TableHead>
                  <TableHead>Valor</TableHead>
                  <TableHead>Vencimento</TableHead>
                  <TableHead>Submissão</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {aprovacoesFiltradas.length > 0 ? aprovacoesFiltradas.map((aprovacao: Aprovacao) => (
                  <TableRow key={aprovacao.id} className="hover:bg-slate-50/50 transition-colors">
                    <TableCell className="font-medium text-slate-600">#{aprovacao.id}</TableCell>
                    <TableCell className="font-semibold text-slate-900">{aprovacao.cliente_nome}</TableCell>
                    <TableCell className="text-sm text-slate-600">{aprovacao.operadora}</TableCell>
                    <TableCell className="font-semibold text-green-600">
                      R$ {aprovacao.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </TableCell>
                    <TableCell className={`text-sm ${getUrgenciaColor(aprovacao.vencimento)}`}>
                      {new Date(aprovacao.vencimento).toLocaleDateString('pt-BR')}
                    </TableCell>
                    <TableCell className="text-sm text-slate-600">
                      {new Date(aprovacao.data_submissao).toLocaleDateString('pt-BR')}
                    </TableCell>
                    <TableCell>{getStatusBadge(aprovacao.status)}</TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleViewDetails(aprovacao)}
                          className="h-8 px-3 text-blue-600 border-blue-200 hover:bg-blue-50"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          Analisar
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-slate-500">
                      Nenhuma solicitação encontrada
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Modal de análise melhorado */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader className="border-b pb-4">
            <DialogTitle className="text-2xl font-bold text-slate-900">
              Análise de Aprovação
            </DialogTitle>
            <p className="text-slate-600">Solicitation #{aprovacaoSelecionada?.id}</p>
          </DialogHeader>
          
          {aprovacaoSelecionada && (
            <div className="space-y-6 pt-4">
              {/* Card com informações principais */}
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <div className="text-sm font-medium text-slate-600 mb-1">Cliente</div>
                      <div className="text-xl font-bold text-slate-900">{aprovacaoSelecionada.cliente_nome}</div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-slate-600 mb-1">Operadora</div>
                      <div className="text-lg font-semibold text-slate-700">{aprovacaoSelecionada.operadora}</div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <div className="text-sm font-medium text-slate-600 mb-1">Valor da Fatura</div>
                      <div className="text-2xl font-bold text-green-600">
                        R$ {aprovacaoSelecionada.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm font-medium text-slate-600 mb-1">Data de Vencimento</div>
                      <div className={`text-lg font-semibold ${getUrgenciaColor(aprovacaoSelecionada.vencimento)}`}>
                        {new Date(aprovacaoSelecionada.vencimento).toLocaleDateString('pt-BR')}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Detalhes adicionais */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white border border-slate-200 rounded-lg p-4">
                  <div className="text-sm font-medium text-slate-600 mb-2">Mês de Referência</div>
                  <div className="text-lg font-semibold">{aprovacaoSelecionada.mes_referencia}</div>
                </div>
                <div className="bg-white border border-slate-200 rounded-lg p-4">
                  <div className="text-sm font-medium text-slate-600 mb-2">Status Atual</div>
                  <div>{getStatusBadge(aprovacaoSelecionada.status)}</div>
                </div>
              </div>

              {/* Observações existentes */}
              {aprovacaoSelecionada.observacoes && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="text-sm font-medium text-yellow-800 mb-2">Observações Existentes</div>
                  <div className="text-yellow-700">{aprovacaoSelecionada.observacoes}</div>
                </div>
              )}

              {/* Campo para novas observações */}
              {aprovacaoSelecionada.status === "pendente" && (
                <div className="space-y-3">
                  <Label htmlFor="observacoes" className="text-base font-medium">
                    Observações da Análise
                  </Label>
                  <Textarea
                    id="observacoes"
                    value={observacoes}
                    onChange={(e) => setObservacoes(e.target.value)}
                    placeholder="Adicione suas observações sobre esta aprovação..."
                    className="min-h-32 resize-none border-slate-300"
                  />
                </div>
              )}

              {/* Ações */}
              <div className="border-t pt-6">
                {aprovacaoSelecionada.status === "pendente" ? (
                  <div className="flex justify-between">
                    <Button
                      variant="outline"
                      onClick={() => setDialogOpen(false)}
                      className="px-6"
                    >
                      Cancelar
                    </Button>
                    <div className="flex gap-3">
                      <Button
                        variant="destructive"
                        onClick={handleRejeitar}
                        disabled={rejeitarMutation.isPending}
                        className="px-6"
                      >
                        <X className="h-4 w-4 mr-2" />
                        {rejeitarMutation.isPending ? "Rejeitando..." : "Rejeitar"}
                      </Button>
                      <Button
                        onClick={handleAprovar}
                        disabled={aprovarMutation.isPending}
                        className="bg-green-600 hover:bg-green-700 px-8"
                      >
                        <Check className="h-4 w-4 mr-2" />
                        {aprovarMutation.isPending ? "Aprovando..." : "Aprovar Fatura"}
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      {aprovacaoSelecionada.status === "aprovada" ? (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-600" />
                      )}
                      <span className="font-medium">
                        Esta fatura já foi {aprovacaoSelecionada.status}
                      </span>
                    </div>
                    {aprovacaoSelecionada.aprovador && (
                      <p className="text-sm text-slate-600">
                        Por: {aprovacaoSelecionada.aprovador}
                      </p>
                    )}
                    {aprovacaoSelecionada.data_aprovacao && (
                      <p className="text-sm text-slate-600">
                        Em: {new Date(aprovacaoSelecionada.data_aprovacao).toLocaleDateString('pt-BR')}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}