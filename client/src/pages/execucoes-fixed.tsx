import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, Clock, CheckCircle, AlertCircle } from "lucide-react";

export default function Execucoes() {
  const { data: execucoes, isLoading } = useQuery({
    queryKey: ["/api/execucoes"],
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const execucoesData = execucoes || [];

  return (
    <div className="space-y-8 p-8">
      <div>
        <h1 className="text-3xl font-bold">Execuções RPA</h1>
        <p className="text-muted-foreground">Monitoramento em tempo real das automações</p>
      </div>

      <div className="space-y-4">
        {execucoesData.map((execucao: any) => (
          <Card key={execucao.id} className="hover:shadow-lg transition-shadow">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className={`w-4 h-4 rounded-full ${
                    execucao.status_execucao === 'EXECUTANDO' ? 'bg-yellow-500 animate-pulse' :
                    execucao.status_execucao === 'CONCLUIDO' ? 'bg-green-500' : 'bg-red-500'
                  }`} />
                  
                  <div>
                    <h3 className="font-semibold">{execucao.nome_sat}</h3>
                    <p className="text-sm text-muted-foreground">
                      {execucao.operadora_nome} - {execucao.tipo_execucao}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Iniciado em</p>
                    <p className="text-sm">{new Date(execucao.data_inicio).toLocaleString()}</p>
                  </div>

                  <Badge variant={
                    execucao.status_execucao === 'EXECUTANDO' ? 'default' :
                    execucao.status_execucao === 'CONCLUIDO' ? 'secondary' : 'destructive'
                  }>
                    {execucao.status_execucao}
                  </Badge>

                  <div className="text-center">
                    <p className="text-sm text-muted-foreground">Tentativas</p>
                    <p className="text-sm font-medium">{execucao.tentativas}</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {execucoesData.length === 0 && (
        <div className="text-center py-12">
          <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Nenhuma execução em andamento</p>
        </div>
      )}
    </div>
  );
}