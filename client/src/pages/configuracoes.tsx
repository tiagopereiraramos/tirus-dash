import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function Configuracoes() {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Configurações</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Configurações do Sistema</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="timeout">Timeout RPA (minutos)</Label>
            <Input id="timeout" type="number" defaultValue="45" />
          </div>
          
          <div>
            <Label htmlFor="retries">Número de Tentativas</Label>
            <Input id="retries" type="number" defaultValue="3" />
          </div>
          
          <Button>Salvar Configurações</Button>
        </CardContent>
      </Card>
    </div>
  );
}