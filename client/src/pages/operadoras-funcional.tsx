import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, Building2, Edit, Trash2, Settings, ExternalLink } from "lucide-react";

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

export default function Operadoras() {
  const { data: operadorasData, isLoading } = useQuery<Operadora[]>({
    queryKey: ["/api/operadoras"],
    retry: false,
  });

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
          <Button className="bg-white text-blue-600 hover:bg-blue-50 font-semibold">
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
                    <Badge variant={operadora.possui_rpa ? "default" : "secondary"}>
                      {operadora.possui_rpa ? "✓ Sim" : "✗ Não"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={operadora.status_ativo ? "default" : "destructive"}>
                      {operadora.status_ativo ? "🟢 Ativo" : "🔴 Inativo"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button variant="outline" size="sm" className="text-blue-600 hover:text-blue-700">
                        <Edit className="h-4 w-4 mr-1" />
                        Editar
                      </Button>
                      <Button variant="outline" size="sm" className="text-green-600 hover:text-green-700">
                        <Settings className="h-4 w-4 mr-1" />
                        Testar
                      </Button>
                      {operadora.url_login && (
                        <Button variant="outline" size="sm" className="text-purple-600 hover:text-purple-700">
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
    </div>
  );
}