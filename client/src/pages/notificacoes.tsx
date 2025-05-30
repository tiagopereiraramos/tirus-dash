import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function Notificacoes() {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Notificações</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Sistema de Notificações</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">Nenhuma notificação no momento</p>
            <Badge variant="outline">Sistema Online</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}