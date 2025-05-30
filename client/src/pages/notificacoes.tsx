import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Bell, Check, X, AlertCircle, Info, AlertTriangle, CheckCircle } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

export default function Notificacoes() {
  const [filtroLida, setFiltroLida] = useState<string>("todas");
  const [filtroTipo, setFiltroTipo] = useState<string>("todos");
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: notificacoes, isLoading } = useQuery({
    queryKey: ["/api/notificacoes"],
  });

  const marcarLidaMutation = useMutation({
    mutationFn: (notificacaoId: number) => 
      apiRequest("PATCH", `/api/notificacoes/${notificacaoId}/marcar-lida`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/notificacoes"] });
      toast({
        title: "Notificação marcada como lida",
      });
    },
  });

  const getNotificationIcon = (tipo: string) => {
    switch (tipo) {
      case "error":
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case "warning":
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case "success":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "info":
        return <Info className="h-5 w-5 text-blue-500" />;
      default:
        return <Bell className="h-5 w-5 text-gray-500" />;
    }
  };

  const getNotificationBadge = (tipo: string) => {
    switch (tipo) {
      case "error":
        return <Badge variant="destructive">Erro</Badge>;
      case "warning":
        return <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400">Aviso</Badge>;
      case "success":
        return <Badge className="bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400">Sucesso</Badge>;
      case "info":
        return <Badge variant="secondary">Info</Badge>;
      default:
        return <Badge variant="outline">{tipo}</Badge>;
    }
  };

  const notificacoesData = notificacoes?.data || [];
  const notificacoesFiltradas = notificacoesData.filter((notif: any) => {
    const filtroLidaMatch = filtroLida === "todas" || 
      (filtroLida === "lidas" && notif.lida) ||
      (filtroLida === "nao-lidas" && !notif.lida);
    
    const filtroTipoMatch = filtroTipo === "todos" || notif.tipo === filtroTipo;
    
    return filtroLidaMatch && filtroTipoMatch;
  }) || [];

  const naoLidasCount = notificacoesData.filter((notif: any) => !notif.lida).length || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold text-foreground">Central de Notificações</h2>
        <p className="text-muted-foreground">
          Acompanhe todas as notificações e alertas do sistema RPA
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total</p>
                <p className="text-2xl font-bold text-foreground">{notificacoes?.length || 0}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                <Bell className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Não Lidas</p>
                <p className="text-2xl font-bold text-foreground">{naoLidasCount}</p>
              </div>
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/20 rounded-lg flex items-center justify-center">
                <AlertCircle className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Hoje</p>
                <p className="text-2xl font-bold text-foreground">8</p>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                <CheckCircle className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Críticas</p>
                <p className="text-2xl font-bold text-foreground">2</p>
              </div>
              <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg flex items-center justify-center">
                <AlertTriangle className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex gap-2">
              <Button
                variant={filtroLida === "todas" ? "default" : "outline"}
                size="sm"
                onClick={() => setFiltroLida("todas")}
              >
                Todas
              </Button>
              <Button
                variant={filtroLida === "nao-lidas" ? "default" : "outline"}
                size="sm"
                onClick={() => setFiltroLida("nao-lidas")}
              >
                Não Lidas
              </Button>
              <Button
                variant={filtroLida === "lidas" ? "default" : "outline"}
                size="sm"
                onClick={() => setFiltroLida("lidas")}
              >
                Lidas
              </Button>
            </div>
            
            <div className="flex gap-2">
              <Button
                variant={filtroTipo === "todos" ? "default" : "outline"}
                size="sm"
                onClick={() => setFiltroTipo("todos")}
              >
                Todos Tipos
              </Button>
              <Button
                variant={filtroTipo === "error" ? "destructive" : "outline"}
                size="sm"
                onClick={() => setFiltroTipo("error")}
              >
                Erros
              </Button>
              <Button
                variant={filtroTipo === "warning" ? "default" : "outline"}
                size="sm"
                onClick={() => setFiltroTipo("warning")}
                className="bg-yellow-500 hover:bg-yellow-600"
              >
                Avisos
              </Button>
              <Button
                variant={filtroTipo === "success" ? "default" : "outline"}
                size="sm"
                onClick={() => setFiltroTipo("success")}
                className="bg-green-500 hover:bg-green-600"
              >
                Sucesso
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notifications List */}
      <div className="space-y-4">
        {notificacoesFiltradas.map((notificacao: any) => (
          <Card key={notificacao.id} className={`transition-all ${!notificacao.lida ? 'border-l-4 border-l-blue-500' : ''}`}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4 flex-1">
                  <div className="mt-1">
                    {getNotificationIcon(notificacao.tipo)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className={`font-medium ${!notificacao.lida ? 'font-semibold' : ''}`}>
                        {notificacao.titulo}
                      </h3>
                      {getNotificationBadge(notificacao.tipo)}
                      {!notificacao.lida && (
                        <Badge variant="secondary" className="text-xs">Nova</Badge>
                      )}
                    </div>
                    <p className="text-muted-foreground text-sm mb-3">
                      {notificacao.mensagem}
                    </p>
                    <div className="text-xs text-muted-foreground">
                      {notificacao.createdAt 
                        ? format(new Date(notificacao.createdAt), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })
                        : "Data não informada"
                      }
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  {!notificacao.lida && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => marcarLidaMutation.mutate(notificacao.id)}
                      disabled={marcarLidaMutation.isPending}
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                  )}
                  <Button variant="ghost" size="sm">
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        
        {notificacoesFiltradas.length === 0 && !isLoading && (
          <Card>
            <CardContent className="p-12 text-center">
              <Bell className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">Nenhuma notificação encontrada</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}