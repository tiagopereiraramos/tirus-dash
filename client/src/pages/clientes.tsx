import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Users, Plus, Search, Building, FileText } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

export default function Clientes() {
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCliente, setSelectedCliente] = useState<any>(null);

  const { data: clientes, isLoading } = useQuery({
    queryKey: ["/api/clientes", { page, search: searchTerm }],
  });

  const { data: contratos } = useQuery({
    queryKey: ["/api/contratos", { clienteId: selectedCliente?.id }],
    enabled: !!selectedCliente?.id,
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "ativo":
        return <Badge className="status-success">Ativo</Badge>;
      case "inativo":
        return <Badge className="status-error">Inativo</Badge>;
      case "suspenso":
        return <Badge className="status-warning">Suspenso</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatCNPJ = (cnpj: string) => {
    if (!cnpj) return "";
    return cnpj.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, "$1.$2.$3/$4-$5");
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-foreground">Clientes</h2>
        <p className="text-muted-foreground">
          Gerencie os clientes e seus contratos com as operadoras
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Clientes</p>
                <p className="text-2xl font-bold text-foreground">{clientes?.total || 0}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                <Users className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Clientes Ativos</p>
                <p className="text-2xl font-bold text-foreground">{clientes?.ativos || 0}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                <Building className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Contratos</p>
                <p className="text-2xl font-bold text-foreground">{clientes?.totalContratos || 0}</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                <FileText className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Novos Este Mês</p>
                <p className="text-2xl font-bold text-foreground">8</p>
              </div>
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
                <Plus className="h-6 w-6 text-orange-600 dark:text-orange-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Buscar Clientes
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Buscar por razão social, nome SAT ou CNPJ..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <Button className="btn-primary">
              <Plus className="h-4 w-4 mr-2" />
              Novo Cliente
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Clients Table */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Clientes</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Razão Social</TableHead>
                <TableHead>Nome SAT</TableHead>
                <TableHead>CNPJ</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Contratos</TableHead>
                <TableHead>Cadastrado</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {clientes?.data?.map((cliente: any) => (
                <TableRow key={cliente.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div className="font-medium text-sm max-w-64 truncate">
                      {cliente.razaoSocial}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm max-w-48 truncate">
                      {cliente.nomeSat}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm font-mono">
                      {formatCNPJ(cliente.cnpj)}
                    </div>
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(cliente.status)}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {cliente.totalContratos || 0} contratos
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      {cliente.createdAt 
                        ? format(new Date(cliente.createdAt), "dd/MM/yyyy", { locale: ptBR })
                        : "-"
                      }
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedCliente(cliente)}
                          >
                            <FileText className="h-4 w-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-4xl">
                          <DialogHeader>
                            <DialogTitle>Detalhes do Cliente</DialogTitle>
                            <DialogDescription>
                              Informações detalhadas e contratos do cliente
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-6">
                            {/* Client Info */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <label className="text-sm font-medium">Razão Social:</label>
                                <p className="text-sm text-muted-foreground">
                                  {selectedCliente?.razaoSocial}
                                </p>
                              </div>
                              <div>
                                <label className="text-sm font-medium">Nome SAT:</label>
                                <p className="text-sm text-muted-foreground">
                                  {selectedCliente?.nomeSat}
                                </p>
                              </div>
                              <div>
                                <label className="text-sm font-medium">CNPJ:</label>
                                <p className="text-sm text-muted-foreground font-mono">
                                  {formatCNPJ(selectedCliente?.cnpj)}
                                </p>
                              </div>
                              <div>
                                <label className="text-sm font-medium">Status:</label>
                                <div className="mt-1">
                                  {getStatusBadge(selectedCliente?.status)}
                                </div>
                              </div>
                            </div>

                            {/* Contracts */}
                            <div>
                              <h4 className="text-lg font-semibold mb-4">Contratos</h4>
                              <div className="border rounded-lg">
                                <Table>
                                  <TableHeader>
                                    <TableRow>
                                      <TableHead>Hash</TableHead>
                                      <TableHead>Operadora</TableHead>
                                      <TableHead>Serviço</TableHead>
                                      <TableHead>Tipo</TableHead>
                                      <TableHead>Status</TableHead>
                                    </TableRow>
                                  </TableHeader>
                                  <TableBody>
                                    {contratos?.map((contrato: any) => (
                                      <TableRow key={contrato.id}>
                                        <TableCell className="font-mono text-xs">
                                          {contrato.hash?.substring(0, 8)}...
                                        </TableCell>
                                        <TableCell>
                                          <Badge variant="outline">
                                            {contrato.operadora?.nome}
                                          </Badge>
                                        </TableCell>
                                        <TableCell className="text-sm">
                                          {contrato.servico}
                                        </TableCell>
                                        <TableCell className="text-sm">
                                          {contrato.tipoServico}
                                        </TableCell>
                                        <TableCell>
                                          {getStatusBadge(contrato.status)}
                                        </TableCell>
                                      </TableRow>
                                    ))}
                                  </TableBody>
                                </Table>
                              </div>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                      <Button variant="ghost" size="sm">
                        <Building className="h-4 w-4" />
                      </Button>
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
