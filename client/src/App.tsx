import React from "react";
import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";

// Simple components for now
function Dashboard() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Dashboard RPA BGTELECOM</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold">Operadoras</h2>
          <p className="text-3xl font-bold text-blue-600">6</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold">Clientes</h2>
          <p className="text-3xl font-bold text-green-600">12</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold">Processos Ativos</h2>
          <p className="text-3xl font-bold text-orange-600">24</p>
        </div>
      </div>
    </div>
  );
}

function Execucoes() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Execuções</h1>
      <div className="bg-white p-6 rounded-lg shadow">
        <p>Lista de execuções do sistema RPA</p>
      </div>
    </div>
  );
}

function Faturas() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-6">Faturas</h1>
      <div className="bg-white p-6 rounded-lg shadow">
        <p>Gestão de faturas</p>
      </div>
    </div>
  );
}

function Sidebar() {
  return (
    <div className="w-64 bg-gray-800 text-white h-screen p-4">
      <h2 className="text-lg font-bold mb-6">RPA BGTELECOM</h2>
      <nav>
        <a href="/" className="block py-2 px-4 rounded hover:bg-gray-700 mb-2">
          Dashboard
        </a>
        <a href="/execucoes" className="block py-2 px-4 rounded hover:bg-gray-700 mb-2">
          Execuções
        </a>
        <a href="/faturas" className="block py-2 px-4 rounded hover:bg-gray-700 mb-2">
          Faturas
        </a>
      </nav>
    </div>
  );
}

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 bg-gray-50 min-h-screen">
        {children}
      </main>
    </div>
  );
}

function Router() {
  return (
    <Layout>
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route path="/execucoes" component={Execucoes} />
        <Route path="/faturas" component={Faturas} />
        <Route>
          <div className="p-8">
            <h1 className="text-2xl font-bold">Página não encontrada</h1>
          </div>
        </Route>
      </Switch>
    </Layout>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider attribute="class" defaultTheme="light">
        <Router />
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;