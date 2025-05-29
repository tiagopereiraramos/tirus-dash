import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Users, Building2, MapPin } from "lucide-react";

export default function Clientes() {
  const { data: clientes, isLoading } = useQuery({
    queryKey: ["/api/clientes"],
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const clientesData = clientes || [];

  return (
    <div className="space-y-8 p-8">
      <div>
        <h1 className="text-3xl font-bold">Clientes</h1>
        <p className="text-muted-foreground">Gestão dos clientes BGTELECOM</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {clientesData.map((cliente: any) => (
          <Card key={cliente.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Users className="h-8 w-8 text-primary" />
                  <div>
                    <CardTitle className="text-lg">{cliente.nome_sat}</CardTitle>
                    <CardDescription>CNPJ: {cliente.cnpj}</CardDescription>
                  </div>
                </div>
                <Badge variant={cliente.status_ativo ? 'default' : 'secondary'}>
                  {cliente.status_ativo ? 'Ativo' : 'Inativo'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">{cliente.unidade}</span>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">Operadora: {cliente.operadora_nome}</span>
                </div>
                
                <div className="pt-4 border-t">
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      Ver Detalhes
                    </Button>
                    <Button size="sm" className="flex-1">
                      Executar RPA
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {clientesData.length === 0 && (
        <div className="text-center py-12">
          <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Nenhum cliente encontrado</p>
        </div>
      )}
    </div>
  );
}