import { Bell, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useQuery } from "@tanstack/react-query";

export default function Header() {
  const { data: notificacoes } = useQuery({
    queryKey: ["/api/notificacoes"],
  });

  const notificacoesNaoLidas = notificacoes?.filter((n: any) => !n.lida)?.length || 0;

  return (
    <div className="fixed top-0 left-64 right-0 h-16 bg-card border-b border-border z-40 flex items-center justify-between px-6">
      {/* Left side - Title */}
      <div className="flex items-center space-x-4">
        <div>
          <h2 className="text-xl font-semibold text-foreground">Dashboard Geral</h2>
          <p className="text-sm text-muted-foreground">
            Visão geral do sistema RPA BGTelecom
          </p>
        </div>
      </div>

      {/* Right side - Notifications and User */}
      <div className="flex items-center space-x-4">
        {/* Notifications */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="h-5 w-5" />
              {notificacoesNaoLidas > 0 && (
                <Badge 
                  variant="destructive" 
                  className="absolute -top-1 -right-1 px-1 min-w-[18px] h-[18px] text-xs"
                >
                  {notificacoesNaoLidas}
                </Badge>
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-80" align="end">
            <DropdownMenuLabel>Notificações</DropdownMenuLabel>
            <DropdownMenuSeparator />
            {notificacoes?.slice(0, 5).map((notificacao: any) => (
              <DropdownMenuItem key={notificacao.id} className="flex flex-col items-start p-3">
                <div className="font-medium text-sm">{notificacao.titulo}</div>
                <div className="text-xs text-muted-foreground">{notificacao.mensagem}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {new Date(notificacao.createdAt).toLocaleString("pt-BR")}
                </div>
              </DropdownMenuItem>
            ))}
            {notificacoes?.length === 0 && (
              <DropdownMenuItem>
                <div className="text-sm text-muted-foreground">Nenhuma notificação</div>
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="flex items-center space-x-2 h-auto p-2">
              <div className="text-right">
                <p className="text-sm font-medium text-foreground">Admin RPA</p>
                <p className="text-xs text-muted-foreground">Administrador</p>
              </div>
              <Avatar className="h-8 w-8">
                <AvatarImage src="" alt="Admin" />
                <AvatarFallback className="bg-primary text-primary-foreground">
                  <User className="h-4 w-4" />
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56" align="end">
            <DropdownMenuLabel>Minha Conta</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <User className="mr-2 h-4 w-4" />
              <span>Perfil</span>
            </DropdownMenuItem>
            <DropdownMenuItem>
              <Bell className="mr-2 h-4 w-4" />
              <span>Notificações</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem>
              <span>Sair</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}
