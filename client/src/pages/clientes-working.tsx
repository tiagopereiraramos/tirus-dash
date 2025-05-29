import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Users, Plus, Building2, MapPin } from "lucide-react";

export default function Clientes() {
  const { data: clientes, isLoading } = useQuery({ 
    queryKey: ["/api/clientes"] 
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Carregando clientes...</div>
      </div>
    );
  }

  const clientesData = Array.isArray(clientes) ? clientes : [];

  return (
    <div className="space-y-8 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Clientes</h1>
          <p className="text-muted-foreground">Gerenciar clientes da BGTELECOM</p>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Adicionar Cliente
        </Button>
      </div>

      <div className="grid gap-6">
        {clientesData.map((cliente: any) => (
          <Card key={cliente.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-lg">{cliente.nome_sat}</CardTitle>
                  <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                    <span>CNPJ: {cliente.cnpj}</span>
                  </div>
                </div>
                <Badge variant={cliente.status_ativo ? "default" : "secondary"}>
                  {cliente.status_ativo ? "Ativo" : "Inativo"}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="flex items-center space-x-2">
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Operadora</p>
                    <p className="text-sm text-muted-foreground">{cliente.operadora_nome}</p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Unidade</p>
                    <p className="text-sm text-muted-foreground">{cliente.unidade}</p>
                  </div>
                </div>
                
                <div className="flex justify-end space-x-2">
                  <Button variant="outline" size="sm">
                    Editar
                  </Button>
                  <Button variant="outline" size="sm">
                    Ver Faturas
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {clientesData.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Users className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Nenhum cliente encontrado</h3>
            <p className="text-muted-foreground text-center mb-4">
              Adicione clientes para começar a gerenciar faturas e execuções RPA.
            </p>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Adicionar Primeiro Cliente
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}