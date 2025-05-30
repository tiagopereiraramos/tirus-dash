import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

export default function AdicionarCliente() {
  const { data: operadorasData } = useQuery({
    queryKey: ["/operadoras"],
    retry: false,
  });

  const operadoras = operadorasData?.operadoras || [];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Adicionar Cliente</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Novo Cliente</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="nome_sat">Nome SAT</Label>
              <Input id="nome_sat" placeholder="Nome do cliente no SAT" />
            </div>
            <div>
              <Label htmlFor="cnpj">CNPJ</Label>
              <Input id="cnpj" placeholder="CNPJ do cliente" />
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="unidade">Unidade</Label>
              <Input id="unidade" placeholder="Unidade do cliente" />
            </div>
            <div>
              <Label htmlFor="operadora">Operadora</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione uma operadora" />
                </SelectTrigger>
                <SelectContent>
                  {operadoras.map((op: any) => (
                    <SelectItem key={op.id} value={op.id.toString()}>
                      {op.nome}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="flex gap-2">
            <Button>Salvar Cliente</Button>
            <Button variant="outline">Cancelar</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}