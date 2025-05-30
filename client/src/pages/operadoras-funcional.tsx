import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Plus, Building2 } from "lucide-react";

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
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center border-b border-gray-200 pb-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Operadoras</h1>
          <p className="text-gray-600 mt-2">Gerencie as operadoras de telecomunicações integradas</p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Plus className="h-4 w-4 mr-2" />
          Nova Operadora
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="border-0 shadow-sm">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">{operadoras.length}</div>
            <div className="text-sm text-gray-600">Total</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-sm">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {operadoras.filter(op => op.status_ativo).length}
            </div>
            <div className="text-sm text-gray-600">Ativas</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-sm">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">
              {operadoras.filter(op => op.possui_rpa).length}
            </div>
            <div className="text-sm text-gray-600">Com RPA</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-sm">
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-orange-600">
              {operadoras.filter(op => op.tipo === 'telecom').length}
            </div>
            <div className="text-sm text-gray-600">Telecom</div>
          </CardContent>
        </Card>
      </div>
      
      <Card className="border-0 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center">
            <Building2 className="h-5 w-5 mr-2 text-blue-600" />
            Lista de Operadoras ({operadoras.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Nome</TableHead>
                <TableHead>Código</TableHead>
                <TableHead>RPA</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {operadoras.length > 0 ? operadoras.map((operadora: any) => (
                <TableRow key={operadora.id}>
                  <TableCell>{operadora.id}</TableCell>
                  <TableCell>{operadora.nome}</TableCell>
                  <TableCell>{operadora.codigo}</TableCell>
                  <TableCell>
                    <Badge variant={operadora.possui_rpa ? "default" : "secondary"}>
                      {operadora.possui_rpa ? "Sim" : "Não"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={operadora.status_ativo ? "default" : "destructive"}>
                      {operadora.status_ativo ? "Ativo" : "Inativo"}
                    </Badge>
                  </TableCell>
                </TableRow>
              )) : (
                <TableRow>
                  <TableCell colSpan={5} className="text-center">Nenhuma operadora encontrada</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}