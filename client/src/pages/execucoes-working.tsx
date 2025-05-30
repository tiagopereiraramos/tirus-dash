import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export default function Execucoes() {
  const { data: execucoes, isLoading } = useQuery({
    queryKey: ["/api/execucoes"],
    retry: false,
  });

  if (isLoading) {
    return <div className="p-6">Carregando execuções...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Execuções RPA</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Lista de Execuções</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Operadora</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Data</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {execucoes?.execucoes?.map((execucao: any) => (
                <TableRow key={execucao.id}>
                  <TableCell>{execucao.id}</TableCell>
                  <TableCell>{execucao.operadora}</TableCell>
                  <TableCell>{execucao.status}</TableCell>
                  <TableCell>{execucao.data}</TableCell>
                </TableRow>
              )) || (
                <TableRow>
                  <TableCell colSpan={4} className="text-center">Nenhuma execução encontrada</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}