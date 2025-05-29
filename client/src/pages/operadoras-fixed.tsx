import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Building2, CheckCircle, XCircle, Settings } from "lucide-react";

export default function Operadoras() {
  const { data: operadoras, isLoading } = useQuery({
    queryKey: ["/api/operadoras"],
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="h-48 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const operadorasData = operadoras || [];

  return (
    <div className="space-y-8 p-8">
      <div>
        <h1 className="text-3xl font-bold">Operadoras</h1>
        <p className="text-muted-foreground">Gestão das operadoras de telecomunicações</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {operadorasData.map((operadora: any) => (
          <Card key={operadora.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Building2 className="h-8 w-8 text-primary" />
                  <div>
                    <CardTitle className="text-lg">{operadora.nome}</CardTitle>
                    <CardDescription>Código: {operadora.codigo}</CardDescription>
                  </div>
                </div>
                <Badge variant={operadora.status_ativo ? 'default' : 'secondary'}>
                  {operadora.status_ativo ? 'Ativo' : 'Inativo'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">RPA Disponível</span>
                  <div className="flex items-center space-x-2">
                    {operadora.possui_rpa ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-500" />
                    )}
                    <span className="text-sm">
                      {operadora.possui_rpa ? 'Sim' : 'Não'}
                    </span>
                  </div>
                </div>
                
                <div className="pt-4 border-t">
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Settings className="h-4 w-4 mr-2" />
                      Configurar
                    </Button>
                    <Button 
                      size="sm" 
                      className="flex-1"
                      disabled={!operadora.possui_rpa}
                    >
                      Executar RPA
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {operadorasData.length === 0 && (
        <div className="text-center py-12">
          <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Nenhuma operadora encontrada</p>
        </div>
      )}
    </div>
  );
}