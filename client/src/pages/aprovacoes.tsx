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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header moderno */}
      <div className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 mb-2">Aprovações de Faturas</h1>
              <p className="text-slate-600 text-lg">Analise e aprove faturas pendentes no sistema</p>
              <div className="flex items-center mt-4 gap-6">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                  <span className="text-sm font-medium text-slate-700">
                    {aprovacoes.filter((a: Aprovacao) => a.status === "pendente").length} Pendentes
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                  <span className="text-sm font-medium text-slate-700">
                    {aprovacoes.filter((a: Aprovacao) => a.status === "aprovada").length} Aprovadas
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-400 rounded-full"></div>
                  <span className="text-sm font-medium text-slate-700">
                    {aprovacoes.filter((a: Aprovacao) => a.status === "rejeitada").length} Rejeitadas
                  </span>
                </div>
              </div>
            </div>
            
            <div className="text-right">
              <div className="text-2xl font-bold text-slate-900">{aprovacoes.length}</div>
              <div className="text-sm text-slate-600">Total de Solicitações</div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-6">
        {/* Filtros limpos */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-slate-700">Filtrar por:</span>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-48 border-slate-300">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos os status</SelectItem>
                <SelectItem value="pendente">Pendentes</SelectItem>
                <SelectItem value="aprovada">Aprovadas</SelectItem>
                <SelectItem value="rejeitada">Rejeitadas</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Lista de aprovações moderna */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200">
            <h3 className="text-lg font-semibold text-slate-900">
              Solicitações de Aprovação ({aprovacoesFiltradas.length})
            </h3>
          </div>
          
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : aprovacoesFiltradas.length > 0 ? (
            <div className="divide-y divide-slate-200">
              {aprovacoesFiltradas.map((aprovacao: Aprovacao) => (
                <div key={aprovacao.id} className="p-6 hover:bg-slate-50 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-3">
                        <span className="text-sm font-medium text-slate-500">#{aprovacao.id}</span>
                        {getStatusBadge(aprovacao.status)}
                        <div className={`text-sm font-medium ${getUrgenciaColor(aprovacao.vencimento)}`}>
                          Vence em {new Date(aprovacao.vencimento).toLocaleDateString('pt-BR')}
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <div className="text-sm text-slate-500">Cliente</div>
                          <div className="font-semibold text-slate-900">{aprovacao.cliente_nome}</div>
                        </div>
                        <div>
                          <div className="text-sm text-slate-500">Operadora</div>
                          <div className="font-medium text-slate-700">{aprovacao.operadora}</div>
                        </div>
                        <div>
                          <div className="text-sm text-slate-500">Valor</div>
                          <div className="text-lg font-bold text-green-600">
                            R$ {aprovacao.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                          </div>
                        </div>
                      </div>
                      
                      {aprovacao.observacoes && (
                        <div className="mt-3 p-3 bg-slate-50 rounded-lg">
                          <div className="text-sm text-slate-500">Observações</div>
                          <div className="text-sm text-slate-700">{aprovacao.observacoes}</div>
                        </div>
                      )}
                    </div>
                    
                    <div className="ml-6">
                      <Button
                        onClick={() => handleViewDetails(aprovacao)}
                        className="bg-blue-600 hover:bg-blue-700 text-white"
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        Analisar
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <CheckCircle className="h-12 w-12 text-slate-400 mx-auto mb-4" />
              <div className="text-lg font-medium text-slate-900 mb-2">Nenhuma solicitação encontrada</div>
              <div className="text-slate-500">Não há aprovações com os filtros selecionados</div>
            </div>
          )}
        </div>
      </div>

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