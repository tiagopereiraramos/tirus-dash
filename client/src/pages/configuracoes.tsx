import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Settings, Database, Bell, Shield, Download, Upload } from "lucide-react";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

export default function Configuracoes() {
  const [configuracoes, setConfiguracoes] = useState({
    notificacaoEmail: true,
    notificacaoSms: false,
    execucaoAutomatica: true,
    intervaloCron: "0 2 * * *", // 2h da manhã todos os dias
    timeoutExecucao: 1800, // 30 minutos
    tentativasMaximas: 3,
  });

  const { toast } = useToast();

  const inicializarDadosMutation = useMutation({
    mutationFn: () => apiRequest("POST", "/api/initialize-data"),
    onSuccess: () => {
      toast({
        title: "Dados inicializados",
        description: "Base de dados populada com sucesso a partir do CSV",
      });
    },
    onError: () => {
      toast({
        title: "Erro",
        description: "Falha ao inicializar dados",
        variant: "destructive",
      });
    },
  });

  const salvarConfiguracoesMutation = useMutation({
    mutationFn: (dados: any) => apiRequest("POST", "/api/configuracoes", dados),
    onSuccess: () => {
      toast({
        title: "Configurações salvas",
        description: "As configurações foram atualizadas com sucesso",
      });
    },
    onError: () => {
      toast({
        title: "Erro",
        description: "Falha ao salvar configurações",
        variant: "destructive",
      });
    },
  });

  const handleSalvarConfiguracoes = () => {
    salvarConfiguracoesMutation.mutate(configuracoes);
  };

  const handleInicializarDados = () => {
    inicializarDadosMutation.mutate();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-foreground">Configurações do Sistema</h2>
        <p className="text-muted-foreground">
          Gerencie as configurações globais do sistema RPA
        </p>
      </div>

      <Tabs defaultValue="geral" className="space-y-4">
        <TabsList>
          <TabsTrigger value="geral">Geral</TabsTrigger>
          <TabsTrigger value="notificacoes">Notificações</TabsTrigger>
          <TabsTrigger value="execucoes">Execuções</TabsTrigger>
          <TabsTrigger value="dados">Dados</TabsTrigger>
        </TabsList>

        <TabsContent value="geral" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="h-5 w-5" />
                <span>Configurações Gerais</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="sistema-nome">Nome do Sistema</Label>
                  <Input id="sistema-nome" value="RPA Telecom Orchestrator" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="versao">Versão</Label>
                  <Input id="versao" value="1.0.0" disabled />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="timezone">Fuso Horário</Label>
                <Input id="timezone" value="America/Sao_Paulo" />
              </div>
              <div className="flex items-center space-x-2">
                <Switch id="modo-debug" />
                <Label htmlFor="modo-debug">Modo Debug</Label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="notificacoes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Bell className="h-5 w-5" />
                <span>Configurações de Notificações</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Notificações por Email</Label>
                  <p className="text-sm text-muted-foreground">
                    Receber notificações sobre execuções por email
                  </p>
                </div>
                <Switch
                  checked={configuracoes.notificacaoEmail}
                  onCheckedChange={(checked) =>
                    setConfiguracoes(prev => ({ ...prev, notificacaoEmail: checked }))
                  }
                />
              </div>
              <Separator />
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Notificações por SMS</Label>
                  <p className="text-sm text-muted-foreground">
                    Receber alertas críticos por SMS
                  </p>
                </div>
                <Switch
                  checked={configuracoes.notificacaoSms}
                  onCheckedChange={(checked) =>
                    setConfiguracoes(prev => ({ ...prev, notificacaoSms: checked }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email-admin">Email do Administrador</Label>
                <Input id="email-admin" placeholder="admin@empresa.com" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="telefone-admin">Telefone para SMS</Label>
                <Input id="telefone-admin" placeholder="+55 11 99999-9999" />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="execucoes" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5" />
                <span>Configurações de Execução RPA</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Execução Automática</Label>
                  <p className="text-sm text-muted-foreground">
                    Executar RPAs automaticamente conforme agendamento
                  </p>
                </div>
                <Switch
                  checked={configuracoes.execucaoAutomatica}
                  onCheckedChange={(checked) =>
                    setConfiguracoes(prev => ({ ...prev, execucaoAutomatica: checked }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cron-interval">Expressão Cron</Label>
                <Input
                  id="cron-interval"
                  value={configuracoes.intervaloCron}
                  onChange={(e) =>
                    setConfiguracoes(prev => ({ ...prev, intervaloCron: e.target.value }))
                  }
                  placeholder="0 2 * * *"
                />
                <p className="text-xs text-muted-foreground">
                  Exemplo: "0 2 * * *" = Todo dia às 2h da manhã
                </p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="timeout">Timeout (segundos)</Label>
                  <Input
                    id="timeout"
                    type="number"
                    value={configuracoes.timeoutExecucao}
                    onChange={(e) =>
                      setConfiguracoes(prev => ({ ...prev, timeoutExecucao: parseInt(e.target.value) }))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="tentativas">Tentativas Máximas</Label>
                  <Input
                    id="tentativas"
                    type="number"
                    value={configuracoes.tentativasMaximas}
                    onChange={(e) =>
                      setConfiguracoes(prev => ({ ...prev, tentativasMaximas: parseInt(e.target.value) }))
                    }
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="dados" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Database className="h-5 w-5" />
                <span>Gestão de Dados</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 border rounded-lg bg-muted/50">
                <h4 className="font-medium mb-2">Inicializar Base de Dados</h4>
                <p className="text-sm text-muted-foreground mb-4">
                  Popula o banco de dados com os dados do arquivo CSV fornecido, incluindo clientes, operadoras, contratos e dados de exemplo.
                </p>
                <Button
                  onClick={handleInicializarDados}
                  disabled={inicializarDadosMutation.isPending}
                  className="w-full"
                >
                  <Upload className="h-4 w-4 mr-2" />
                  {inicializarDadosMutation.isPending ? "Inicializando..." : "Inicializar Dados do CSV"}
                </Button>
              </div>

              <Separator />

              <div className="grid grid-cols-2 gap-4">
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Exportar Dados
                </Button>
                <Button variant="outline">
                  <Upload className="h-4 w-4 mr-2" />
                  Importar Dados
                </Button>
              </div>

              <div className="p-4 border rounded-lg bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800">
                <h4 className="font-medium text-red-800 dark:text-red-400 mb-2">Zona Perigosa</h4>
                <p className="text-sm text-red-700 dark:text-red-300 mb-4">
                  Ações irreversíveis que podem afetar todo o sistema.
                </p>
                <div className="space-y-2">
                  <Button variant="destructive" size="sm" className="w-full">
                    Limpar Todos os Dados
                  </Button>
                  <Button variant="destructive" size="sm" className="w-full">
                    Reset Completo do Sistema
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Save Button */}
      <div className="flex justify-end">
        <Button
          onClick={handleSalvarConfiguracoes}
          disabled={salvarConfiguracoesMutation.isPending}
          className="btn-primary"
        >
          {salvarConfiguracoesMutation.isPending ? "Salvando..." : "Salvar Configurações"}
        </Button>
      </div>
    </div>
  );
}