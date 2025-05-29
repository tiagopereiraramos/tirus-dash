import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { UserPlus, ArrowLeft } from "lucide-react";
import { Link } from "wouter";

interface ClienteForm {
  nome_sat: string;
  cnpj: string;
  operadora_id: number;
  unidade: string;
  filtro?: string;
  servico?: string;
  dados_sat?: string;
  login_portal?: string;
  senha_portal?: string;
  cpf?: string;
}

export default function AdicionarCliente() {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<ClienteForm>();

  const { data: operadoras } = useQuery({
    queryKey: ["/api/operadoras"],
  });

  const createClienteMutation = useMutation({
    mutationFn: async (data: ClienteForm) => {
      const response = await fetch("/api/clientes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error("Erro ao criar cliente");
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Cliente criado",
        description: "Cliente adicionado com sucesso ao sistema.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/clientes"] });
      form.reset();
    },
    onError: () => {
      toast({
        title: "Erro",
        description: "Não foi possível criar o cliente.",
        variant: "destructive",
      });
    },
  });

  const onSubmit = async (data: ClienteForm) => {
    setIsSubmitting(true);
    try {
      await createClienteMutation.mutateAsync(data);
    } finally {
      setIsSubmitting(false);
    }
  };

  const operadorasData = operadoras || [];

  return (
    <div className="space-y-8 p-8">
      <div className="flex items-center space-x-4">
        <Link href="/clientes">
          <Button variant="outline" size="sm">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Voltar
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">Adicionar Cliente</h1>
          <p className="text-muted-foreground">Cadastrar novo cliente no sistema BGTELECOM</p>
        </div>
      </div>

      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <UserPlus className="h-5 w-5" />
            <span>Dados do Cliente</span>
          </CardTitle>
          <CardDescription>
            Preencha as informações do novo cliente
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="nome_sat"
                  rules={{ required: "Nome SAT é obrigatório" }}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Nome SAT</FormLabel>
                      <FormControl>
                        <Input placeholder="Nome no sistema SAT" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="cnpj"
                  rules={{ required: "CNPJ é obrigatório" }}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>CNPJ</FormLabel>
                      <FormControl>
                        <Input placeholder="00.000.000/0000-00" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="operadora_id"
                  rules={{ required: "Operadora é obrigatória" }}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Operadora</FormLabel>
                      <Select onValueChange={(value) => field.onChange(parseInt(value))}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione a operadora" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          {operadorasData.map((operadora: any) => (
                            <SelectItem key={operadora.id} value={operadora.id.toString()}>
                              {operadora.nome}
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
                  name="unidade"
                  rules={{ required: "Unidade é obrigatória" }}
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Unidade</FormLabel>
                      <FormControl>
                        <Input placeholder="Unidade do cliente" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="filtro"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Filtro</FormLabel>
                      <FormControl>
                        <Input placeholder="Filtro para busca" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="servico"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Serviço</FormLabel>
                      <FormControl>
                        <Input placeholder="Tipo de serviço" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="login_portal"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Login Portal</FormLabel>
                      <FormControl>
                        <Input placeholder="Login da operadora" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="senha_portal"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Senha Portal</FormLabel>
                      <FormControl>
                        <Input type="password" placeholder="Senha da operadora" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="cpf"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>CPF</FormLabel>
                      <FormControl>
                        <Input placeholder="000.000.000-00" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="dados_sat"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Dados SAT</FormLabel>
                    <FormControl>
                      <Textarea 
                        placeholder="Informações adicionais do SAT" 
                        className="min-h-[100px]"
                        {...field} 
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex space-x-4">
                <Button 
                  type="submit" 
                  disabled={isSubmitting}
                  className="flex-1"
                >
                  {isSubmitting ? "Salvando..." : "Salvar Cliente"}
                </Button>
                <Link href="/clientes">
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