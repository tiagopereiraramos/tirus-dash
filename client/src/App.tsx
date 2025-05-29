import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "next-themes";
import NotFound from "@/pages/not-found";
import Dashboard from "@/pages/dashboard";
import Execucoes from "@/pages/execucoes";
import Aprovacoes from "@/pages/aprovacoes";
import Operadoras from "@/pages/operadoras";
import Clientes from "@/pages/clientes";
import Faturas from "@/pages/faturas";
import Notificacoes from "@/pages/notificacoes";
import Configuracoes from "@/pages/configuracoes";
import Sidebar from "@/components/layout/sidebar";
import Header from "@/components/layout/header";
import { WebSocketProvider } from "@/lib/websocket";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Dashboard} />
      <Route path="/execucoes" component={Execucoes} />
      <Route path="/aprovacoes" component={Aprovacoes} />
      <Route path="/operadoras" component={Operadoras} />
      <Route path="/clientes" component={Clientes} />
      <Route component={NotFound} />
    </Switch>
  );
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 ml-64">
        <Header />
        <main className="pt-16 p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="light">
        <TooltipProvider>
          <WebSocketProvider>
            <Layout>
              <Router />
            </Layout>
            <Toaster />
          </WebSocketProvider>
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
