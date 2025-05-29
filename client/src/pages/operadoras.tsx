import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Progress } from "@/components/ui/progress";
import { Settings, Play, Pause, BarChart3 } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

export default function Operadoras() {
  const { data: operadoras } = useQuery({
    queryKey: ["/api/operadoras"],
  });

  const { data: operadorasStatus } = useQuery({
    queryKey: ["/api/operadoras/status"],
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "ativo":
        return <Badge className="status-success">Ativo</Badge>;
      case "inativo":
        return <Badge className="status-error">Inativo</Badge>;
      case "manutencao":
        return <Badge className="status-warning">Manutenção</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getOperadorColor = (codigo: string) => {
    const colors: Record<string, string> = {
      "EMBRATEL": "bg-blue-600",
      "VIVO": "bg-purple-600", 
      "DIGITALNET": "bg-green-600",
      "AZUTON": "bg-orange-600",
      "OI": "bg-red-600",
    };
    return colors[codigo] || "bg-gray-600";
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-foreground">Operadoras</h2>
        <p className="text-muted-foreground">
          Gerencie as operadoras e monitore o status dos RPAs
        </p>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        {operadorasStatus?.map((operadora: any) => (
          <Card key={operadora.codigo}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className={`w-8 h-8 ${getOperadorColor(operadora.codigo)} rounded-lg flex items-center justify-center`}>
                  <span className="text-white text-xs font-bold">
                    {operadora.codigo.substring(0, 2)}
                  </span>
                </div>
                {getStatusBadge(operadora.status)}
              </div>
              <div>
                <h3 className="font-semibold text-sm mb-2">{operadora.nome}</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">Taxa de Sucesso</span>
                    <span className="font-medium">{operadora.taxaSucesso || 0}%</span>
                  </div>
                  <Progress value={operadora.taxaSucesso || 0} className="h-2" />
                  <div className="text-xs text-muted-foreground">
                    Última execução: {operadora.ultimaExecucao || "Nunca"}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Detailed Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Configuração das Operadoras</CardTitle>
            <Button className="btn-primary">
              <Settings className="h-4 w-4 mr-2" />
              Adicionar Operadora
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Operadora</TableHead>
                <TableHead>Código</TableHead>
                <TableHead>URL Base</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Total Clientes</TableHead>
                <TableHead>Última Execução</TableHead>
                <TableHead>Taxa de Sucesso</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {operadoras?.map((operadora: any) => (
                <TableRow key={operadora.id} className="hover:bg-muted/50">
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 ${getOperadorColor(operadora.codigo)} rounded-lg flex items-center justify-center`}>
                        <span className="text-white text-xs font-bold">
                          {operadora.codigo.substring(0, 2)}
                        </span>
                      </div>
                      <div>
                        <div className="font-medium">{operadora.nome}</div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{operadora.codigo}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm text-muted-foreground max-w-48 truncate">
                      {operadora.url || "Não configurado"}
                    </div>
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(operadora.status)}
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      {operadora.totalClientes || 0} clientes
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      {operadora.ultimaExecucao 
                        ? format(new Date(operadora.ultimaExecucao), "dd/MM HH:mm", { locale: ptBR })
                        : "Nunca"
                      }
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Progress value={operadora.taxaSucesso || 0} className="w-16 h-2" />
                      <span className="text-xs text-muted-foreground">
                        {operadora.taxaSucesso || 0}%
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Button variant="ghost" size="sm">
                        <Settings className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <BarChart3 className="h-4 w-4" />
                      </Button>
                      {operadora.status === "ativo" ? (
                        <Button variant="ghost" size="sm">
                          <Pause className="h-4 w-4" />
                        </Button>
                      ) : (
                        <Button variant="ghost" size="sm">
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* RPA Configurations */}
      <Card>
        <CardHeader>
          <CardTitle>Configurações dos RPAs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {operadoras?.map((operadora: any) => (
              <Card key={`config-${operadora.id}`} className="border-2">
                <CardHeader className="pb-3">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 ${getOperadorColor(operadora.codigo)} rounded-lg flex items-center justify-center`}>
                      <span className="text-white text-xs font-bold">
                        {operadora.codigo.substring(0, 2)}
                      </span>
                    </div>
                    <div>
                      <CardTitle className="text-base">{operadora.nome}</CardTitle>
                      {getStatusBadge(operadora.status)}
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Timeout</span>
                    <span className="font-medium">30s</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Retry</span>
                    <span className="font-medium">3x</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Threads</span>
                    <span className="font-medium">2</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Última Atualização</span>
                    <span className="font-medium text-xs">
                      {operadora.updatedAt 
                        ? format(new Date(operadora.updatedAt), "dd/MM", { locale: ptBR })
                        : "Nunca"
                      }
                    </span>
                  </div>
                  <Button variant="outline" size="sm" className="w-full">
                    <Settings className="h-4 w-4 mr-2" />
                    Configurar
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
