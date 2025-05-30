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
import { Building2, Plus, Settings, CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

interface Operadora {
  id: number;
  nome: string;
  codigo: string;
  possui_rpa: boolean;
  status_ativo: boolean;
}

interface NovaOperadora {
  nome: string;
  codigo: string;
  possui_rpa: boolean;
  status_ativo: boolean;
}

export default function Operadoras() {
  const { toast } = useToast();
  const [busca, setBusca] = useState<string>("");
  const [dialogAberto, setDialogAberto] = useState(false);
  const [novaOperadora, setNovaOperadora] = useState<NovaOperadora>({
    nome: "",
    codigo: "",
    possui_rpa: false,
    status_ativo: true
  });

  // Buscar operadoras - endpoint retorna array direto
  const { data: operadoras, isLoading, error } = useQuery<Operadora[]>({
    queryKey: ["/api/operadoras"],
    retry: 2
  });

  // Mutação para criar nova operadora
  const criarOperadoraMutation = useMutation({
    mutationFn: (dadosOperadora: NovaOperadora) => 
      apiRequest("/api/operadoras", "POST", dadosOperadora),
    onSuccess: () => {
      toast({
        title: "Operadora criada",
        description: "A operadora foi criada com sucesso.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/operadoras"] });
      setDialogAberto(false);
      setNovaOperadora({
        nome: "",
        codigo: "",
        possui_rpa: false,
        status_ativo: true
      });
    },
    onError: (error: any) => {
      toast({
        title: "Erro ao criar operadora",
        description: error?.message || "Ocorreu um erro ao criar a operadora.",
        variant: "destructive",
      });
    },
  });

  // Filtrar operadoras baseado na busca
  const operadorasFiltradas = (operadoras || []).filter((operadora) =>
    !busca || 
    operadora.nome.toLowerCase().includes(busca.toLowerCase()) ||
    operadora.codigo.toLowerCase().includes(busca.toLowerCase())
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!novaOperadora.nome.trim() || !novaOperadora.codigo.trim()) {
      toast({
        title: "Campos obrigatórios",
        description: "Nome e código são obrigatórios.",
        variant: "destructive",
      });
      return;
    }

    criarOperadoraMutation.mutate(novaOperadora);
  };

  const getStatusIcon = (ativo: boolean) => {
    return ativo ? <CheckCircle className="h-4 w-4" /> : <XCircle className="h-4 w-4" />;
  };

  const getStatusColor = (ativo: boolean) => {
    return ativo ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800";
  };

  const getRpaIcon = (possuiRpa: boolean) => {
    return possuiRpa ? <CheckCircle className="h-4 w-4" /> : <AlertTriangle className="h-4 w-4" />;
  };

  const getRpaColor = (possuiRpa: boolean) => {
    return possuiRpa ? "bg-blue-100 text-blue-800" : "bg-yellow-100 text-yellow-800";
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Carregando operadoras...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg text-red-600">Erro ao carregar operadoras: {(error as Error).message}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Operadoras</h1>
          <p className="text-muted-foreground mt-2">
            Gerencie as operadoras de telecomunicações do sistema
          </p>
        </div>
        <Dialog open={dialogAberto} onOpenChange={setDialogAberto}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Nova Operadora
            </Button>
          </DialogTrigger>
          <DialogContent>
            <form onSubmit={handleSubmit}>
              <DialogHeader>
                <DialogTitle>Criar Nova Operadora</DialogTitle>
                <DialogDescription>
                  Adicione uma nova operadora ao sistema
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="nome">Nome *</Label>
                  <Input
                    id="nome"
                    placeholder="Nome da operadora"
                    value={novaOperadora.nome}
                    onChange={(e) => setNovaOperadora({...novaOperadora, nome: e.target.value})}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="codigo">Código *</Label>
                  <Input
                    id="codigo"
                    placeholder="Código da operadora"
                    value={novaOperadora.codigo}
                    onChange={(e) => setNovaOperadora({...novaOperadora, codigo: e.target.value.toUpperCase()})}
                    required
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="possui_rpa"
                    checked={novaOperadora.possui_rpa}
                    onCheckedChange={(checked) => setNovaOperadora({...novaOperadora, possui_rpa: checked})}
                  />
                  <Label htmlFor="possui_rpa">Possui RPA</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="status_ativo"
                    checked={novaOperadora.status_ativo}
                    onCheckedChange={(checked) => setNovaOperadora({...novaOperadora, status_ativo: checked})}
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
                  disabled={criarOperadoraMutation.isPending}
                >
                  {criarOperadoraMutation.isPending ? "Criando..." : "Criar Operadora"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Building2 className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Total</p>
                <p className="text-2xl font-bold">{operadoras?.length || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Ativas</p>
                <p className="text-2xl font-bold">
                  {(operadoras || []).filter(op => op.status_ativo).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center">
              <Settings className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">Com RPA</p>
                <p className="text-2xl font-bold">
                  {(operadoras || []).filter(op => op.possui_rpa).length}
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
                placeholder="Buscar por nome ou código..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Operadoras */}
      <Card>
        <CardHeader>
          <CardTitle>Operadoras ({operadorasFiltradas.length})</CardTitle>
          <CardDescription>
            Lista de todas as operadoras cadastradas no sistema
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Nome</TableHead>
                <TableHead>Código</TableHead>
                <TableHead>RPA</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {operadorasFiltradas.map((operadora) => (
                <TableRow key={operadora.id}>
                  <TableCell>
                    <div className="font-medium">{operadora.nome}</div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{operadora.codigo}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={getRpaColor(operadora.possui_rpa)}>
                      <div className="flex items-center gap-1">
                        {getRpaIcon(operadora.possui_rpa)}
                        {operadora.possui_rpa ? "Disponível" : "Indisponível"}
                      </div>
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusColor(operadora.status_ativo)}>
                      <div className="flex items-center gap-1">
                        {getStatusIcon(operadora.status_ativo)}
                        {operadora.status_ativo ? "Ativo" : "Inativo"}
                      </div>
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Button size="sm" variant="outline">
                      <Settings className="h-4 w-4 mr-1" />
                      Configurar
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
              {operadorasFiltradas.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                    {busca ? "Nenhuma operadora encontrada com os filtros aplicados" : "Nenhuma operadora cadastrada"}
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