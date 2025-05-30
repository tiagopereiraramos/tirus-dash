import type { Express } from "express";
import express from "express";
import { createServer, type Server } from "http";

export async function registerRoutes(app: Express): Promise<Server> {
  
  // Middleware para capturar o body das requisições
  app.use(express.json());
  
  // Proxy simples para redirecionar TODAS as chamadas /api para o FastAPI
  app.use('/api', async (req, res) => {
    try {
      const fastApiUrl = `http://localhost:8000${req.originalUrl}`;
      console.log(`Redirecionando ${req.method} ${req.originalUrl} para ${fastApiUrl}`);
      
      const options: any = {
        method: req.method,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        }
      };
      
      // Se for POST, PUT ou PATCH, incluir o body
      if (['POST', 'PUT', 'PATCH'].includes(req.method) && req.body) {
        options.body = JSON.stringify(req.body);
      }
      
      const response = await fetch(fastApiUrl, options);
      const data = await response.json();
      
      res.status(response.status).json(data);
    } catch (error) {
      console.error('Erro no proxy:', error);
      res.status(500).json({ error: 'Erro interno do servidor' });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}