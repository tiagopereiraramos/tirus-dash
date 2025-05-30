import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, Building2, Edit, Trash2, Settings, ExternalLink, CheckCircle, XCircle } from "lucide-react";
import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";

interface Operadora {
  id: number;
  nome: string;
  codigo: string;
  tipo: string;
  url_login: string;
  status: string;
  possui_rpa: boolean;
  status_ativo: boolean;
}

const operadoraSchema = z.object({
  nome: z.string().min(1, "Nome é obrigatório"),
  codigo: z.string().min(2, "Código deve ter pelo menos 2 caracteres"),
  tipo: z.string().min(1, "Tipo é obrigatório"),
  url_login: z.string().url("URL deve ser válida"),
  possui_rpa: z.boolean().default(false),
  status_ativo: z.boolean().default(true),
});

export default function Operadoras() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingOperadora, setEditingOperadora] = useState<Operadora | null>(null);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: operadorasData, isLoading } = useQuery<Operadora[]>({
    queryKey: ["/api/operadoras"],
    queryFn: async () => {
      const response = await fetch('/api/operadoras');
      if (!response.ok) {
        throw new Error(`Erro ao buscar operadoras: ${response.status}`);
      }
      const data = await response.json();
      return data.data || data;
    },
    retry: false,
  });

  const form = useForm<z.infer<typeof operadoraSchema>>({
    resolver: zodResolver(operadoraSchema),
    defaultValues: {
      nome: "",
      codigo: "",
      tipo: "",
      url_login: "",
      possui_rpa: false,
      status_ativo: true,
    },
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: (data: z.infer<typeof operadoraSchema>) =>
      apiRequest(`/api/operadoras`, { method: "POST", body: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/operadoras"] });
      toast({
        title: "Sucesso",
        description: "Operadora criada com sucesso",
      });
      setDialogOpen(false);
      form.reset();
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao criar operadora",
        variant: "destructive",
      });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<z.infer<typeof operadoraSchema>> }) =>
      apiRequest(`/api/operadoras/${id}`, { method: "PUT", body: data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/operadoras"] });
      toast({
        title: "Sucesso",
        description: "Operadora atualizada com sucesso",
      });
      setDialogOpen(false);
      setEditingOperadora(null);
      form.reset();
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao atualizar operadora",
        variant: "destructive",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) =>
      apiRequest(`/api/operadoras/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/operadoras"] });
      toast({
        title: "Sucesso",
        description: "Operadora deletada com sucesso",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao deletar operadora",
        variant: "destructive",
      });
    },
  });

  const testMutation = useMutation({
    mutationFn: (id: number) =>
      apiRequest(`/api/operadoras/${id}/test`, { method: "POST" }),
    onSuccess: (data) => {
      toast({
        title: "Teste Concluído",
        description: data.message || "Teste de conexão realizado",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Erro no Teste",
        description: error.message || "Erro ao testar conexão",
        variant: "destructive",
      });
    },
  });

  // Handlers
  const handleCreate = () => {
    setEditingOperadora(null);
    form.reset();
    setDialogOpen(true);
  };

  const handleEdit = (operadora: Operadora) => {
    setEditingOperadora(operadora);
    form.reset({
      nome: operadora.nome,
      codigo: operadora.codigo,
      tipo: operadora.tipo,
      url_login: operadora.url_login,
      possui_rpa: operadora.possui_rpa,
      status_ativo: operadora.status_ativo,
    });
    setDialogOpen(true);
  };

  const handleDelete = (id: number) => {
    if (confirm("Tem certeza que deseja deletar esta operadora?")) {
      deleteMutation.mutate(id);
    }
  };

  const handleTest = (id: number) => {
    testMutation.mutate(id);
  };

  const handleSubmit = (values: z.infer<typeof operadoraSchema>) => {
    if (editingOperadora) {
      updateMutation.mutate({ id: editingOperadora.id, data: values });
    } else {
      createMutation.mutate(values);
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/4"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  const operadoras = operadorasData || [];

  return (
    <div className="p-6 space-y-6 bg-slate-50 min-h-screen">
      {/* Header com gradiente azul */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Operadoras</h1>
            <p className="text-blue-100 mt-2">Gerencie as operadoras de telecomunicações integradas</p>
          </div>
          <Button 
            onClick={handleCreate}
            className="bg-white text-blue-600 hover:bg-blue-50 font-semibold"
          >
            <Plus className="h-4 w-4 mr-2" />
            Nova Operadora
          </Button>
        </div>
      </div>

      {/* Cards de estatísticas com gradientes */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-500 to-blue-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">{operadoras.length}</div>
            <div className="text-sm text-blue-100 mt-1">Total de Operadoras</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-500 to-green-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {operadoras.filter(op => op.status_ativo).length}
            </div>
            <div className="text-sm text-green-100 mt-1">Operadoras Ativas</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-purple-500 to-purple-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {operadoras.filter(op => op.possui_rpa).length}
            </div>
            <div className="text-sm text-purple-100 mt-1">Com RPA Integrado</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-orange-500 to-orange-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {operadoras.filter(op => op.tipo === 'telecom').length}
            </div>
            <div className="text-sm text-orange-100 mt-1">Telecomunicações</div>
          </CardContent>
        </Card>
      </div>
      
      {/* Tabela de operadoras com design moderno */}
      <Card className="border-0 shadow-lg bg-white">
        <CardHeader className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-lg">
          <CardTitle className="flex items-center text-slate-800">
            <Building2 className="h-5 w-5 mr-2 text-blue-600" />
            Lista de Operadoras ({operadoras.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Nome</TableHead>
                <TableHead>Código</TableHead>
                <TableHead>Tipo</TableHead>
                <TableHead>URL Login</TableHead>
                <TableHead>RPA</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {operadoras.length > 0 ? operadoras.map((operadora) => (
                <TableRow key={operadora.id}>
                  <TableCell className="font-medium">{operadora.id}</TableCell>
                  <TableCell>
                    <div className="flex items-center">
                      <Building2 className="h-4 w-4 mr-2 text-blue-600" />
                      <span className="font-medium">{operadora.nome}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline" className="font-mono">
                      {operadora.codigo}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={
                      operadora.tipo === 'telecom' ? 'bg-blue-100 text-blue-800' :
                      operadora.tipo === 'internet' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }>
                      {operadora.tipo}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <span className="text-sm font-mono text-blue-600 max-w-48 truncate block">
                      {operadora.url_login}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge variant={operadora.possui_rpa ? "default" : "secondary"} className="flex items-center gap-1">
                      <CheckCircle className="h-3 w-3" />
                      {operadora.possui_rpa ? "Sim" : "Não"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge 
                      variant={operadora.status_ativo ? "default" : "destructive"} 
                      className="flex items-center gap-1"
                    >
                      {operadora.status_ativo ? (
                        <>
                          <CheckCircle className="h-3 w-3 text-green-600" />
                          Ativo
                        </>
                      ) : (
                        <>
                          <XCircle className="h-3 w-3 text-red-600" />
                          Inativo
                        </>
                      )}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="text-blue-600 hover:text-blue-700"
                        onClick={() => handleEdit(operadora)}
                      >
                        <Edit className="h-4 w-4 mr-1" />
                        Editar
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="text-green-600 hover:text-green-700"
                        onClick={() => handleTest(operadora.id)}
                        disabled={testMutation.isPending}
                      >
                        <Settings className="h-4 w-4 mr-1" />
                        {testMutation.isPending ? "Testando..." : "Testar"}
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="text-red-600 hover:text-red-700"
                        onClick={() => handleDelete(operadora.id)}
                        disabled={deleteMutation.isPending}
                      >
                        <Trash2 className="h-4 w-4 mr-1" />
                        Deletar
                      </Button>
                      {operadora.url_login && (
                        <Button 
                          variant="outline" 
                          size="sm" 
                          className="text-purple-600 hover:text-purple-700"
                          onClick={() => window.open(operadora.url_login, '_blank')}
                        >
                          <ExternalLink className="h-4 w-4 mr-1" />
                          Acessar
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              )) : (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8">
                    <Building2 className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">Nenhuma operadora encontrada</p>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Dialog para criar/editar operadora */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>
              {editingOperadora ? "Editar Operadora" : "Nova Operadora"}
            </DialogTitle>
          </DialogHeader>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="nome"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Nome</FormLabel>
                      <FormControl>
                        <Input placeholder="Ex: VIVO" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
                <FormField
                  control={form.control}
                  name="codigo"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Código</FormLabel>
                      <FormControl>
                        <Input placeholder="Ex: VIV" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="tipo"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Tipo</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Selecione o tipo" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="telecom">Telecomunicações</SelectItem>
                        <SelectItem value="internet">Internet</SelectItem>
                        <SelectItem value="celular">Celular</SelectItem>
                        <SelectItem value="fixo">Telefonia Fixa</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="url_login"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>URL de Login</FormLabel>
                    <FormControl>
                      <Input placeholder="https://portal.operadora.com.br" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="possui_rpa"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                      <div className="space-y-0.5">
                        <FormLabel className="text-base">RPA Disponível</FormLabel>
                        <div className="text-sm text-muted-foreground">
                          Possui automação configurada
                        </div>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="status_ativo"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4">
                      <div className="space-y-0.5">
                        <FormLabel className="text-base">Status Ativo</FormLabel>
                        <div className="text-sm text-muted-foreground">
                          Operadora habilitada
                        </div>
                      </div>
                      <FormControl>
                        <Switch
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                    </FormItem>
                  )}
                />
              </div>

              <div className="flex justify-end space-x-2">
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
                >
                  {createMutation.isPending || updateMutation.isPending
                    ? "Salvando..."
                    : editingOperadora
                    ? "Atualizar"
                    : "Criar"}
                </Button>
              </div>
            </form>
          </Form>
        </DialogContent>
      </Dialog>
    </div>
  );
}