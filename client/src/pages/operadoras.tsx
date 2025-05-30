import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Building2, Plus, Settings, Activity } from "lucide-react";

interface Operadora {
  id: number;
  nome: string;
  codigo: string;
  tipo: string;
  url_login: string;
  status: string;
  created_at: string;
}

export default function Operadoras() {
  const { data: operadoras, isLoading } = useQuery<Operadora[]>({
    queryKey: ["/api/operadoras"],
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-40 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'ativo':
        return 'bg-green-100 text-green-800';
      case 'inativo':
        return 'bg-red-100 text-red-800';
      case 'manutencao':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTipoColor = (tipo: string) => {
    switch (tipo?.toLowerCase()) {
      case 'telecom':
        return 'bg-blue-100 text-blue-800';
      case 'internet':
        return 'bg-purple-100 text-purple-800';
      case 'satelite':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {operadoras?.map((operadora) => (
          <Card key={operadora.id} className="border-0 shadow-sm hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center text-lg">
                  <Building2 className="h-5 w-5 mr-2 text-blue-600" />
                  {operadora.nome}
                </CardTitle>
                <Badge className={getStatusColor(operadora.status)}>
                  {operadora.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Código:</span>
                  <span className="font-medium">{operadora.codigo}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Tipo:</span>
                  <Badge className={getTipoColor(operadora.tipo)}>
                    {operadora.tipo}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">URL Login:</span>
                  <span className="text-sm font-mono text-blue-600 truncate max-w-32">
                    {operadora.url_login}
                  </span>
                </div>
              </div>

              <div className="flex space-x-2 pt-2">
                <Button variant="outline" size="sm" className="flex-1">
                  <Settings className="h-4 w-4 mr-1" />
                  Configurar
                </Button>
                <Button variant="outline" size="sm" className="flex-1">
                  <Activity className="h-4 w-4 mr-1" />
                  Testar
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {operadoras && operadoras.length === 0 && (
        <div className="text-center py-12">
          <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhuma operadora cadastrada</h3>
          <p className="text-gray-600 mb-4">Comece adicionando sua primeira operadora de telecomunicações.</p>
          <Button className="bg-blue-600 hover:bg-blue-700">
            <Plus className="h-4 w-4 mr-2" />
            Adicionar Operadora
          </Button>
        </div>
      )}

      <Card className="border-0 shadow-sm">
        <CardHeader>
          <CardTitle>Estatísticas das Operadoras</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {operadoras?.length || 0}
              </div>
              <div className="text-sm text-gray-600">Total</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {operadoras?.filter(op => op.status.toLowerCase() === 'ativo').length || 0}
              </div>
              <div className="text-sm text-gray-600">Ativas</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {operadoras?.filter(op => op.status.toLowerCase() === 'inativo').length || 0}
              </div>
              <div className="text-sm text-gray-600">Inativas</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {operadoras?.filter(op => op.status.toLowerCase() === 'manutencao').length || 0}
              </div>
              <div className="text-sm text-gray-600">Manutenção</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}