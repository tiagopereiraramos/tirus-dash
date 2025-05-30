import { Link } from 'react-router-dom';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Building2,
  Users,
  FileText,
  CheckCircle,
  Play,
  Upload,
  Bell,
  Settings,
  LogOut
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Operadoras', href: '/operadoras', icon: Building2 },
  { name: 'Clientes', href: '/clientes', icon: Users },
  { name: 'Faturas', href: '/faturas', icon: FileText },
  { name: 'Aprovações', href: '/aprovacoes', icon: CheckCircle },
  { name: 'Execuções', href: '/execucoes', icon: Play },
  { name: 'Upload Avulso', href: '/upload', icon: Upload },
  { name: 'Notificações', href: '/notificacoes', icon: Bell },
  { name: 'Configurações', href: '/configuracoes', icon: Settings },
];

export default function Sidebar() {
  return (
    <div className="flex h-full w-64 flex-col bg-gray-900">
      <div className="flex h-16 items-center justify-center px-4">
        <h1 className="text-xl font-bold text-white">RPA BGTELECOM</h1>
      </div>
      
      <nav className="flex-1 space-y-1 px-2 py-4">
        {navigation.map((item) => (
          <Link
            key={item.name}
            to={item.href}
            className="group flex items-center px-2 py-2 text-sm font-medium rounded-md text-gray-300 hover:bg-gray-700 hover:text-white"
          >
            <item.icon className="mr-3 h-5 w-5 flex-shrink-0 text-gray-400 group-hover:text-gray-300" />
            {item.name}
          </Link>
        ))}
      </nav>

      <div className="flex-shrink-0 p-4">
        <button className="group flex w-full items-center px-2 py-2 text-sm font-medium text-gray-300 rounded-md hover:bg-gray-700 hover:text-white">
          <LogOut className="mr-3 h-5 w-5 flex-shrink-0 text-gray-400 group-hover:text-gray-300" />
          Sair
        </button>
      </div>
    </div>
  );
}