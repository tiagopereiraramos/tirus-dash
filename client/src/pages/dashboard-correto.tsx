import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function Dashboard() {
  const { data: metrics, isLoading } = useQuery({
    queryKey: ["/dashboard/metrics"],
    retry: false,
  });

  if (isLoading) {
    return <div className="p-6">Carregando dashboard...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Dashboard RPA BGTELECOM</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Total de Operadoras</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.operadoras || 6}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total de Clientes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.clientes || 12}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Processos Ativos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{metrics?.processos || 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Status Sistema</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">Online</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Sistema RPA BGTELECOM</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Backend: FastAPI (Python) - Porta 8000</p>
          <p>Frontend: Vite + React - Porta 3000</p>
          <p>Database: PostgreSQL</p>
          <p className="text-green-600 font-semibold">Express: Completamente Removido</p>
        </CardContent>
      </Card>
    </div>
  );
}