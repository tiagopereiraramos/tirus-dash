import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Eye, Square, RefreshCw } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

// Mock data para demonstração
const mockExecutions = [
  {
    id: 1,
    contrato: {
      cliente: { nomeSat: "RICAL - RACK INDUSTRIA", cnpj: "84.718.741/0001-00" },
      operadora: { nome: "EMBRATEL" }
    },
    status: "concluido",
    tempoExecucao: 204,
    iniciadoEm: new Date().toISOString(),
  },
  {
    id: 2,
    contrato: {
      cliente: { nomeSat: "ALVORADA COMERCIO", cnpj: "01.963.040/0003-63" },
      operadora: { nome: "DIGITALNET" }
    },
    status: "executando",
    tempoExecucao: 72,
    iniciadoEm: new Date(Date.now() - 72000).toISOString(),
  },
  {
    id: 3,
    contrato: {
      cliente: { nomeSat: "CENZE TRANSPORTES", cnpj: "15.447.568/0002-03" },
      operadora: { nome: "VIVO" }
    },
    status: "falha",
    tempoExecucao: 345,
    iniciadoEm: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: 4,
    contrato: {
      cliente: { nomeSat: "FINANCIAL CONSTRUTORA", cnpj: "15.565.179/0001-00" },
      operadora: { nome: "AZUTON" }
    },
    status: "concluido",
    tempoExecucao: 178,
    iniciadoEm: new Date(Date.now() - 1800000).toISOString(),
  },
];

export default function RecentExecutions() {
  const { data: execucoes } = useQuery({
    queryKey: ["/api/execucoes", { page: 1, limit: 10 }],
    enabled: false, // Disabled to use mock data
  });

  const data = execucoes?.data || mockExecutions;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "concluido":
        return (
          <Badge className="status-success">
            <svg className="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Concluído
          </Badge>
        );
      case "executando":
        return (
          <Badge className="status-info">
            <svg className="h-3 w-3 mr-1 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Executando
          </Badge>
        );
      case "falha":
        return (
          <Badge className="status-error">
            <svg className="h-3 w-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            Falha
          </Badge>
        );
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Execuções Recentes</CardTitle>
          <Button variant="outline" size="sm">
            Ver todas
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="px-6">Cliente</TableHead>
              <TableHead>Operadora</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Tempo</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((execucao: any) => (
              <TableRow key={execucao.id} className="hover:bg-muted/50">
                <TableCell className="px-6">
                  <div>
                    <div className="font-medium text-sm">
                      {execucao.contrato.cliente.nomeSat}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {execucao.contrato.cliente.cnpj}
                    </div>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant="outline" className="text-xs">
                    {execucao.contrato.operadora.nome}
                  </Badge>
                </TableCell>
                <TableCell>
                  {getStatusBadge(execucao.status)}
                </TableCell>
                <TableCell>
                  <div className="text-sm">
                    {formatDuration(execucao.tempoExecucao)}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
