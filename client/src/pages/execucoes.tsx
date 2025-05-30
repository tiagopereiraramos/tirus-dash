import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Play, Square, RefreshCw } from "lucide-react";

export default function Execucoes() {
  const { data: execucoes = [], isLoading } = useQuery({
    queryKey: ["/execucoes"],
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'EXECUTANDO': return 'bg-blue-500';
      case 'CONCLUIDO': return 'bg-green-500';
      case 'ERRO': return 'bg-red-500';
      case 'PENDENTE': return 'bg-yellow-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Execuções RPA</h1>
        <div className="space-x-2">
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
          <Button size="sm">
            <Play className="h-4 w-4 mr-2" />
            Nova Execução
          </Button>
        </div>
      </div>

      <div className="grid gap-4">
        {Array.isArray(execucoes) && execucoes.length > 0 ? (
          execucoes.map((execucao: any) => (
            <Card key={execucao.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg">{execucao.processo_nome || `Processo ${execucao.id}`}</CardTitle>
                    <p className="text-sm text-gray-600">{execucao.operadora_nome} - {execucao.cliente_nome}</p>
                  </div>
                  <Badge className={getStatusColor(execucao.status)}>
                    {execucao.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="font-medium">Data Início:</span>
                    <p>{execucao.data_inicio ? new Date(execucao.data_inicio).toLocaleString('pt-BR') : 'N/A'}</p>
                  </div>
                  <div>
                    <span className="font-medium">Data Fim:</span>
                    <p>{execucao.data_fim ? new Date(execucao.data_fim).toLocaleString('pt-BR') : 'Em execução'}</p>
                  </div>
                  <div>
                    <span className="font-medium">Faturas:</span>
                    <p>{execucao.quantidade_faturas || 0} processadas</p>
                  </div>
                  <div className="flex space-x-2">
                    {execucao.status === 'EXECUTANDO' && (
                      <Button variant="destructive" size="sm">
                        <Square className="h-4 w-4 mr-1" />
                        Parar
                      </Button>
                    )}
                    <Button variant="outline" size="sm">
                      Ver Detalhes
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : (
          <Card>
            <CardContent className="text-center py-8">
              <p className="text-gray-500">Nenhuma execução encontrada</p>
              <Button className="mt-4">
                <Play className="h-4 w-4 mr-2" />
                Iniciar Nova Execução
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}