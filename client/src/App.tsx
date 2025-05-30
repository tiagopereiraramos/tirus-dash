import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './lib/queryClient';
import Layout from './components/layout/Layout';
import Dashboard from './pages/dashboard-correto';
import Operadoras from './pages/operadoras-funcional';
import Clientes from './pages/clientes-funcional';
import Faturas from './pages/faturas-limpo';
import Aprovacoes from './pages/aprovacoes-limpo';
import Execucoes from './pages/execucoes';
import Upload from './pages/upload-avulso';
import Notificacoes from './pages/notificacoes';
import Configuracoes from './pages/configuracoes';
import './index.css';

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