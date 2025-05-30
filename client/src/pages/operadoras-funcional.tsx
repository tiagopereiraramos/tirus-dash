import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export default function Operadoras() {
  const { data: operadorasData, isLoading } = useQuery({
    queryKey: ["/api/operadoras"],
    retry: false,
  });

  if (isLoading) {
    return <div className="p-6">Carregando operadoras...</div>;
  }

  const operadoras = operadorasData || [];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Operadoras</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Lista de Operadoras</CardTitle>
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