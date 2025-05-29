import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Settings, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

export default function OperatorStatus() {
  const { data: operadorasStatus, isLoading } = useQuery({
    queryKey: ["/api/operadoras/status"],
  });

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

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "ativo":
        return (
          <Badge className="status-success text-xs">
            Online
          </Badge>
        );
      case "inativo":
        return (
          <Badge className="status-error text-xs">
            Offline
          </Badge>
        );
      case "manutencao":
        return (
          <Badge className="status-warning text-xs">
            Manutenção
          </Badge>
        );
      default:
        return <Badge variant="outline" className="text-xs">{status}</Badge>;
    }
  };

  const getTrendIcon = (taxaSucesso: number) => {
    if (taxaSucesso >= 95) {
      return <TrendingUp className="h-3 w-3 text-green-600 dark:text-green-400" />;
    } else if (taxaSucesso >= 85) {
      return <Minus className="h-3 w-3 text-yellow-600 dark:text-yellow-400" />;
    } else {
      return <TrendingDown className="h-3 w-3 text-red-600 dark:text-red-400" />;
    }
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Status das Operadoras
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Status das Operadoras
          </CardTitle>
          <Settings className="h-4 w-4 text-muted-foreground cursor-pointer hover:text-foreground" />
        </div>
      </CardHeader>
      <CardContent>
        {!operadorasStatus?.length ? (
          <div className="text-center py-8">
            <Settings className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-medium text-foreground mb-2">
              Nenhuma operadora configurada
            </h3>
            <p className="text-sm text-muted-foreground">
              Configure as operadoras para monitorar o status
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {operadorasStatus.map((operadora: any) => (
              <div
                key={operadora.id}
                className="flex items-center justify-between p-3 rounded-lg bg-muted/30 hover:bg-muted/50 transition-colors"
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-8 h-8 ${getOperadorColor(operadora.codigo)} rounded-lg flex items-center justify-center`}>
                    <span className="text-white text-xs font-bold">
                      {operadora.codigo.substring(0, 2)}
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="text-sm font-medium text-foreground">
                        {operadora.nome}
                      </span>
                      {getStatusBadge(operadora.status)}
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                      <span>
                        {operadora.ultimaExecucao 
                          ? `Última execução: ${format(new Date(operadora.ultimaExecucao), "dd/MM HH:mm", { locale: ptBR })}`
                          : "Nunca executado"
                        }
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-sm font-medium text-foreground">
                      {operadora.taxaSucesso || 0}%
                    </span>
                    {getTrendIcon(operadora.taxaSucesso || 0)}
                  </div>
                  <Progress 
                    value={operadora.taxaSucesso || 0} 
                    className="w-16 h-2"
                  />
                </div>
              </div>
            ))}
          </div>
        )}
        
        {/* Summary */}
        {operadorasStatus?.length > 0 && (
          <div className="mt-6 pt-4 border-t border-border">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <p className="text-lg font-bold text-green-600 dark:text-green-400">
                  {operadorasStatus.filter((op: any) => op.status === "ativo").length}
                </p>
                <p className="text-xs text-muted-foreground">Online</p>
              </div>
              <div>
                <p className="text-lg font-bold text-red-600 dark:text-red-400">
                  {operadorasStatus.filter((op: any) => op.status === "inativo").length}
                </p>
                <p className="text-xs text-muted-foreground">Offline</p>
              </div>
              <div>
                <p className="text-lg font-bold text-foreground">
                  {Math.round(
                    operadorasStatus.reduce((acc: number, op: any) => acc + (op.taxaSucesso || 0), 0) / 
                    operadorasStatus.length
                  )}%
                </p>
                <p className="text-xs text-muted-foreground">Taxa Média</p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
