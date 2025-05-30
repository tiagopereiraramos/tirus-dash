import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Download, Clock, CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";

interface Fatura {
  id: number;
  cliente: string;
  operadora: string;
  valor: number;
  vencimento: string;
  status: string;
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

export default function Faturas() {
  const { toast } = useToast();
  const [filtroOperadora, setFiltroOperadora] = useState<string>("");
  const [filtroStatus, setFiltroStatus] = useState<string>("");
  const [busca, setBusca] = useState<string>("");

  const { data: faturasResponse, isLoading: loadingFaturas } = useQuery<FaturasResponse>({ 
    queryKey: ["/api/faturas"] 
  });

  const { data: operadoras, isLoading: loadingOperadoras } = useQuery<Operadora[]>({ 
    queryKey: ["/api/operadoras"] 
  });

  const downloadMutation = useMutation({
    mutationFn: (faturaId: number) => apiRequest(`/api/faturas/${faturaId}/download`, { method: "POST" }),
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

  const faturasData = Array.isArray(faturasResponse) ? faturasResponse : (faturasResponse?.data || []);

  const faturasFiltradas = faturasData.filter((fatura) => {
    const matchOperadora = !filtroOperadora || fatura.operadora === filtroOperadora;
    const matchStatus = !filtroStatus || fatura.status === filtroStatus;
    const matchBusca = !busca || 
      fatura.cliente.toLowerCase().includes(busca.toLowerCase()) ||
      fatura.operadora.toLowerCase().includes(busca.toLowerCase());
    
    return matchOperadora && matchStatus && matchBusca;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case "AGUARDANDO_DOWNLOAD": return "bg-yellow-100 text-yellow-800";
      case "FATURA_BAIXADA": return "bg-blue-100 text-blue-800";
      case "PENDENTE_APROVACAO": return "bg-orange-100 text-orange-800";
      case "APROVADA": return "bg-green-100 text-green-800";
      case "REJEITADA": return "bg-red-100 text-red-800";
      case "ENVIADA_SAT": return "bg-purple-100 text-purple-800";
      case "ERRO": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "AGUARDANDO_DOWNLOAD": return <Clock className="h-4 w-4" />;
      case "FATURA_BAIXADA": return <Download className="h-4 w-4" />;
      case "APROVADA": return <CheckCircle className="h-4 w-4" />;
      case "REJEITADA": return <XCircle className="h-4 w-4" />;
      case "ERRO": return <AlertTriangle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  if (loadingFaturas || loadingOperadoras) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Carregando faturas...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Faturas</h1>
          <p className="text-muted-foreground mt-2">
            Gerencie e acompanhe as faturas de telecomunicações
          </p>
        </div>
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
                  <SelectValue placeholder="Todos os status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todos">Todos os status</SelectItem>
                  <SelectItem value="AGUARDANDO_DOWNLOAD">Aguardando Download</SelectItem>
                  <SelectItem value="FATURA_BAIXADA">Fatura Baixada</SelectItem>
                  <SelectItem value="PENDENTE_APROVACAO">Pendente Aprovação</SelectItem>
                  <SelectItem value="APROVADA">Aprovada</SelectItem>
                  <SelectItem value="REJEITADA">Rejeitada</SelectItem>
                  <SelectItem value="ENVIADA_SAT">Enviada SAT</SelectItem>
                  <SelectItem value="ERRO">Erro</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Faturas */}
      <Card>
        <CardHeader>
          <CardTitle>Faturas ({faturasFiltradas.length})</CardTitle>
          <CardDescription>
            Lista de todas as faturas do sistema
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
              {faturasFiltradas.map((fatura) => (
                <TableRow key={fatura.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{fatura.nome_sat}</div>
                      {fatura.observacoes && (
                        <div className="text-sm text-muted-foreground">{fatura.observacoes}</div>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>{fatura.operadora_nome}</TableCell>
                  <TableCell>{fatura.mes_ano}</TableCell>
                  <TableCell>
                    R$ {fatura.valor_fatura.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(fatura.status_processo)}>
                      <div className="flex items-center gap-1">
                        {getStatusIcon(fatura.status_processo)}
                        {fatura.status_processo.replace(/_/g, ' ')}
                      </div>
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => downloadMutation.mutate(fatura.id)}
                        disabled={downloadMutation.isPending}
                      >
                        <Download className="h-4 w-4 mr-1" />
                        Download
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
              {faturasFiltradas.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                    Nenhuma fatura encontrada
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