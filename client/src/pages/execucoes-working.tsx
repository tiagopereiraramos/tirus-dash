import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Activity, Play, Square, Building2, Clock } from "lucide-react";

export default function Execucoes() {
  const { data: execucoes, isLoading } = useQuery({ 
    queryKey: ["/api/execucoes"] 
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Carregando execuções...</div>
      </div>
    );
  }

  const execucoesData = Array.isArray(execucoes) ? execucoes : [];

  return (
    <div className="space-y-8 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Execuções RPA</h1>
          <p className="text-muted-foreground">Monitorar e gerenciar execuções dos robôs</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">
            <Square className="mr-2 h-4 w-4" />
            Parar Todas
          </Button>
          <Button>
            <Play className="mr-2 h-4 w-4" />
            Executar RPA
          </Button>
        </div>
      </div>

      <div className="grid gap-6">
        {execucoesData.map((execucao: any) => (
          <Card key={execucao.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-lg">{execucao.nome_sat}</CardTitle>
                  <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                    <span>Tipo: {execucao.tipo_execucao}</span>
                    <span>•</span>
                    <span>Tentativas: {execucao.tentativas}</span>
                  </div>
                </div>
                <Badge variant={execucao.status_execucao === "EXECUTANDO" ? "default" : execucao.status_execucao === "CONCLUIDO" ? "secondary" : "destructive"}>
                  {execucao.status_execucao}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4">
                <div className="flex items-center space-x-2">
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Operadora</p>
                    <p className="text-sm text-muted-foreground">{execucao.operadora_nome}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Início</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(execucao.data_inicio).toLocaleString('pt-BR')}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Activity className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Status</p>
                    <p className="text-sm text-muted-foreground">
                      {execucao.status_execucao === "EXECUTANDO" ? "Em execução" : execucao.status_execucao === "CONCLUIDO" ? "Concluído" : "Erro"}
                    </p>
                  </div>
                </div>
                
                <div className="flex justify-end space-x-2">
                  {execucao.status_execucao === "EXECUTANDO" ? (
                    <Button variant="outline" size="sm">
                      <Square className="mr-1 h-3 w-3" />
                      Parar
                    </Button>
                  ) : (
                    <Button variant="outline" size="sm">
                      <Play className="mr-1 h-3 w-3" />
                      Reexecutar
                    </Button>
                  )}
                  <Button variant="outline" size="sm">
                    Ver Logs
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {execucoesData.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Activity className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Nenhuma execução encontrada</h3>
            <p className="text-muted-foreground text-center mb-4">
              Configure clientes e operadoras para começar a executar RPAs.
            </p>
            <Button>
              <Play className="mr-2 h-4 w-4" />
              Executar Primeiro RPA
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}