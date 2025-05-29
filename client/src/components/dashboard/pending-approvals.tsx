import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Check, X, Clock, AlertTriangle } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";

export default function PendingApprovals() {
  const [selectedFatura, setSelectedFatura] = useState<any>(null);
  const [motivoRejeicao, setMotivoRejeicao] = useState("");
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: faturas, isLoading } = useQuery({
    queryKey: ["/api/faturas", { statusAprovacao: "pendente", limit: 5 }],
  });

  const aprovarMutation = useMutation({
    mutationFn: (faturaId: number) => 
      apiRequest("PATCH", `/api/faturas/${faturaId}/aprovar`, { aprovadoPor: 1 }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
      queryClient.invalidateQueries({ queryKey: ["/api/dashboard/metrics"] });
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
      queryClient.invalidateQueries({ queryKey: ["/api/dashboard/metrics"] });
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

  const getOperadoraBadge = (operadora: string) => {
    const colors: Record<string, string> = {
      "EMBRATEL": "bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300",
      "VIVO": "bg-purple-100 text-purple-800 dark:bg-purple-900/20 dark:text-purple-300",
      "DIGITALNET": "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300",
      "AZUTON": "bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-300",
      "OI": "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300",
    };
    
    return colors[operadora] || "bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300";
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Aprovações Pendentes
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Aprovações Pendentes
          </CardTitle>
          <Button variant="outline" size="sm">
            Ver todas
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {!faturas?.data?.length ? (
          <div className="text-center py-8">
            <AlertTriangle className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">
              Nenhuma aprovação pendente
            </h3>
            <p className="text-sm text-muted-foreground">
              Todas as faturas foram processadas
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {faturas.data.slice(0, 3).map((fatura: any) => (
              <div
                key={fatura.id}
                className="border border-border rounded-lg p-4 hover:bg-muted/30 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-sm font-medium text-foreground">
                        {fatura.contrato?.cliente?.nomeSat || "Cliente Não Identificado"}
                      </span>
                      <Badge 
                        className={`text-xs ${getOperadoraBadge(fatura.contrato?.operadora?.nome || "")}`}
                        variant="outline"
                      >
                        {fatura.contrato?.operadora?.nome}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-1">
                      Fatura: {formatCurrency(fatura.valor || 0)}
                      {fatura.dataVencimento && (
                        <span className="ml-2">
                          • Venc: {format(new Date(fatura.dataVencimento), "dd/MM/yyyy", { locale: ptBR })}
                        </span>
                      )}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {fatura.createdAt 
                        ? `Há ${Math.floor((Date.now() - new Date(fatura.createdAt).getTime()) / (1000 * 60 * 60))} horas`
                        : "Recebido recentemente"
                      }
                    </p>
                  </div>
                  <div className="flex space-x-2 ml-4">
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
                            Informe o motivo da rejeição. Esta informação será enviada ao cliente.
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
                            {rejeitarMutation.isPending ? "Rejeitando..." : "Rejeitar Fatura"}
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleAprovar(fatura.id)}
                      disabled={aprovarMutation.isPending}
                      className="text-green-600 hover:text-green-700 hover:bg-green-50 dark:hover:bg-green-900/20"
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            
            {faturas?.data?.length > 3 && (
              <div className="text-center pt-2">
                <Button variant="outline" size="sm">
                  Ver mais {faturas.data.length - 3} aprovações
                </Button>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
