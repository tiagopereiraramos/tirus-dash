import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Check, X, Eye, Clock, AlertCircle } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

export default function Aprovacoes() {
  const [statusFilter, setStatusFilter] = useState<string>("pendente");
  const [selectedFatura, setSelectedFatura] = useState<any>(null);
  const [motivoRejeicao, setMotivoRejeicao] = useState("");
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: faturas, isLoading } = useQuery({
    queryKey: ["/api/faturas", { statusAprovacao: statusFilter }],
  });

  const aprovarMutation = useMutation({
    mutationFn: (faturaId: number) => 
      apiRequest("PATCH", `/api/faturas/${faturaId}/aprovar`, { aprovadoPor: 1 }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
      toast({
        title: "Fatura Aprovada",
        description: "A fatura foi aprovada e seguirá para pagamento",
      });
    },
    onError: () => {
      toast({
        title: "Erro",
        description: "Falha ao aprovar fatura",
        variant: "destructive",
      });
    },
  });

  const rejeitarMutation = useMutation({
    mutationFn: ({ faturaId, motivo }: { faturaId: number; motivo: string }) =>
      apiRequest("PATCH", `/api/faturas/${faturaId}/rejeitar`, { motivoRejeicao: motivo }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
      setMotivoRejeicao("");
      setSelectedFatura(null);
      toast({
        title: "Fatura Rejeitada",
        description: "A fatura foi rejeitada e o cliente será notificado",
      });
    },
    onError: () => {
      toast({
        title: "Erro",
        description: "Falha ao rejeitar fatura",
        variant: "destructive",
      });
    },
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "aprovada":
        return <Badge className="status-success">Aprovada</Badge>;
      case "rejeitada":
        return <Badge className="status-error">Rejeitada</Badge>;
      case "pendente":
        return <Badge className="status-warning">Pendente</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatCurrency = (value: string | number) => {
    const numValue = typeof value === "string" ? parseFloat(value) : value;
    return new Intl.NumberFormat("pt-BR", {
      style: "currency",
      currency: "BRL",
    }).format(numValue || 0);
  };

  const handleAprovar = (faturaId: number) => {
    aprovarMutation.mutate(faturaId);
  };

  const handleRejeitar = () => {
    if (selectedFatura && motivoRejeicao.trim()) {
      rejeitarMutation.mutate({
        faturaId: selectedFatura.id,
        motivo: motivoRejeicao,
      });
    }
  };

  const pendingCount = faturas?.data?.filter((f: any) => f.statusAprovacao === "pendente").length || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-foreground">Aprovação de Faturas</h2>
        <p className="text-muted-foreground">
          Gerencie e aprove as faturas processadas pelos RPAs
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Pendentes</p>
                <p className="text-2xl font-bold text-foreground">{pendingCount}</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg flex items-center justify-center">
                <Clock className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Aprovadas Hoje</p>
                <p className="text-2xl font-bold text-foreground">18</p>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                <Check className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Rejeitadas</p>
                <p className="text-2xl font-bold text-foreground">3</p>
              </div>
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/20 rounded-lg flex items-center justify-center">
                <X className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Valor Total</p>
                <p className="text-2xl font-bold text-foreground">R$ 45.280</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                <AlertCircle className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Status de Aprovação" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos</SelectItem>
                <SelectItem value="pendente">Pendente</SelectItem>
                <SelectItem value="aprovada">Aprovada</SelectItem>
                <SelectItem value="rejeitada">Rejeitada</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Faturas Table */}
      <Card>
        <CardHeader>
          <CardTitle>Faturas para Aprovação</CardTitle>
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
                <TableHead>Recebido</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {faturas?.data?.map((fatura: any) => (
                <TableRow key={fatura.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div>
                      <div className="font-medium text-sm">
                        {fatura.contrato?.cliente?.nomeSat || "Cliente"}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {fatura.contrato?.cliente?.cnpj}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {fatura.contrato?.operadora?.nome || "N/A"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="font-medium">
                      {formatCurrency(fatura.valor)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      {fatura.dataVencimento 
                        ? format(new Date(fatura.dataVencimento), "dd/MM/yyyy", { locale: ptBR })
                        : "-"
                      }
                    </div>
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(fatura.statusAprovacao)}
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      {fatura.createdAt 
                        ? format(new Date(fatura.createdAt), "dd/MM HH:mm", { locale: ptBR })
                        : "-"
                      }
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      {fatura.statusAprovacao === "pendente" && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleAprovar(fatura.id)}
                            disabled={aprovarMutation.isPending}
                            className="text-green-600 hover:text-green-700 hover:bg-green-50 dark:hover:bg-green-900/20"
                          >
                            <Check className="h-4 w-4" />
                          </Button>
                          <Dialog>
                            <DialogTrigger asChild>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setSelectedFatura(fatura)}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20"
                              >
                                <X className="h-4 w-4" />
                              </Button>
                            </DialogTrigger>
                            <DialogContent>
                              <DialogHeader>
                                <DialogTitle>Rejeitar Fatura</DialogTitle>
                                <DialogDescription>
                                  Informe o motivo da rejeição da fatura. Esta informação será enviada ao cliente.
                                </DialogDescription>
                              </DialogHeader>
                              <div className="space-y-4">
                                <div>
                                  <label className="text-sm font-medium">Cliente:</label>
                                  <p className="text-sm text-muted-foreground">
                                    {selectedFatura?.contrato?.cliente?.nomeSat}
                                  </p>
                                </div>
                                <div>
                                  <label className="text-sm font-medium">Valor:</label>
                                  <p className="text-sm text-muted-foreground">
                                    {formatCurrency(selectedFatura?.valor || 0)}
                                  </p>
                                </div>
                                <div>
                                  <label className="text-sm font-medium">Motivo da Rejeição:</label>
                                  <Textarea
                                    value={motivoRejeicao}
                                    onChange={(e) => setMotivoRejeicao(e.target.value)}
                                    placeholder="Digite o motivo da rejeição..."
                                    className="mt-1"
                                  />
                                </div>
                              </div>
                              <DialogFooter>
                                <Button variant="outline" onClick={() => setSelectedFatura(null)}>
                                  Cancelar
                                </Button>
                                <Button
                                  onClick={handleRejeitar}
                                  disabled={!motivoRejeicao.trim() || rejeitarMutation.isPending}
                                  variant="destructive"
                                >
                                  Rejeitar Fatura
                                </Button>
                              </DialogFooter>
                            </DialogContent>
                          </Dialog>
                        </>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
