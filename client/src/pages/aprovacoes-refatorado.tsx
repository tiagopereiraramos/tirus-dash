import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { CheckCircle, XCircle, Clock, Search, FileCheck } from "lucide-react";
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

export default function Aprovacoes() {
  const { toast } = useToast();
  const [busca, setBusca] = useState<string>("");
  const [observacao, setObservacao] = useState<string>("");
  const [motivo, setMotivo] = useState<string>("");
  const [dialogAberto, setDialogAberto] = useState(false);
  const [tipoDialog, setTipoDialog] = useState<"aprovar" | "rejeitar">("aprovar");
  const [faturaAtual, setFaturaAtual] = useState<Fatura | null>(null);

  const { data: faturasResponse, isLoading: loadingFaturas } = useQuery({ 
    queryKey: ["/api/faturas"] 
  });

  const aprovarMutation = useMutation({
    mutationFn: (data: { id: number; observacao: string }) => 
      apiRequest(`/api/aprovacoes/${data.id}/aprovar`, { 
        method: "POST", 
        body: JSON.stringify({ observacao: data.observacao }),
        headers: { 'Content-Type': 'application/json' }
      }),
    onSuccess: () => {
      toast({
        title: "Fatura aprovada",
        description: "A fatura foi aprovada com sucesso.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
      setDialogAberto(false);
      setObservacao("");
      setFaturaAtual(null);
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
        body: JSON.stringify({ motivo: data.motivo }),
        headers: { 'Content-Type': 'application/json' }
      }),
    onSuccess: () => {
      toast({
        title: "Fatura rejeitada",
        description: "A fatura foi rejeitada com sucesso.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
      setDialogAberto(false);
      setMotivo("");
      setFaturaAtual(null);
    },
    onError: () => {
      toast({
        title: "Erro na rejeição",
        description: "Ocorreu um erro ao rejeitar a fatura.",
        variant: "destructive",
      });
    },
  });

  const faturas = Array.isArray(faturasResponse) ? faturasResponse : [];
  
  const faturasPendentes = faturas.filter((fatura) => {
    const isPendente = fatura.status === "pendente";
    const matchBusca = !busca || 
      fatura.cliente.toLowerCase().includes(busca.toLowerCase()) ||
      fatura.operadora.toLowerCase().includes(busca.toLowerCase());
    
    return isPendente && matchBusca;
  });

  const handleAprovar = (fatura: Fatura) => {
    setFaturaAtual(fatura);
    setTipoDialog("aprovar");
    setDialogAberto(true);
  };

  const handleRejeitar = (fatura: Fatura) => {
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
          <h1 className="text-3xl font-bold tracking-tight">Aprovações de Faturas</h1>
          <p className="text-muted-foreground">
            Gerencie aprovações e rejeições de faturas pendentes
          </p>
        </div>
      </div>

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pendentes</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{faturasPendentes.length}</div>
            <p className="text-xs text-muted-foreground">
              Aguardando aprovação
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Aprovadas</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {faturas.filter(f => f.status === "aprovada").length}
            </div>
            <p className="text-xs text-muted-foreground">
              Total aprovadas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Valor Pendente</CardTitle>
            <FileCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              R$ {faturasPendentes.reduce((acc, f) => acc + f.valor, 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </div>
            <p className="text-xs text-muted-foreground">
              Total a aprovar
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filtro de Busca */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Buscar Faturas
          </CardTitle>
          <CardDescription>
            Encontre faturas específicas por cliente ou operadora
          </CardDescription>
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

      {/* Tabela de Faturas Pendentes */}
      <Card>
        <CardHeader>
          <CardTitle>
            Faturas Pendentes de Aprovação ({faturasPendentes.length})
          </CardTitle>
          <CardDescription>
            {faturasPendentes.length === 0 ? "Não há faturas pendentes de aprovação" : 
             `${faturasPendentes.length} faturas aguardando sua análise`}
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
                {faturasPendentes.map((fatura) => (
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
                      <Badge className="bg-yellow-100 text-yellow-800">
                        <Clock className="h-3 w-3 mr-1" />
                        Pendente
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right space-x-2">
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
                    </TableCell>
                  </TableRow>
                ))}
                {faturasPendentes.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                      <FileCheck className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                      <p>Nenhuma fatura pendente de aprovação</p>
                      <p className="text-sm">Todas as faturas foram processadas</p>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
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
            <DialogDescription>
              {tipoDialog === "aprovar" 
                ? "Confirme a aprovação desta fatura. Você pode adicionar observações opcionais."
                : "Informe o motivo da rejeição desta fatura."}
            </DialogDescription>
          </DialogHeader>
          {faturaAtual && (
            <div className="space-y-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold">{faturaAtual.cliente}</h4>
                <p className="text-sm text-gray-600">{faturaAtual.operadora}</p>
                <p className="text-sm">Valor: R$ {faturaAtual.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</p>
                <p className="text-sm">Vencimento: {faturaAtual.vencimento}</p>
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
            </div>
          )}
          <DialogFooter>
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
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}