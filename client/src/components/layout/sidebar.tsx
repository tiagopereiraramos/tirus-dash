import { Link, useLocation } from "wouter";
import { cn } from "@/lib/utils";
import { 
  Home, 
  Building2, 
  Users, 
  FileText, 
  CheckCircle, 
  Upload, 
  UserPlus, 
  Bell, 
  Settings,
  Play
} from "lucide-react";

const navItems = [
  { href: "/", label: "Dashboard", icon: Home },
  { href: "/operadoras", label: "Operadoras", icon: Building2 },
  { href: "/clientes", label: "Clientes", icon: Users },
  { href: "/faturas", label: "Faturas", icon: FileText },
  { href: "/execucoes", label: "Execuções", icon: Play },
  { href: "/aprovacoes", label: "Aprovações", icon: CheckCircle },
  { href: "/adicionar-cliente", label: "Adicionar Cliente", icon: UserPlus },
  { href: "/upload-avulso", label: "Upload Avulso", icon: Upload },
  { href: "/notificacoes", label: "Notificações", icon: Bell },
  { href: "/configuracoes", label: "Configurações", icon: Settings },
];

export default function Sidebar() {
  const [location] = useLocation();

  return (
    <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 h-screen p-4">
      <div className="mb-8">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">RPA BGTELECOM</h1>
        <p className="text-sm text-gray-500">Sistema de Orquestração</p>
      </div>
      
      <nav className="space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location === item.href;
          
          return (
            <Link key={item.href} href={item.href}>
              <div
                className={cn(
                  "flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors",
                  isActive
                    ? "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300"
                    : "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                )}
              >
                <Icon className="h-5 w-5" />
                <span className="text-sm font-medium">{item.label}</span>
              </div>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}