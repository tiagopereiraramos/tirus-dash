import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Search, Download, FileText, Calendar, DollarSign } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";

interface Fatura {
  id: number;
  cliente: string;
  operadora: string;
  valor: number;
  vencimento: string;
  status: string;
}

export default function Faturas() {
  const [busca, setBusca] = useState("");
  const [filtroStatus, setFiltroStatus] = useState("");
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: faturasResponse, isLoading } = useQuery({
    queryKey: ["/api/faturas"],
    retry: false,
  });

  const downloadMutation = useMutation({
    mutationFn: (faturaId: number) => 
      apiRequest(`/api/faturas/${faturaId}/download`, { method: "POST" }),
    onSuccess: () => {
      toast({
        title: "Download iniciado",
        description: "O download da fatura foi iniciado com sucesso.",
      });
    },
    onError: () => {
      toast({
        title: "Erro no download",
        description: "Ocorreu um erro ao iniciar o download da fatura.",
        variant: "destructive",
      });
    },
  });

  const faturas = Array.isArray(faturasResponse) ? faturasResponse : [];

  const faturasFiltradas = faturas.filter((fatura) => {
    const matchBusca = !busca || 
      fatura.cliente.toLowerCase().includes(busca.toLowerCase()) ||
      fatura.operadora.toLowerCase().includes(busca.toLowerCase());
    const matchStatus = !filtroStatus || fatura.status === filtroStatus;
    
    return matchBusca && matchStatus;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "aprovada": return "bg-green-100 text-green-800";
      case "pendente": return "bg-yellow-100 text-yellow-800";
      case "processando": return "bg-blue-100 text-blue-800";
      case "rejeitada": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
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
        <h1 className="text-3xl font-bold text-gray-900">Gestão de Faturas</h1>
        <p className="text-gray-600 mt-2">Acompanhe e gerencie todas as faturas do sistema</p>
      </div>

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-0 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total de Faturas</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{faturas.length}</p>
              </div>
              <div className="p-3 rounded-full bg-blue-50">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Pendentes</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  {faturas.filter(f => f.status === "pendente").length}
                </p>
              </div>
              <div className="p-3 rounded-full bg-yellow-50">
                <Calendar className="h-6 w-6 text-yellow-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-0 shadow-sm">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Valor Total</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">
                  R$ {faturas.reduce((acc, f) => acc + f.valor, 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div className="p-3 rounded-full bg-green-50">
                <DollarSign className="h-6 w-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card className="border-0 shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-semibold">Filtros</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Buscar por cliente ou operadora..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={filtroStatus} onValueChange={setFiltroStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Filtrar por status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">Todos os status</SelectItem>
                <SelectItem value="pendente">Pendente</SelectItem>
                <SelectItem value="aprovada">Aprovada</SelectItem>
                <SelectItem value="processando">Processando</SelectItem>
                <SelectItem value="rejeitada">Rejeitada</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Faturas */}
      <Card className="border-0 shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg font-semibold">
            Lista de Faturas ({faturasFiltradas.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {faturasFiltradas.map((fatura) => (
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
                      <Badge className={`text-xs ${getStatusColor(fatura.status)}`}>
                        {fatura.status.charAt(0).toUpperCase() + fatura.status.slice(1)}
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
                      onClick={() => downloadMutation.mutate(fatura.id)}
                      disabled={downloadMutation.isPending}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      {downloadMutation.isPending ? "Baixando..." : "Download"}
                    </Button>
                  </div>
                </div>
              </div>
            ))}
            
            {faturasFiltradas.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Nenhuma fatura encontrada</p>
                <p className="text-sm">Ajuste os filtros para ver mais resultados</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}