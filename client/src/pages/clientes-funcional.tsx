import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export default function Clientes() {
  const { data: clientesData, isLoading } = useQuery({
    queryKey: ["/api/clientes"],
    retry: false,
  });

  if (isLoading) {
    return <div className="p-6">Carregando clientes...</div>;
  }

  const clientes = clientesData || [];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Clientes</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Lista de Clientes</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Nome SAT</TableHead>
                <TableHead>CNPJ</TableHead>
                <TableHead>Unidade</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {clientes.length > 0 ? clientes.map((cliente: any) => (
                <TableRow key={cliente.id}>
                  <TableCell>{cliente.id}</TableCell>
                  <TableCell>{cliente.nome_sat}</TableCell>
                  <TableCell>{cliente.cnpj}</TableCell>
                  <TableCell>{cliente.unidade}</TableCell>
                  <TableCell>
                    <Badge variant={cliente.status_ativo ? "default" : "destructive"}>
                      {cliente.status_ativo ? "Ativo" : "Inativo"}
                    </Badge>
                  </TableCell>
                </TableRow>
              )) : (
                <TableRow>
                  <TableCell colSpan={5} className="text-center">Nenhum cliente encontrado</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}