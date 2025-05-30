import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function Aprovacoes() {
  const { data: aprovacoes, isLoading } = useQuery({
    queryKey: ["/aprovacoes"],
    retry: false,
  });

  if (isLoading) {
    return <div className="p-6">Carregando aprovações...</div>;
  }

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Aprovações Pendentes</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Faturas para Aprovação</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">Nenhuma aprovação pendente no momento</p>
            <Button variant="outline">Atualizar Lista</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}