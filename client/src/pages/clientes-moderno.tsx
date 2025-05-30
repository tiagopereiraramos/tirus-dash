import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
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
import { Plus, Edit, Trash2, Users } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

// Schema de validação para clientes
const clienteSchema = z.object({
  nome: z.string().min(1, "Nome é obrigatório"),
  cnpj: z.string().min(14, "CNPJ deve ter pelo menos 14 caracteres"),
  email: z.string().email("Email inválido"),
  telefone: z.string().min(1, "Telefone é obrigatório"),
  endereco: z.string().min(1, "Endereço é obrigatório"),
  cidade: z.string().min(1, "Cidade é obrigatória"),
  estado: z.string().min(2, "Estado deve ter 2 caracteres").max(2, "Estado deve ter 2 caracteres"),
  cep: z.string().min(8, "CEP deve ter pelo menos 8 caracteres"),
  status_ativo: z.boolean(),
});

type Cliente = {
  id: number;
  nome: string;
  cnpj: string;
  email: string;
  telefone: string;
  endereco: string;
  cidade: string;
  estado: string;
  cep: string;
  status_ativo: boolean;
};

export default function ClientesModerno() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCliente, setEditingCliente] = useState<Cliente | null>(null);
  const { toast } = useToast();

  // Configurar formulário
  const form = useForm<z.infer<typeof clienteSchema>>({
    resolver: zodResolver(clienteSchema),
    defaultValues: {
      nome: "",
      cnpj: "",
      email: "",
      telefone: "",
      endereco: "",
      cidade: "",
      estado: "",
      cep: "",
      status_ativo: true,
    },
  });

  // Query para buscar clientes
  const { data: clientes = [], isLoading } = useQuery({
    queryKey: ["/api/clientes"],
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: z.infer<typeof clienteSchema>) =>
      apiRequest(`/api/clientes`, { method: "POST", body: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/clientes"] });
      toast({
        title: "Sucesso",
        description: "Cliente criado com sucesso",
      });
      setDialogOpen(false);
      form.reset();
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao criar cliente",
        variant: "destructive",
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<z.infer<typeof clienteSchema>> }) =>
      apiRequest(`/api/clientes/${id}`, { method: "PUT", body: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/clientes"] });
      toast({
        title: "Sucesso",
        description: "Cliente atualizado com sucesso",
      });
      setDialogOpen(false);
      setEditingCliente(null);
      form.reset();
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao atualizar cliente",
        variant: "destructive",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) =>
      apiRequest(`/api/clientes/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/clientes"] });
      queryClient.refetchQueries({ queryKey: ["/api/clientes"] });
      toast({
        title: "Sucesso",
        description: "Cliente deletado com sucesso",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao deletar cliente",
        variant: "destructive",
      });
    },
  });

  // Handlers
  const handleEdit = (cliente: Cliente) => {
    setEditingCliente(cliente);
    form.reset({
      nome: cliente.nome,
      cnpj: cliente.cnpj,
      email: cliente.email,
      telefone: cliente.telefone,
      endereco: cliente.endereco,
      cidade: cliente.cidade,
      estado: cliente.estado,
      cep: cliente.cep,
      status_ativo: cliente.status_ativo,
    });
    setDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    if (confirm("Tem certeza que deseja deletar este cliente?")) {
      deleteMutation.mutate(id);
    }
  };

  const onSubmit = (data: z.infer<typeof clienteSchema>) => {
    if (editingCliente) {
      updateMutation.mutate({ id: editingCliente.id, data });
    } else {
      createMutation.mutate(data);
    }
  };

  const handleNewCliente = () => {
    setEditingCliente(null);
    form.reset();
    setDialogOpen(true);
  };

  return (
    <div className="p-6 space-y-6 bg-slate-50 min-h-screen">
      {/* Header com gradiente azul */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Clientes</h1>
            <p className="text-blue-100 mt-2">Gerencie os clientes do sistema RPA BGTELECOM</p>
          </div>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button 
                onClick={handleNewCliente}
                className="bg-white text-blue-600 hover:bg-blue-50 font-semibold"
              >
                <Plus className="h-4 w-4 mr-2" />
                Novo Cliente
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-5xl max-h-[95vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-xl font-semibold">
                  {editingCliente ? "Editar Cliente" : "Novo Cliente"}
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="nome">Nome</Label>
                    <Input
                      id="nome"
                      {...form.register("nome")}
                      placeholder="Nome do cliente"
                    />
                    {form.formState.errors.nome && (
                      <p className="text-sm text-red-500">{form.formState.errors.nome.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cnpj">CNPJ</Label>
                    <Input
                      id="cnpj"
                      {...form.register("cnpj")}
                      placeholder="00.000.000/0000-00"
                    />
                    {form.formState.errors.cnpj && (
                      <p className="text-sm text-red-500">{form.formState.errors.cnpj.message}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      {...form.register("email")}
                      placeholder="email@empresa.com"
                    />
                    {form.formState.errors.email && (
                      <p className="text-sm text-red-500">{form.formState.errors.email.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="telefone">Telefone</Label>
                    <Input
                      id="telefone"
                      {...form.register("telefone")}
                      placeholder="(11) 99999-9999"
                    />
                    {form.formState.errors.telefone && (
                      <p className="text-sm text-red-500">{form.formState.errors.telefone.message}</p>
                    )}
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="endereco">Endereço</Label>
                  <Input
                    id="endereco"
                    {...form.register("endereco")}
                    placeholder="Rua, número, complemento"
                  />
                  {form.formState.errors.endereco && (
                    <p className="text-sm text-red-500">{form.formState.errors.endereco.message}</p>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="cidade">Cidade</Label>
                    <Input
                      id="cidade"
                      {...form.register("cidade")}
                      placeholder="São Paulo"
                    />
                    {form.formState.errors.cidade && (
                      <p className="text-sm text-red-500">{form.formState.errors.cidade.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="estado">Estado</Label>
                    <Input
                      id="estado"
                      {...form.register("estado")}
                      placeholder="SP"
                      maxLength={2}
                      className="uppercase"
                    />
                    {form.formState.errors.estado && (
                      <p className="text-sm text-red-500">{form.formState.errors.estado.message}</p>
                    )}
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cep">CEP</Label>
                    <Input
                      id="cep"
                      {...form.register("cep")}
                      placeholder="01234-567"
                    />
                    {form.formState.errors.cep && (
                      <p className="text-sm text-red-500">{form.formState.errors.cep.message}</p>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="status_ativo"
                    checked={form.watch("status_ativo")}
                    onCheckedChange={(checked) => form.setValue("status_ativo", checked)}
                  />
                  <Label htmlFor="status_ativo">Cliente Ativo</Label>
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
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  >
                    {createMutation.isPending || updateMutation.isPending
                      ? "Salvando..."
                      : editingCliente
                      ? "Atualizar"
                      : "Criar"}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Cards de estatísticas com gradientes */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-500 to-blue-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">{clientes.length}</div>
            <div className="text-sm text-blue-100 mt-1">Total de Clientes</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-500 to-green-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {clientes.filter((c: Cliente) => c.status_ativo).length}
            </div>
            <div className="text-sm text-green-100 mt-1">Clientes Ativos</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-red-500 to-red-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {clientes.filter((c: Cliente) => !c.status_ativo).length}
            </div>
            <div className="text-sm text-red-100 mt-1">Clientes Inativos</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-500 to-purple-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {new Set(clientes.map((c: Cliente) => c.cidade)).size}
            </div>
            <div className="text-sm text-purple-100 mt-1">Cidades Diferentes</div>
          </CardContent>
        </Card>
      </div>

      {/* Tabela de clientes com design moderno */}
      <Card className="border-0 shadow-lg bg-white">
        <CardHeader className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-lg">
          <CardTitle className="flex items-center text-slate-800">
            <Users className="h-5 w-5 mr-2 text-blue-600" />
            Lista de Clientes ({clientes.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Nome</TableHead>
                  <TableHead>CNPJ</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Telefone</TableHead>
                  <TableHead>Cidade/Estado</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {clientes.length > 0 ? clientes.map((cliente: Cliente) => (
                  <TableRow key={cliente.id} className="hover:bg-slate-50/50 transition-colors">
                    <TableCell className="font-medium text-slate-600">#{cliente.id}</TableCell>
                    <TableCell className="font-semibold text-slate-900">{cliente.nome}</TableCell>
                    <TableCell className="font-mono text-sm text-slate-600">{cliente.cnpj}</TableCell>
                    <TableCell className="text-sm text-slate-600">{cliente.email}</TableCell>
                    <TableCell className="text-sm text-slate-600">{cliente.telefone}</TableCell>
                    <TableCell className="text-sm text-slate-600">{cliente.cidade}/{cliente.estado}</TableCell>
                    <TableCell>
                      <Badge
                        variant={cliente.status_ativo ? "default" : "secondary"}
                        className={
                          cliente.status_ativo
                            ? "bg-green-100 text-green-700 hover:bg-green-200 border-green-200"
                            : "bg-red-100 text-red-700 hover:bg-red-200 border-red-200"
                        }
                      >
                        {cliente.status_ativo ? "Ativo" : "Inativo"}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(cliente)}
                          className="h-8 px-3 text-blue-600 border-blue-200 hover:bg-blue-50"
                        >
                          <Edit className="h-4 w-4 mr-1" />
                          Editar
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(cliente.id)}
                          disabled={deleteMutation.isPending}
                          className="h-8 px-3 text-red-600 border-red-200 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4 mr-1" />
                          Excluir
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-slate-500">
                      Nenhum cliente cadastrado
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