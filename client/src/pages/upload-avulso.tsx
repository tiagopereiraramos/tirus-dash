import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function UploadAvulso() {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Upload Avulso</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>Upload de Fatura</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="arquivo">Selecionar Arquivo</Label>
            <Input id="arquivo" type="file" accept=".pdf,.jpg,.png" />
          </div>
          
          <div>
            <Label htmlFor="observacoes">Observações</Label>
            <Input id="observacoes" placeholder="Observações sobre o upload" />
          </div>
          
          <Button>Fazer Upload</Button>
        </CardContent>
      </Card>
    </div>
  );
}