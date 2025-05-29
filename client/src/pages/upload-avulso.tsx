import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Upload, FileText, ArrowLeft } from "lucide-react";
import { Link } from "wouter";

interface UploadForm {
  cliente_id: number;
  mes_ano: string;
  arquivo: File;
  observacoes?: string;
}

export default function UploadAvulso() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const form = useForm<UploadForm>();

  const { data: clientes } = useQuery({
    queryKey: ["/api/clientes"],
  });

  const uploadMutation = useMutation({
    mutationFn: async (data: FormData) => {
      const response = await fetch("/api/upload-avulso", {
        method: "POST",
        body: data,
      });
      if (!response.ok) throw new Error("Erro no upload");
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Upload realizado",
        description: "Arquivo enviado com sucesso para processamento.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/faturas"] });
      form.reset();
      setSelectedFile(null);
    },
    onError: () => {
      toast({
        title: "Erro no upload",
        description: "Não foi possível enviar o arquivo.",
        variant: "destructive",
      });
    },
  });

  const onSubmit = async (data: UploadForm) => {
    if (!selectedFile) {
      toast({
        title: "Arquivo obrigatório",
        description: "Selecione um arquivo para upload.",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append("arquivo", selectedFile);
      formData.append("cliente_id", data.cliente_id.toString());
      formData.append("mes_ano", data.mes_ano);
      if (data.observacoes) {
        formData.append("observacoes", data.observacoes);
      }

      await uploadMutation.mutateAsync(formData);
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Verificar se é PDF
      if (file.type !== "application/pdf") {
        toast({
          title: "Formato inválido",
          description: "Apenas arquivos PDF são aceitos.",
          variant: "destructive",
        });
        return;
      }
      setSelectedFile(file);
    }
  };

  const clientesData = clientes || [];

  return (
    <div className="space-y-8 p-8">
      <div className="flex items-center space-x-4">
        <Link href="/faturas">
          <Button variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">Upload Avulso</h1>
          <p className="text-muted-foreground">Envio manual de faturas para o sistema</p>
        </div>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Upload className="h-5 w-5" />
            <span>Enviar Fatura</span>
          </CardTitle>
          <CardDescription>
            Faça o upload de uma fatura em PDF para processamento manual
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="cliente_id"
                  rules={{ required: "Cliente é obrigatório" }}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Cliente</FormLabel>
                      <Select onValueChange={(value) => field.onChange(parseInt(value))}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione o cliente" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {clientesData.map((cliente: any) => (
                            <SelectItem key={cliente.id} value={cliente.id.toString()}>
                              {cliente.nome_sat}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="mes_ano"
                  rules={{ required: "Mês/Ano é obrigatório" }}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Mês/Ano</FormLabel>
                      <FormControl>
                        <Input 
                          placeholder="MM/AAAA" 
                          pattern="^\d{2}/\d{4}$"
                          {...field} 
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="arquivo"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Arquivo da Fatura</FormLabel>
                    <FormControl>
                      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
                        <div className="text-center">
                          <FileText className="mx-auto h-12 w-12 text-gray-400" />
                          <div className="mt-4">
                            <label htmlFor="file-upload" className="cursor-pointer">
                              <span className="mt-2 block text-sm font-medium text-gray-900">
                                {selectedFile ? selectedFile.name : "Clique para selecionar um arquivo PDF"}
                              </span>
                              <input
                                id="file-upload"
                                name="file-upload"
                                type="file"
                                accept=".pdf"
                                className="sr-only"
                                onChange={handleFileChange}
                              />
                            </label>
                          </div>
                          <p className="text-xs text-gray-500">
                            PDF até 10MB
                          </p>
                        </div>
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="observacoes"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Observações (opcional)</FormLabel>
                    <FormControl>
                      <Input placeholder="Observações sobre a fatura" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex space-x-4">
                <Button 
                  type="submit" 
                  disabled={isUploading || !selectedFile}
                  className="flex-1"
                >
                  {isUploading ? "Enviando..." : "Enviar Fatura"}
                </Button>
                <Link href="/faturas">
                  <Button variant="outline" className="flex-1">
                    Cancelar
                  </Button>
                </Link>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  );
}