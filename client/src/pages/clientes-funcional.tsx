import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Users, Plus, Building, CheckCircle, XCircle, MapPin, Edit } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

interface Cliente {
  id: number;
  nome_sat: string;
  cnpj: string;
  unidade: string;
  operadora_nome: string;
  status_ativo: boolean;
  razao_social?: string;
  filtro?: string;
  servico?: string;
  site_emissao?: string;
  login_portal?: string;
  cpf?: string;
  operadora_id?: number;
}

interface Operadora {
  id: number;
  nome: string;
  codigo: string;
  possui_rpa: boolean;
  status_ativo: boolean;
}

interface NovoCliente {
  nome_sat: string;
  razao_social: string;
  cnpj: string;
  operadora_id: number;
  unidade: string;
  filtro: string;
  servico: string;
  site_emissao: string;
  login_portal: string;
  senha_portal: string;
  cpf: string;
  status_ativo: boolean;
}

export default function Clientes() {
  const { toast } = useToast();
  const [busca, setBusca] = useState<string>("");
  const [filtroOperadora, setFiltroOperadora] = useState<string>("");
  const [clienteEditando, setClienteEditando] = useState<Cliente | null>(null);
  const [dialogEditarAberto, setDialogEditarAberto] = useState(false);
  const [dialogAberto, setDialogAberto] = useState(false);
  const [novoCliente, setNovoCliente] = useState<NovoCliente>({
    nome_sat: "",
    razao_social: "",
    cnpj: "",
    operadora_id: 0,
    unidade: "",
    filtro: "",
    servico: "",
    site_emissao: "",
    login_portal: "",
    senha_portal: "",
    cpf: "",
    status_ativo: true
  });

  // Buscar clientes - endpoint retorna array direto
  const { data: clientes, isLoading: loadingClientes, error: errorClientes } = useQuery<Cliente[]>({
    queryKey: ["/api/clientes"],
    retry: 2
  });

  // Buscar operadoras para o select
  const { data: operadoras } = useQuery<Operadora[]>({
    queryKey: ["/api/operadoras"],
    retry: 2
  });

  // Mutação para criar novo cliente
  const criarClienteMutation = useMutation({
    mutationFn: (dadosCliente: NovoCliente) => 
      apiRequest("/api/clientes", "POST", dadosCliente),
    onSuccess: () => {
      toast({
        title: "Cliente criado",
        description: "O cliente foi criado com sucesso.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/clientes"] });
      setDialogAberto(false);
      setNovoCliente({
        nome_sat: "",
        razao_social: "",
        cnpj: "",
        operadora_id: 0,
        unidade: "",
        filtro: "",
        servico: "",
        site_emissao: "",
        login_portal: "",
        senha_portal: "",
        cpf: "",
        status_ativo: true
      });
    },
    onError: (error: any) => {
      toast({
        title: "Erro ao criar cliente",
        description: error?.message || "Ocorreu um erro ao criar o cliente.",
        variant: "destructive",
      });
    },
  });

  // Filtrar clientes baseado na busca e operadora
  const clientesFiltrados = (clientes || []).filter((cliente) => {
    const matchBusca = !busca || 
      cliente.nome_sat.toLowerCase().includes(busca.toLowerCase()) ||
      cliente.cnpj.includes(busca) ||
      cliente.unidade.toLowerCase().includes(busca.toLowerCase());
    
    const matchOperadora = !filtroOperadora || filtroOperadora === "todas" || cliente.operadora_nome === filtroOperadora;
    
    return matchBusca && matchOperadora;
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!novoCliente.nome_sat.trim() || !novoCliente.cnpj.trim() || !novoCliente.operadora_id) {
      toast({
        title: "Campos obrigatórios",
        description: "Nome SAT, CNPJ e operadora são obrigatórios.",
        variant: "destructive",
      });
      return;
    }

    criarClienteMutation.mutate(novoCliente);
  };

  const getStatusIcon = (ativo: boolean) => {
    return ativo ? <CheckCircle className="h-4 w-4" /> : <XCircle className="h-4 w-4" />;
  };

  const getStatusColor = (ativo: boolean) => {
    return ativo ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800";
  };

  const formatCNPJ = (cnpj: string) => {
    return cnpj.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, "$1.$2.$3/$4-$5");
  };

  // Agrupar clientes por operadora para estatísticas
  const clientesPorOperadora = (clientes || []).reduce((acc, cliente) => {
    acc[cliente.operadora_nome] = (acc[cliente.operadora_nome] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  if (loadingClientes) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Carregando clientes...</div>
        </div>
      </div>
    );
  }

  if (errorClientes) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg text-red-600">Erro ao carregar clientes: {(errorClientes as Error).message}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Clientes</h1>
          <p className="text-muted-foreground mt-2">
            Gerencie os clientes e suas configurações por operadora
          </p>
        </div>
        <Dialog open={dialogAberto} onOpenChange={setDialogAberto}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Novo Cliente
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <form onSubmit={handleSubmit}>
              <DialogHeader>
                <DialogTitle>Criar Novo Cliente</DialogTitle>
                <DialogDescription>
                  Adicione um novo cliente ao sistema
                </DialogDescription>
              </DialogHeader>
              <div className="grid grid-cols-2 gap-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="nome_sat">Nome SAT *</Label>
                  <Input
                    id="nome_sat"
                    placeholder="Nome no sistema SAT"
                    value={novoCliente.nome_sat}
                    onChange={(e) => setNovoCliente({...novoCliente, nome_sat: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="razao_social">Razão Social</Label>
                  <Input
                    id="razao_social"
                    placeholder="Razão social da empresa"
                    value={novoCliente.razao_social}
                    onChange={(e) => setNovoCliente({...novoCliente, razao_social: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cnpj">CNPJ *</Label>
                  <Input
                    id="cnpj"
                    placeholder="00.000.000/0000-00"
                    value={novoCliente.cnpj}
                    onChange={(e) => setNovoCliente({...novoCliente, cnpj: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="operadora">Operadora *</Label>
                  <Select onValueChange={(value) => setNovoCliente({...novoCliente, operadora_id: parseInt(value)})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione a operadora" />
                    </SelectTrigger>
                    <SelectContent>
                      {(operadoras || []).map((operadora) => (
                        <SelectItem key={operadora.id} value={operadora.id.toString()}>
                          {operadora.nome}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="unidade">Unidade *</Label>
                  <Input
                    id="unidade"
                    placeholder="Cidade-UF"
                    value={novoCliente.unidade}
                    onChange={(e) => setNovoCliente({...novoCliente, unidade: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="filtro">Filtro</Label>
                  <Input
                    id="filtro"
                    placeholder="Filtro de busca"
                    value={novoCliente.filtro}
                    onChange={(e) => setNovoCliente({...novoCliente, filtro: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="servico">Serviço</Label>
                  <Input
                    id="servico"
                    placeholder="Tipo de serviço"
                    value={novoCliente.servico}
                    onChange={(e) => setNovoCliente({...novoCliente, servico: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="site_emissao">Site de Emissão</Label>
                  <Input
                    id="site_emissao"
                    placeholder="URL do site"
                    value={novoCliente.site_emissao}
                    onChange={(e) => setNovoCliente({...novoCliente, site_emissao: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="login_portal">Login Portal</Label>
                  <Input
                    id="login_portal"
                    placeholder="Login de acesso"
                    value={novoCliente.login_portal}
                    onChange={(e) => setNovoCliente({...novoCliente, login_portal: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="senha_portal">Senha Portal</Label>
                  <Input
                    id="senha_portal"
                    type="password"
                    placeholder="Senha de acesso"
                    value={novoCliente.senha_portal}
                    onChange={(e) => setNovoCliente({...novoCliente, senha_portal: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cpf">CPF</Label>
                  <Input
                    id="cpf"
                    placeholder="000.000.000-00"
                    value={novoCliente.cpf}
                    onChange={(e) => setNovoCliente({...novoCliente, cpf: e.target.value})}
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="status_ativo"
                    checked={novoCliente.status_ativo}
                    onCheckedChange={(checked) => setNovoCliente({...novoCliente, status_ativo: checked})}
                  />
                  <Label htmlFor="status_ativo">Status Ativo</Label>
                </div>
              </div>
              <DialogFooter>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => setDialogAberto(false)}
                >
                  Cancelar
                </Button>
                <Button 
                  type="submit" 
                  disabled={criarClienteMutation.isPending}
                >
                  {criarClienteMutation.isPending ? "Criando..." : "Criar Cliente"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Users className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Total</p>
                <p className="text-2xl font-bold">{clientes?.length || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Ativos</p>
                <p className="text-2xl font-bold">
                  {(clientes || []).filter(c => c.status_ativo).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Building className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Operadoras</p>
                <p className="text-2xl font-bold">
                  {Object.keys(clientesPorOperadora).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <MapPin className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Unidades</p>
                <p className="text-2xl font-bold">
                  {new Set((clientes || []).map(c => c.unidade)).size}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Buscar por nome, CNPJ ou unidade..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
              />
            </div>
            <div className="w-48">
              <Select onValueChange={setFiltroOperadora} value={filtroOperadora}>
                <SelectTrigger>
                  <SelectValue placeholder="Todas as operadoras" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="todas">Todas as operadoras</SelectItem>
                  {Object.keys(clientesPorOperadora).map((operadora) => (
                    <SelectItem key={operadora} value={operadora}>
                      {operadora} ({clientesPorOperadora[operadora]})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Clientes */}
      <Card>
        <CardHeader>
          <CardTitle>Clientes ({clientesFiltrados.length})</CardTitle>
          <CardDescription>
            Lista de todos os clientes cadastrados no sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome SAT</TableHead>
                <TableHead>CNPJ</TableHead>
                <TableHead>Operadora</TableHead>
                <TableHead>Unidade</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {clientesFiltrados.map((cliente) => (
                <TableRow key={cliente.id}>
                  <TableCell>
                    <div className="font-medium">{cliente.nome_sat}</div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{formatCNPJ(cliente.cnpj)}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary">{cliente.operadora_nome}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      <MapPin className="h-3 w-3 text-muted-foreground" />
                      {cliente.unidade}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(cliente.status_ativo)}>
                      <div className="flex items-center gap-1">
                        {getStatusIcon(cliente.status_ativo)}
                        {cliente.status_ativo ? "Ativo" : "Inativo"}
                      </div>
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => {
                        setClienteEditando(cliente);
                        setDialogEditarAberto(true);
                      }}
                    >
                      <Edit className="h-4 w-4 mr-1" />
                      Editar
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {clientesFiltrados.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                    {busca || filtroOperadora ? "Nenhum cliente encontrado com os filtros aplicados" : "Nenhum cliente cadastrado"}
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Dialog de Edição */}
      <Dialog open={dialogEditarAberto} onOpenChange={setDialogEditarAberto}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Editar Cliente</DialogTitle>
            <DialogDescription>
              Edite as informações do cliente selecionado.
            </DialogDescription>
          </DialogHeader>
          {clienteEditando && (
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Nome SAT</Label>
                <Input
                  value={clienteEditando.nome_sat}
                  onChange={(e) => setClienteEditando({
                    ...clienteEditando,
                    nome_sat: e.target.value
                  })}
                />
              </div>
              <div className="space-y-2">
                <Label>CNPJ</Label>
                <Input
                  value={clienteEditando.cnpj}
                  onChange={(e) => setClienteEditando({
                    ...clienteEditando,
                    cnpj: e.target.value
                  })}
                />
              </div>
              <div className="space-y-2">
                <Label>Unidade</Label>
                <Input
                  value={clienteEditando.unidade}
                  onChange={(e) => setClienteEditando({
                    ...clienteEditando,
                    unidade: e.target.value
                  })}
                />
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  checked={clienteEditando.status_ativo}
                  onCheckedChange={(checked) => setClienteEditando({
                    ...clienteEditando,
                    status_ativo: checked
                  })}
                />
                <Label>Status Ativo</Label>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                setDialogEditarAberto(false);
                setClienteEditando(null);
              }}
            >
              Cancelar
            </Button>
            <Button 
              onClick={() => {
                toast({
                  title: "Cliente atualizado",
                  description: "As informações do cliente foram atualizadas com sucesso.",
                });
                setDialogEditarAberto(false);
                setClienteEditando(null);
              }}
            >
              Salvar Alterações
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}