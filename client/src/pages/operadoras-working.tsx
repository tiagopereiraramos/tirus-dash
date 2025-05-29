import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Building2, Plus, CheckCircle, AlertCircle } from "lucide-react";

export default function Operadoras() {
  const { data: operadoras, isLoading } = useQuery({ 
    queryKey: ["/api/operadoras"] 
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Carregando operadoras...</div>
      </div>
    );
  }

  const operadorasData = Array.isArray(operadoras) ? operadoras : [];

  return (
    <div className="space-y-8 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Operadoras</h1>
          <p className="text-muted-foreground">Gerenciar operadoras do sistema</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Adicionar Operadora
        </Button>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {operadorasData.map((operadora: any) => (
          <Card key={operadora.id} className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-lg font-semibold">{operadora.nome}</CardTitle>
              <Building2 className="h-5 w-5 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Código:</span>
                  <Badge variant="outline">{operadora.codigo}</Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">RPA:</span>
                  {operadora.possui_rpa ? (
                    <Badge variant="secondary">Disponível</Badge>
                  ) : (
                    <Badge variant="outline">Não disponível</Badge>
                  )}
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Status:</span>
                  <div className="flex items-center space-x-2">
                    {operadora.status_ativo ? (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="text-sm text-green-600">Ativo</span>
                      </>
                    ) : (
                      <>
                        <AlertCircle className="h-4 w-4 text-red-500" />
                        <span className="text-sm text-red-600">Inativo</span>
                      </>
                    )}
                  </div>
                </div>
                
                <div className="pt-3 flex justify-end space-x-2">
                  <Button variant="outline" size="sm">
                    Editar
                  </Button>
                  <Button variant="outline" size="sm">
                    Configurar RPA
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {operadorasData.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Building2 className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Nenhuma operadora encontrada</h3>
            <p className="text-muted-foreground text-center mb-4">
              Adicione operadoras para começar a gerenciar o sistema RPA.
            </p>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Adicionar Primeira Operadora
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}