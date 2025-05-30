import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { 
  Upload, 
  FileText, 
  X, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  Download,
  Eye,
  Trash2
} from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useToast } from "@/hooks/use-toast";
import { apiRequest, queryClient } from "@/lib/queryClient";

// Schema de validação para upload
const uploadSchema = z.object({
  cliente_id: z.number().min(1, "Cliente é obrigatório"),
  operadora: z.string().min(1, "Operadora é obrigatória"),
  mes_referencia: z.string().min(1, "Mês de referência é obrigatório"),
  observacoes: z.string().optional(),
});

type UploadAvulso = {
  id: number;
  cliente_nome: string;
  operadora: string;
  arquivo_nome: string;
  arquivo_tamanho: number;
  mes_referencia: string;
  status: "processando" | "concluido" | "erro" | "pendente";
  progresso: number;
  data_upload: string;
  observacoes?: string;
  resultado?: {
    faturas_encontradas?: number;
    valor_total?: number;
    erros?: string[];
  };
};

export default function UploadAvulso() {
  const [arquivoSelecionado, setArquivoSelecionado] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const { toast } = useToast();

  // Configurar formulário
  const form = useForm<z.infer<typeof uploadSchema>>({
    resolver: zodResolver(uploadSchema),
    defaultValues: {
      cliente_id: 0,
      operadora: "",
      mes_referencia: "",
      observacoes: "",
    },
  });

  // Query para buscar uploads
  const { data: uploads = [], isLoading } = useQuery({
    queryKey: ["/api/uploads"],
    refetchInterval: 3000, // Auto-refresh a cada 3 segundos
  });

  // Query para buscar clientes
  const { data: clientes = [] } = useQuery({
    queryKey: ["/api/clientes"],
  });

  // Mutation para upload
  const uploadMutation = useMutation({
    mutationFn: (formData: FormData) =>
      fetch('/api/uploads', {
        method: 'POST',
        body: formData,
      }).then(res => res.json()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/uploads"] });
      toast({
        title: "Sucesso",
        description: "Arquivo enviado com sucesso e está sendo processado",
      });
      form.reset();
      setArquivoSelecionado(null);
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao enviar arquivo",
        variant: "destructive",
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) =>
      apiRequest(`/api/uploads/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/uploads"] });
      toast({
        title: "Sucesso",
        description: "Upload removido com sucesso",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Erro",
        description: error.message || "Erro ao remover upload",
        variant: "destructive",
      });
    },
  });

  // Handlers
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
        setArquivoSelecionado(file);
      } else {
        toast({
          title: "Formato inválido",
          description: "Apenas arquivos PDF são aceitos",
          variant: "destructive",
        });
      }
    }
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragOver(false);
    
    const file = event.dataTransfer.files[0];
    if (file) {
      if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
        setArquivoSelecionado(file);
      } else {
        toast({
          title: "Formato inválido",
          description: "Apenas arquivos PDF são aceitos",
          variant: "destructive",
        });
      }
    }
  };

  const handleSubmit = (data: z.infer<typeof uploadSchema>) => {
    if (!arquivoSelecionado) {
      toast({
        title: "Arquivo necessário",
        description: "Selecione um arquivo PDF para enviar",
        variant: "destructive",
      });
      return;
    }

    const formData = new FormData();
    formData.append('arquivo', arquivoSelecionado);
    formData.append('cliente_id', data.cliente_id.toString());
    formData.append('operadora', data.operadora);
    formData.append('mes_referencia', data.mes_referencia);
    if (data.observacoes) {
      formData.append('observacoes', data.observacoes);
    }

    uploadMutation.mutate(formData);
  };

  const handleDelete = (id: number) => {
    if (confirm("Tem certeza que deseja remover este upload?")) {
      deleteMutation.mutate(id);
    }
  };

  const getStatusBadge = (status: string) => {
    const config = {
      processando: { 
        variant: "default" as const, 
        className: "bg-blue-100 text-blue-700 border-blue-200",
        icon: <Clock className="h-3 w-3 mr-1 animate-pulse" />
      },
      concluido: { 
        variant: "default" as const, 
        className: "bg-green-100 text-green-700 border-green-200",
        icon: <CheckCircle className="h-3 w-3 mr-1" />
      },
      erro: { 
        variant: "destructive" as const, 
        className: "bg-red-100 text-red-700 border-red-200",
        icon: <AlertCircle className="h-3 w-3 mr-1" />
      },
      pendente: { 
        variant: "secondary" as const, 
        className: "bg-yellow-100 text-yellow-700 border-yellow-200",
        icon: <Clock className="h-3 w-3 mr-1" />
      },
    };
    
    const badgeConfig = config[status as keyof typeof config] || config.pendente;
    return (
      <Badge variant={badgeConfig.variant} className={badgeConfig.className}>
        {badgeConfig.icon}
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="p-6 space-y-6 bg-slate-50 min-h-screen">
      {/* Header com gradiente teal */}
      <div className="bg-gradient-to-r from-teal-500 to-teal-600 rounded-lg shadow-lg p-6 text-white">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Upload Avulso</h1>
            <p className="text-teal-100 mt-2">Envie faturas individualmente para processamento no sistema SAT</p>
          </div>
          <div className="flex items-center gap-2">
            <FileText className="h-6 w-6" />
            <span className="text-sm font-medium">
              {uploads.filter((u: UploadAvulso) => u.status === "processando").length} processando
            </span>
          </div>
        </div>
      </div>

      {/* Formulário de upload */}
      <Card className="border-0 shadow-lg bg-white">
        <CardHeader className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-lg">
          <CardTitle className="flex items-center text-slate-800">
            <Upload className="h-5 w-5 mr-2 text-teal-600" />
            Novo Upload de Fatura
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            {/* Área de drop de arquivo */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragOver 
                  ? 'border-teal-400 bg-teal-50' 
                  : 'border-slate-300 hover:border-teal-400 hover:bg-slate-50'
              }`}
              onDrop={handleDrop}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
            >
              {arquivoSelecionado ? (
                <div className="flex items-center justify-center space-x-3">
                  <FileText className="h-8 w-8 text-teal-600" />
                  <div className="text-left">
                    <p className="font-medium text-slate-900">{arquivoSelecionado.name}</p>
                    <p className="text-sm text-slate-500">{formatFileSize(arquivoSelecionado.size)}</p>
                  </div>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setArquivoSelecionado(null)}
                    className="text-red-600 border-red-200 hover:bg-red-50"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ) : (
                <div>
                  <Upload className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                  <p className="text-lg font-medium text-slate-600 mb-2">
                    Arraste um arquivo PDF aqui ou
                  </p>
                  <Label htmlFor="arquivo" className="cursor-pointer">
                    <span className="inline-flex items-center px-4 py-2 bg-teal-600 text-white rounded-lg hover:bg-teal-700 transition-colors">
                      Selecionar Arquivo
                    </span>
                    <Input
                      id="arquivo"
                      type="file"
                      accept=".pdf"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                  </Label>
                  <p className="text-sm text-slate-500 mt-2">Apenas arquivos PDF são aceitos</p>
                </div>
              )}
            </div>

            {/* Campos do formulário */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="cliente_id">Cliente</Label>
                <Select onValueChange={(value) => form.setValue("cliente_id", parseInt(value))}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o cliente" />
                  </SelectTrigger>
                  <SelectContent>
                    {clientes.map((cliente: any) => (
                      <SelectItem key={cliente.id} value={cliente.id.toString()}>
                        {cliente.nome}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {form.formState.errors.cliente_id && (
                  <p className="text-sm text-red-500">{form.formState.errors.cliente_id.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="operadora">Operadora</Label>
                <Select onValueChange={(value) => form.setValue("operadora", value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione a operadora" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="EMBRATEL">EMBRATEL</SelectItem>
                    <SelectItem value="VIVO">VIVO</SelectItem>
                    <SelectItem value="OI">OI</SelectItem>
                    <SelectItem value="AZUTON">AZUTON</SelectItem>
                    <SelectItem value="DIGITALNET">DIGITALNET</SelectItem>
                    <SelectItem value="SAT">SAT</SelectItem>
                  </SelectContent>
                </Select>
                {form.formState.errors.operadora && (
                  <p className="text-sm text-red-500">{form.formState.errors.operadora.message}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="mes_referencia">Mês de Referência</Label>
                <Input
                  id="mes_referencia"
                  {...form.register("mes_referencia")}
                  placeholder="Ex: 2024-12"
                />
                {form.formState.errors.mes_referencia && (
                  <p className="text-sm text-red-500">{form.formState.errors.mes_referencia.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="observacoes">Observações</Label>
                <Textarea
                  id="observacoes"
                  {...form.register("observacoes")}
                  placeholder="Observações sobre este upload..."
                  className="min-h-20"
                />
              </div>
            </div>

            <div className="flex justify-end">
              <Button
                type="submit"
                disabled={uploadMutation.isPending}
                className="bg-gradient-to-r from-teal-600 to-cyan-600 hover:from-teal-700 hover:to-cyan-700"
              >
                <Upload className="h-4 w-4 mr-2" />
                {uploadMutation.isPending ? "Enviando..." : "Enviar Arquivo"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card className="border-0 shadow-lg bg-gradient-to-br from-teal-500 to-teal-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">{uploads.length}</div>
            <div className="text-sm text-teal-100 mt-1">Total de Uploads</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-blue-500 to-blue-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {uploads.filter((u: UploadAvulso) => u.status === "processando").length}
            </div>
            <div className="text-sm text-blue-100 mt-1">Processando</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-green-500 to-green-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {uploads.filter((u: UploadAvulso) => u.status === "concluido").length}
            </div>
            <div className="text-sm text-green-100 mt-1">Concluídos</div>
          </CardContent>
        </Card>
        <Card className="border-0 shadow-lg bg-gradient-to-br from-red-500 to-red-600">
          <CardContent className="p-6 text-center">
            <div className="text-3xl font-bold text-white">
              {uploads.filter((u: UploadAvulso) => u.status === "erro").length}
            </div>
            <div className="text-sm text-red-100 mt-1">Com Erro</div>
          </CardContent>
        </Card>
      </div>

      {/* Tabela de uploads */}
      <Card className="border-0 shadow-lg bg-white">
        <CardHeader className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-t-lg">
          <CardTitle className="flex items-center text-slate-800">
            <FileText className="h-5 w-5 mr-2 text-teal-600" />
            Histórico de Uploads ({uploads.length})
          </CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-teal-600"></div>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Arquivo</TableHead>
                  <TableHead>Cliente</TableHead>
                  <TableHead>Operadora</TableHead>
                  <TableHead>Mês Ref.</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Progresso</TableHead>
                  <TableHead>Resultado</TableHead>
                  <TableHead>Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {uploads.length > 0 ? uploads.map((upload: UploadAvulso) => (
                  <TableRow key={upload.id} className="hover:bg-slate-50/50 transition-colors">
                    <TableCell className="font-medium text-slate-600">#{upload.id}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-slate-400" />
                        <div>
                          <p className="font-medium text-sm">{upload.arquivo_nome}</p>
                          <p className="text-xs text-slate-500">{formatFileSize(upload.arquivo_tamanho)}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-slate-600">{upload.cliente_nome}</TableCell>
                    <TableCell className="text-sm text-slate-600">{upload.operadora}</TableCell>
                    <TableCell className="text-sm text-slate-600">{upload.mes_referencia}</TableCell>
                    <TableCell>{getStatusBadge(upload.status)}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2 min-w-20">
                        <Progress value={upload.progresso} className="h-2 flex-1" />
                        <span className="text-xs font-medium w-8">{upload.progresso}%</span>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm">
                      {upload.resultado && (
                        <div className="space-y-1">
                          {upload.resultado.faturas_encontradas && (
                            <div className="text-green-600">✓ {upload.resultado.faturas_encontradas} faturas</div>
                          )}
                          {upload.resultado.valor_total && (
                            <div className="text-blue-600">R$ {upload.resultado.valor_total.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</div>
                          )}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-1">
                        <Button
                          variant="outline"
                          size="sm"
                          className="h-8 px-2 text-slate-600 border-slate-200 hover:bg-slate-50"
                        >
                          <Eye className="h-3 w-3" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(upload.id)}
                          disabled={deleteMutation.isPending}
                          className="h-8 px-2 text-red-600 border-red-200 hover:bg-red-50"
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )) : (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center py-8 text-slate-500">
                      Nenhum upload realizado ainda
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}