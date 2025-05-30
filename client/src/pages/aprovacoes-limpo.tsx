import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Search, CheckCircle, XCircle, Clock, DollarSign, FileCheck } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";

interface Aprovacao {
  id: number;
  cliente: string;
  operadora: string;
  valor: number;
  vencimento: string;
  status: string;
}

export default function Aprovacoes() {
  const [busca, setBusca] = useState("");
  const [observacao, setObservacao] = useState("");
  const [motivo, setMotivo] = useState("");
  const [dialogAberto, setDialogAberto] = useState(false);
  const [tipoDialog, setTipoDialog] = useState<"aprovar" | "rejeitar">("aprovar");
  const [faturaAtual, setFaturaAtual] = useState<Aprovacao | null>(null);
  
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: aprovacoes, isLoading } = useQuery({
    queryKey: ["/api/faturas"],
    retry: false,
  });

  const aprovarMutation = useMutation({
    mutationFn: (data: { id: number; observacao: string }) => 
      apiRequest(`/api/aprovacoes/${data.id}/aprovar`, { 
        method: "POST", 
        body: { observacao: data.observacao }
      }),
    onSuccess: () => {
      toast({
        title: "Fatura aprovada",
        description: "A fatura foi aprovada com sucesso.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
      setDialogAberto(false);
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
    mutationFn: (data: { id: number; motivo: string }) => 
      apiRequest(`/api/aprovacoes/${data.id}/rejeitar`, { 
        method: "POST", 
        body: { motivo: data.motivo }
      }),
    onSuccess: () => {
      toast({
        title: "Fatura rejeitada",
        description: "A fatura foi rejeitada com sucesso.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
      setDialogAberto(false);
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

  const faturasData = Array.isArray(aprovacoes) ? aprovacoes : [];
  
  const faturasPendentes = faturasData.filter((fatura) => {
    const isPendente = fatura.status === "pendente";
    const matchBusca = !busca || 
      fatura.cliente.toLowerCase().includes(busca.toLowerCase()) ||
      fatura.operadora.toLowerCase().includes(busca.toLowerCase());
    
    return isPendente && matchBusca;
  });

  const handleAprovar = (fatura: Aprovacao) => {
    setFaturaAtual(fatura);
    setTipoDialog("aprovar");
    setDialogAberto(true);
  };

  const handleRejeitar = (fatura: Aprovacao) => {
    setFaturaAtual(fatura);
    setTipoDialog("rejeitar");
    setDialogAberto(true);
  };

  const confirmarAcao = () => {
    if (!faturaAtual) return;

    if (tipoDialog === "aprovar") {
      aprovarMutation.mutate({ id: faturaAtual.id, observacao });
    } else {
      if (!motivo.trim()) {
        toast({
          title: "Motivo obrigatório",
          description: "Por favor, informe o motivo da rejeição.",
          variant: "destructive",
        });
        return;
      }
      rejeitarMutation.mutate({ id: faturaAtual.id, motivo });
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
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
    <div className="p-6 space-y-6">
      {/* Cabeçalho */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-3xl font-bold text-gray-900">Aprovações de Faturas</h1>
        <p className="text-gray-600 mt-2">Gerencie aprovações e rejeições de faturas pendentes</p>
      </div>

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-0 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pendentes</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{faturasPendentes.length}</p>
              </div>
              <div className="p-3 rounded-full bg-yellow-50">
                <Clock className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Aprovadas</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {faturasData.filter(f => f.status === "aprovada").length}
                </p>
              </div>
              <div className="p-3 rounded-full bg-green-50">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Valor Pendente</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  R$ {faturasPendentes.reduce((acc, f) => acc + f.valor, 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="p-3 rounded-full bg-blue-50">
                <DollarSign className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card className="border-0 shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-semibold">Buscar Faturas</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Buscar por cliente ou operadora..."
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Lista de Faturas Pendentes */}
      <Card className="border-0 shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-semibold">
            Faturas Pendentes de Aprovação ({faturasPendentes.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {faturasPendentes.map((fatura) => (
              <div
                key={fatura.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-4 mb-2">
                      <h3 className="font-semibold text-gray-900">{fatura.cliente}</h3>
                      <Badge variant="secondary" className="text-xs">
                        {fatura.operadora}
                      </Badge>
                      <Badge className="text-xs bg-yellow-100 text-yellow-800">
                        Pendente
                      </Badge>
                    </div>
                    <div className="flex items-center gap-6 text-sm text-gray-600">
                      <span>Valor: R$ {fatura.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
                      <span>Vencimento: {fatura.vencimento}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRejeitar(fatura)}
                      className="text-red-600 border-red-200 hover:bg-red-50"
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Rejeitar
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => handleAprovar(fatura)}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Aprovar
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            
            {faturasPendentes.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <FileCheck className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Nenhuma fatura pendente de aprovação</p>
                <p className="text-sm">Todas as faturas foram processadas</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Dialog de Confirmação */}
      <Dialog open={dialogAberto} onOpenChange={setDialogAberto}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {tipoDialog === "aprovar" ? "Aprovar Fatura" : "Rejeitar Fatura"}
            </DialogTitle>
          </DialogHeader>
          {faturaAtual && (
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold">{faturaAtual.cliente}</h4>
                <p className="text-sm text-gray-600">{faturaAtual.operadora}</p>
                <p className="text-sm">Valor: R$ {faturaAtual.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
              </div>
              
              {tipoDialog === "aprovar" ? (
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Observação (opcional)
                  </label>
                  <Textarea
                    placeholder="Adicione uma observação sobre a aprovação..."
                    value={observacao}
                    onChange={(e) => setObservacao(e.target.value)}
                  />
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Motivo da Rejeição *
                  </label>
                  <Textarea
                    placeholder="Informe o motivo da rejeição..."
                    value={motivo}
                    onChange={(e) => setMotivo(e.target.value)}
                  />
                </div>
              )}
              
              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setDialogAberto(false)}>
                  Cancelar
                </Button>
                <Button
                  onClick={confirmarAcao}
                  disabled={aprovarMutation.isPending || rejeitarMutation.isPending}
                  className={tipoDialog === "aprovar" ? "bg-green-600 hover:bg-green-700" : "bg-red-600 hover:bg-red-700"}
                >
                  {(aprovarMutation.isPending || rejeitarMutation.isPending) ? "Processando..." : 
                   (tipoDialog === "aprovar" ? "Confirmar Aprovação" : "Confirmar Rejeição")}
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}