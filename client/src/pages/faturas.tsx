import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import { Plus, Eye, Download, FileText, Filter } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

// Schema de validação para faturas
const faturaSchema = z.object({
  cliente: z.string().min(1, "Cliente é obrigatório"),
  operadora: z.string().min(1, "Operadora é obrigatória"),
  numero_fatura: z.string().min(1, "Número da fatura é obrigatório"),
  valor: z.number().min(0, "Valor deve ser maior que zero"),
  vencimento: z.string().min(1, "Data de vencimento é obrigatória"),
  mes_referencia: z.string().min(1, "Mês de referência é obrigatório"),
  status: z.string().min(1, "Status é obrigatório"),
});

type Fatura = {
  id: number;
  cliente: string;
  operadora: string;
  numero_fatura: string;
  valor: number;
  vencimento: string;
  mes_referencia: string;
  status: string;
  arquivo_url?: string;
};

export default function Faturas() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingFatura, setEditingFatura] = useState<Fatura | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const { toast } = useToast();

  // Configurar formulário
  const form = useForm<z.infer<typeof faturaSchema>>({
    resolver: zodResolver(faturaSchema),
    defaultValues: {
      cliente: "",
      operadora: "",
      numero_fatura: "",
      valor: 0,
      vencimento: "",
      mes_referencia: "",
      status: "pendente",
    },
  });

  // Query para buscar faturas
  const { data: faturas = [], isLoading } = useQuery({
    queryKey: ["/api/faturas"],
  });

  // Filtrar faturas por status
  const faturasFiltradas = filterStatus === "all" 
    ? faturas 
    : faturas.filter((f: Fatura) => f.status === filterStatus);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: z.infer<typeof faturaSchema>) =>
      apiRequest(`/api/faturas`, { method: "POST", body: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
      toast({
        title: "Sucesso",
        description: "Fatura criada com sucesso",
      });
      setDialogOpen(false);
      form.reset();
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao criar fatura",
        variant: "destructive",
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<z.infer<typeof faturaSchema>> }) =>
      apiRequest(`/api/faturas/${id}`, { method: "PUT", body: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
      toast({
        title: "Sucesso",
        description: "Fatura atualizada com sucesso",
      });
      setDialogOpen(false);
      setEditingFatura(null);
      form.reset();
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao atualizar fatura",
        variant: "destructive",
      });
    },
  });

  // Handlers
  const handleEdit = (fatura: Fatura) => {
    setEditingFatura(fatura);
    form.reset({
      cliente: fatura.cliente,
      operadora: fatura.operadora,
      numero_fatura: fatura.numero_fatura,
      valor: fatura.valor,
      vencimento: fatura.vencimento,
      mes_referencia: fatura.mes_referencia,
      status: fatura.status,
    });
    setDialogOpen(true);
  };

  const onSubmit = (data: z.infer<typeof faturaSchema>) => {
    if (editingFatura) {
      updateMutation.mutate({ id: editingFatura.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleNewFatura = () => {
    setEditingFatura(null);
    form.reset();
    setDialogOpen(true);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pendente: { variant: "secondary" as const, className: "bg-yellow-100 text-yellow-700 border-yellow-200" },
      aprovada: { variant: "default" as const, className: "bg-green-100 text-green-700 border-green-200" },
      rejeitada: { variant: "destructive" as const, className: "bg-red-100 text-red-700 border-red-200" },
      processando: { variant: "secondary" as const, className: "bg-blue-100 text-blue-700 border-blue-200" },
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pendente;
    return (
      <Badge variant={config.variant} className={config.className}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  return (
    <div className="p-6 space-y-6 bg-slate-50 min-h-screen">
      {/* Header com gradiente */}
      <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Faturas</h1>
            <p className="text-green-100 mt-2">Gerencie todas as faturas do sistema RPA BGTELECOM</p>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button 
                onClick={handleNewFatura}
                className="bg-white text-green-600 hover:bg-green-50 font-semibold"
              >
                <Plus className="h-4 w-4 mr-2" />
                Nova Fatura
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[95vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-xl font-semibold">
                  {editingFatura ? "Editar Fatura" : "Nova Fatura"}
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="cliente">Cliente</Label>
                    <Input
                      id="cliente"
                      {...form.register("cliente")}
                      placeholder="Nome do cliente"
                    />
                    {form.formState.errors.cliente && (
                      <p className="text-sm text-red-500">{form.formState.errors.cliente.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="operadora">Operadora</Label>
                    <Select onValueChange={(value) => form.setValue("operadora", value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione a operadora" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="EMBRATEL">EMBRATEL</SelectItem>
                        <SelectItem value="VIVO">VIVO</SelectItem>
                        <SelectItem value="OI">OI</SelectItem>
                        <SelectItem value="AZUTON">AZUTON</SelectItem>
                        <SelectItem value="DIGITALNET">DIGITALNET</SelectItem>
                        <SelectItem value="SAT">SAT</SelectItem>
                      </SelectContent>
                    </Select>
                    {form.formState.errors.operadora && (
                      <p className="text-sm text-red-500">{form.formState.errors.operadora.message}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="numero_fatura">Número da Fatura</Label>
                    <Input
                      id="numero_fatura"
                      {...form.register("numero_fatura")}
                      placeholder="Ex: 123456789"
                    />
                    {form.formState.errors.numero_fatura && (
                      <p className="text-sm text-red-500">{form.formState.errors.numero_fatura.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="valor">Valor (R$)</Label>
                    <Input
                      id="valor"
                      type="number"
                      step="0.01"
                      {...form.register("valor", { valueAsNumber: true })}
                      placeholder="0.00"
                    />
                    {form.formState.errors.valor && (
                      <p className="text-sm text-red-500">{form.formState.errors.valor.message}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="vencimento">Data de Vencimento</Label>
                    <Input
                      id="vencimento"
                      type="date"
                      {...form.register("vencimento")}
                    />
                    {form.formState.errors.vencimento && (
                      <p className="text-sm text-red-500">{form.formState.errors.vencimento.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="mes_referencia">Mês de Referência</Label>
                    <Input
                      id="mes_referencia"
                      {...form.register("mes_referencia")}
                      placeholder="Ex: 2024-12"
                    />
                    {form.formState.errors.mes_referencia && (
                      <p className="text-sm text-red-500">{form.formState.errors.mes_referencia.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="status">Status</Label>
                    <Select onValueChange={(value) => form.setValue("status", value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione o status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pendente">Pendente</SelectItem>
                        <SelectItem value="aprovada">Aprovada</SelectItem>
                        <SelectItem value="rejeitada">Rejeitada</SelectItem>
                        <SelectItem value="processando">Processando</SelectItem>
                      </SelectContent>
                    </Select>
                    {form.formState.errors.status && (
                      <p className="text-sm text-red-500">{form.formState.errors.status.message}</p>
                    )}
                  </div>
                </div>

                <div className="flex justify-end space-x-2 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setDialogOpen(false)}
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    disabled={createMutation.isPending || updateMutation.isPending}
                    className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
                  >
                    {createMutation.isPending || updateMutation.isPending
                      ? "Salvando..."
                      : editingFatura
                      ? "Atualizar"
                      : "Criar"}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-500 to-green-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">{faturas.length}</div>
            <div className="text-sm text-green-100 mt-1">Total de Faturas</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-yellow-500 to-yellow-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {faturas.filter((f: Fatura) => f.status === "pendente").length}
            </div>
            <div className="text-sm text-yellow-100 mt-1">Pendentes</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-emerald-500 to-emerald-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {faturas.filter((f: Fatura) => f.status === "aprovada").length}
            </div>
            <div className="text-sm text-emerald-100 mt-1">Aprovadas</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-red-500 to-red-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              R$ {faturas.reduce((total: number, f: Fatura) => total + f.valor, 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </div>
            <div className="text-sm text-red-100 mt-1">Valor Total</div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card className="border-0 shadow-lg bg-white">
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <Filter className="h-5 w-5 text-slate-600" />
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
                <SelectItem value="processando">Processando</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de faturas */}
      <Card className="border-0 shadow-lg bg-white">
        <CardHeader className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-lg">
          <CardTitle className="flex items-center text-slate-800">
            <FileText className="h-5 w-5 mr-2 text-green-600" />
            Lista de Faturas ({faturasFiltradas.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Operadora</TableHead>
                  <TableHead>Número</TableHead>
                  <TableHead>Valor</TableHead>
                  <TableHead>Vencimento</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {faturasFiltradas.length > 0 ? faturasFiltradas.map((fatura: Fatura) => (
                  <TableRow key={fatura.id} className="hover:bg-slate-50/50 transition-colors">
                    <TableCell className="font-medium text-slate-600">#{fatura.id}</TableCell>
                    <TableCell className="font-semibold text-slate-900">{fatura.cliente}</TableCell>
                    <TableCell className="text-sm text-slate-600">{fatura.operadora}</TableCell>
                    <TableCell className="font-mono text-sm text-slate-600">{fatura.numero_fatura}</TableCell>
                    <TableCell className="font-semibold text-green-600">
                      R$ {fatura.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </TableCell>
                    <TableCell className="text-sm text-slate-600">
                      {new Date(fatura.vencimento).toLocaleDateString('pt-BR')}
                    </TableCell>
                    <TableCell>{getStatusBadge(fatura.status)}</TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(fatura)}
                          className="h-8 px-3 text-blue-600 border-blue-200 hover:bg-blue-50"
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          Ver
                        </Button>
                        {fatura.arquivo_url && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="h-8 px-3 text-green-600 border-green-200 hover:bg-green-50"
                          >
                            <Download className="h-4 w-4 mr-1" />
                            Download
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-slate-500">
                      Nenhuma fatura encontrada
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}