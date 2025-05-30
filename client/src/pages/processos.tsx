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
import { Plus, Play, Pause, Square, Settings, Activity, AlertCircle } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

// Schema de validação para processos
const processoSchema = z.object({
  nome: z.string().min(1, "Nome é obrigatório"),
  operadora: z.string().min(1, "Operadora é obrigatória"),
  cliente_id: z.number().min(1, "Cliente é obrigatório"),
  tipo_execucao: z.string().min(1, "Tipo de execução é obrigatório"),
  agendamento: z.string().optional(),
  parametros: z.string().optional(),
  ativo: z.boolean(),
});

type Processo = {
  id: number;
  nome: string;
  operadora: string;
  cliente_nome: string;
  tipo_execucao: string;
  status: string;
  ultima_execucao: string;
  proxima_execucao: string;
  sucesso_rate: number;
  ativo: boolean;
};

export default function Processos() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingProcesso, setEditingProcesso] = useState<Processo | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const { toast } = useToast();

  // Configurar formulário
  const form = useForm<z.infer<typeof processoSchema>>({
    resolver: zodResolver(processoSchema),
    defaultValues: {
      nome: "",
      operadora: "",
      cliente_id: 0,
      tipo_execucao: "download",
      agendamento: "",
      parametros: "",
      ativo: true,
    },
  });

  // Query para buscar processos
  const { data: processos = [], isLoading } = useQuery({
    queryKey: ["/api/processos"],
  });

  // Query para buscar clientes (para o select)
  const { data: clientes = [] } = useQuery({
    queryKey: ["/api/clientes"],
  });

  // Filtrar processos por status
  const processosFiltrados = filterStatus === "all" 
    ? processos 
    : processos.filter((p: Processo) => p.status === filterStatus);

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: z.infer<typeof processoSchema>) =>
      apiRequest(`/api/processos`, { method: "POST", body: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/processos"] });
      toast({
        title: "Sucesso",
        description: "Processo criado com sucesso",
      });
      setDialogOpen(false);
      form.reset();
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao criar processo",
        variant: "destructive",
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<z.infer<typeof processoSchema>> }) =>
      apiRequest(`/api/processos/${id}`, { method: "PUT", body: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/processos"] });
      toast({
        title: "Sucesso",
        description: "Processo atualizado com sucesso",
      });
      setDialogOpen(false);
      setEditingProcesso(null);
      form.reset();
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao atualizar processo",
        variant: "destructive",
      });
    },
  });

  const executeMutation = useMutation({
    mutationFn: (id: number) =>
      apiRequest(`/api/processos/${id}/executar`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/processos"] });
      toast({
        title: "Sucesso",
        description: "Processo iniciado com sucesso",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao executar processo",
        variant: "destructive",
      });
    },
  });

  // Handlers
  const handleEdit = (processo: Processo) => {
    setEditingProcesso(processo);
    form.reset({
      nome: processo.nome,
      operadora: processo.operadora,
      cliente_id: 1, // Seria necessário buscar o ID real do cliente
      tipo_execucao: processo.tipo_execucao,
      agendamento: "",
      parametros: "",
      ativo: processo.ativo,
    });
    setDialogOpen(true);
  };

  const handleExecute = (id: number) => {
    if (confirm("Tem certeza que deseja executar este processo?")) {
      executeMutation.mutate(id);
    }
  };

  const onSubmit = (data: z.infer<typeof processoSchema>) => {
    if (editingProcesso) {
      updateMutation.mutate({ id: editingProcesso.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleNewProcesso = () => {
    setEditingProcesso(null);
    form.reset();
    setDialogOpen(true);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      executando: { variant: "default" as const, className: "bg-blue-100 text-blue-700 border-blue-200" },
      concluido: { variant: "default" as const, className: "bg-green-100 text-green-700 border-green-200" },
      erro: { variant: "destructive" as const, className: "bg-red-100 text-red-700 border-red-200" },
      agendado: { variant: "secondary" as const, className: "bg-yellow-100 text-yellow-700 border-yellow-200" },
      pausado: { variant: "secondary" as const, className: "bg-gray-100 text-gray-700 border-gray-200" },
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.agendado;
    return (
      <Badge variant={config.variant} className={config.className}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  return (
    <div className="p-6 space-y-6 bg-slate-50 min-h-screen">
      {/* Header com gradiente roxo */}
      <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Processos RPA</h1>
            <p className="text-purple-100 mt-2">Gerencie e monitore todos os processos de automação</p>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button 
                onClick={handleNewProcesso}
                className="bg-white text-purple-600 hover:bg-purple-50 font-semibold"
              >
                <Plus className="h-4 w-4 mr-2" />
                Novo Processo
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-4xl max-h-[95vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-xl font-semibold">
                  {editingProcesso ? "Editar Processo" : "Novo Processo"}
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="nome">Nome do Processo</Label>
                    <Input
                      id="nome"
                      {...form.register("nome")}
                      placeholder="Ex: Download Faturas Embratel"
                    />
                    {form.formState.errors.nome && (
                      <p className="text-sm text-red-500">{form.formState.errors.nome.message}</p>
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
                    <Label htmlFor="cliente_id">Cliente</Label>
                    <Select onValueChange={(value) => form.setValue("cliente_id", parseInt(value))}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione o cliente" />
                      </SelectTrigger>
                      <SelectContent>
                        {clientes.map((cliente: any) => (
                          <SelectItem key={cliente.id} value={cliente.id.toString()}>
                            {cliente.nome}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {form.formState.errors.cliente_id && (
                      <p className="text-sm text-red-500">{form.formState.errors.cliente_id.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="tipo_execucao">Tipo de Execução</Label>
                    <Select onValueChange={(value) => form.setValue("tipo_execucao", value)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione o tipo" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="download">Download de Faturas</SelectItem>
                        <SelectItem value="upload_sat">Upload para SAT</SelectItem>
                        <SelectItem value="aprovacao">Processo de Aprovação</SelectItem>
                        <SelectItem value="notificacao">Envio de Notificações</SelectItem>
                      </SelectContent>
                    </Select>
                    {form.formState.errors.tipo_execucao && (
                      <p className="text-sm text-red-500">{form.formState.errors.tipo_execucao.message}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="agendamento">Agendamento (Cron)</Label>
                    <Input
                      id="agendamento"
                      {...form.register("agendamento")}
                      placeholder="Ex: 0 9 * * 1-5 (9h, segunda a sexta)"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="parametros">Parâmetros</Label>
                    <Input
                      id="parametros"
                      {...form.register("parametros")}
                      placeholder="JSON com parâmetros específicos"
                    />
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="ativo"
                    {...form.register("ativo")}
                    className="rounded border-gray-300"
                  />
                  <Label htmlFor="ativo">Processo Ativo</Label>
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
                    className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700"
                  >
                    {createMutation.isPending || updateMutation.isPending
                      ? "Salvando..."
                      : editingProcesso
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
        <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-500 to-purple-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">{processos.length}</div>
            <div className="text-sm text-purple-100 mt-1">Total de Processos</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-500 to-blue-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {processos.filter((p: Processo) => p.status === "executando").length}
            </div>
            <div className="text-sm text-blue-100 mt-1">Em Execução</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-500 to-green-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {processos.filter((p: Processo) => p.status === "concluido").length}
            </div>
            <div className="text-sm text-green-100 mt-1">Concluídos</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-red-500 to-red-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {processos.filter((p: Processo) => p.status === "erro").length}
            </div>
            <div className="text-sm text-red-100 mt-1">Com Erro</div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card className="border-0 shadow-lg bg-white">
        <CardContent className="p-4">
          <div className="flex items-center gap-4">
            <Settings className="h-5 w-5 text-slate-600" />
            <Label>Filtrar por status:</Label>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todos</SelectItem>
                <SelectItem value="executando">Em Execução</SelectItem>
                <SelectItem value="concluido">Concluídos</SelectItem>
                <SelectItem value="erro">Com Erro</SelectItem>
                <SelectItem value="agendado">Agendados</SelectItem>
                <SelectItem value="pausado">Pausados</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de processos */}
      <Card className="border-0 shadow-lg bg-white">
        <CardHeader className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-lg">
          <CardTitle className="flex items-center text-slate-800">
            <Activity className="h-5 w-5 mr-2 text-purple-600" />
            Lista de Processos ({processosFiltrados.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Nome</TableHead>
                  <TableHead>Operadora</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Tipo</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Última Execução</TableHead>
                  <TableHead>Taxa de Sucesso</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {processosFiltrados.length > 0 ? processosFiltrados.map((processo: Processo) => (
                  <TableRow key={processo.id} className="hover:bg-slate-50/50 transition-colors">
                    <TableCell className="font-medium text-slate-600">#{processo.id}</TableCell>
                    <TableCell className="font-semibold text-slate-900">{processo.nome}</TableCell>
                    <TableCell className="text-sm text-slate-600">{processo.operadora}</TableCell>
                    <TableCell className="text-sm text-slate-600">{processo.cliente_nome}</TableCell>
                    <TableCell className="text-sm text-slate-600">{processo.tipo_execucao}</TableCell>
                    <TableCell>{getStatusBadge(processo.status)}</TableCell>
                    <TableCell className="text-sm text-slate-600">
                      {processo.ultima_execucao ? new Date(processo.ultima_execucao).toLocaleString('pt-BR') : "Nunca"}
                    </TableCell>
                    <TableCell className="text-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-600 h-2 rounded-full" 
                            style={{ width: `${processo.sucesso_rate || 0}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{processo.sucesso_rate || 0}%</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleExecute(processo.id)}
                          disabled={executeMutation.isPending || processo.status === "executando"}
                          className="h-8 px-3 text-green-600 border-green-200 hover:bg-green-50"
                        >
                          <Play className="h-4 w-4 mr-1" />
                          Executar
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(processo)}
                          className="h-8 px-3 text-blue-600 border-blue-200 hover:bg-blue-50"
                        >
                          <Settings className="h-4 w-4 mr-1" />
                          Config
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-slate-500">
                      Nenhum processo encontrado
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