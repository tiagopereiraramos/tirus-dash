import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/layout/Layout';
import Dashboard from './pages/dashboard-correto';
import Operadoras from './pages/operadoras-funcional';
import Clientes from './pages/clientes-funcional';
import Faturas from './pages/faturas-correto';
import Aprovacoes from './pages/aprovacoes-correto';
import Execucoes from './pages/execucoes';
import Upload from './pages/upload-avulso';
import Notificacoes from './pages/notificacoes';
import Configuracoes from './pages/configuracoes';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryFn: async ({ queryKey }) => {
        const url = queryKey[0].toString().startsWith('/api') ? queryKey[0] : `/api${queryKey[0]}`;
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      },
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="/operadoras" element={<Operadoras />} />
            <Route path="/clientes" element={<Clientes />} />
            <Route path="/faturas" element={<Faturas />} />
            <Route path="/aprovacoes" element={<Aprovacoes />} />
            <Route path="/execucoes" element={<Execucoes />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/notificacoes" element={<Notificacoes />} />
            <Route path="/configuracoes" element={<Configuracoes />} />
          </Route>
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}

export default App;