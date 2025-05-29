"""
Sistema de Notificações Avançado
EvolutionAPI WhatsApp + Email SMTP
Conforme especificação do manual da BGTELECOM
Desenvolvido por: Tiago Pereira Ramos
Data: 29/05/2025
"""

import logging
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..config.settings import configuracoes

logger = logging.getLogger(__name__)

class NotificacaoService:
    """
    Sistema completo de notificações
    WhatsApp via EvolutionAPI + Email SMTP
    """
    
    def __init__(self):
        self.configuracoes = configuracoes
        logger.info("Sistema de notificações inicializado")
    
    async def enviar_notificacao_aprovacao_pendente(
        self,
        processo_id: str,
        cliente_nome: str,
        operadora_nome: str,
        valor_fatura: Optional[float] = None,
        destinatarios: List[str] = None
    ):
        """Notifica sobre fatura pendente de aprovação"""
        try:
            titulo = "Nova Fatura Pendente de Aprovação"
            
            # Mensagem WhatsApp
            whatsapp_msg = f"""
🔔 *NOVA FATURA PARA APROVAÇÃO*

📋 Processo: {processo_id}
🏢 Cliente: {cliente_nome}
📡 Operadora: {operadora_nome}
💰 Valor: R$ {valor_fatura:.2f if valor_fatura else 'N/I'}

⏰ Aguardando aprovação no sistema RPA
🔗 Acesse o sistema para aprovar/rejeitar

*Sistema Orquestrador RPA - BGTELECOM*
            """
            
            # Email HTML
            email_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <div style="background-color: #f8f9fa; padding: 20px;">
                        <h2 style="color: #dc3545;">🔔 Nova Fatura Pendente de Aprovação</h2>
                        
                        <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3>Detalhes da Fatura:</h3>
                            <ul>
                                <li><strong>Processo:</strong> {processo_id}</li>
                                <li><strong>Cliente:</strong> {cliente_nome}</li>
                                <li><strong>Operadora:</strong> {operadora_nome}</li>
                                <li><strong>Valor:</strong> R$ {valor_fatura:.2f if valor_fatura else 'Não informado'}</li>
                                <li><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</li>
                            </ul>
                        </div>
                        
                        <p style="color: #6c757d;">
                            Acesse o sistema RPA para aprovar ou rejeitar esta fatura.
                        </p>
                        
                        <hr>
                        <small style="color: #6c757d;">Sistema Orquestrador RPA - BGTELECOM</small>
                    </div>
                </body>
            </html>
            """
            
            # Enviar notificações
            await self._enviar_whatsapp(whatsapp_msg, destinatarios)
            await self._enviar_email(titulo, email_html, destinatarios)
            
            logger.info(f"Notificação de aprovação pendente enviada para processo {processo_id}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de aprovação pendente: {e}")
    
    async def enviar_notificacao_fatura_aprovada(
        self,
        processo_id: str,
        cliente_nome: str,
        aprovador_nome: str,
        destinatarios: List[str] = None
    ):
        """Notifica sobre fatura aprovada"""
        try:
            titulo = "Fatura Aprovada com Sucesso"
            
            whatsapp_msg = f"""
✅ *FATURA APROVADA*

📋 Processo: {processo_id}
🏢 Cliente: {cliente_nome}
👤 Aprovador: {aprovador_nome}
🕐 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

✅ A fatura foi aprovada e será enviada para o SAT automaticamente.

*Sistema Orquestrador RPA - BGTELECOM*
            """
            
            email_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <div style="background-color: #f8f9fa; padding: 20px;">
                        <h2 style="color: #28a745;">✅ Fatura Aprovada com Sucesso</h2>
                        
                        <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3>Detalhes da Aprovação:</h3>
                            <ul>
                                <li><strong>Processo:</strong> {processo_id}</li>
                                <li><strong>Cliente:</strong> {cliente_nome}</li>
                                <li><strong>Aprovador:</strong> {aprovador_nome}</li>
                                <li><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</li>
                            </ul>
                        </div>
                        
                        <p style="color: #28a745;">
                            A fatura foi aprovada e será enviada para o SAT automaticamente.
                        </p>
                        
                        <hr>
                        <small style="color: #6c757d;">Sistema Orquestrador RPA - BGTELECOM</small>
                    </div>
                </body>
            </html>
            """
            
            await self._enviar_whatsapp(whatsapp_msg, destinatarios)
            await self._enviar_email(titulo, email_html, destinatarios)
            
            logger.info(f"Notificação de aprovação enviada para processo {processo_id}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de aprovação: {e}")
    
    async def enviar_notificacao_fatura_rejeitada(
        self,
        processo_id: str,
        cliente_nome: str,
        aprovador_nome: str,
        motivo: str,
        destinatarios: List[str] = None
    ):
        """Notifica sobre fatura rejeitada"""
        try:
            titulo = "Fatura Rejeitada"
            
            whatsapp_msg = f"""
❌ *FATURA REJEITADA*

📋 Processo: {processo_id}
🏢 Cliente: {cliente_nome}
👤 Rejeitador: {aprovador_nome}
📝 Motivo: {motivo}
🕐 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

❌ A fatura foi rejeitada e precisará ser revista.

*Sistema Orquestrador RPA - BGTELECOM*
            """
            
            email_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <div style="background-color: #f8f9fa; padding: 20px;">
                        <h2 style="color: #dc3545;">❌ Fatura Rejeitada</h2>
                        
                        <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3>Detalhes da Rejeição:</h3>
                            <ul>
                                <li><strong>Processo:</strong> {processo_id}</li>
                                <li><strong>Cliente:</strong> {cliente_nome}</li>
                                <li><strong>Rejeitador:</strong> {aprovador_nome}</li>
                                <li><strong>Motivo:</strong> {motivo}</li>
                                <li><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</li>
                            </ul>
                        </div>
                        
                        <p style="color: #dc3545;">
                            A fatura foi rejeitada e precisará ser revista.
                        </p>
                        
                        <hr>
                        <small style="color: #6c757d;">Sistema Orquestrador RPA - BGTELECOM</small>
                    </div>
                </body>
            </html>
            """
            
            await self._enviar_whatsapp(whatsapp_msg, destinatarios)
            await self._enviar_email(titulo, email_html, destinatarios)
            
            logger.info(f"Notificação de rejeição enviada para processo {processo_id}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de rejeição: {e}")
    
    async def enviar_notificacao_erro_rpa(
        self,
        operadora: str,
        cliente_nome: str,
        erro_msg: str,
        destinatarios: List[str] = None
    ):
        """Notifica sobre erro na execução RPA"""
        try:
            titulo = f"Erro RPA - {operadora}"
            
            whatsapp_msg = f"""
🚨 *ERRO NA EXECUÇÃO RPA*

📡 Operadora: {operadora}
🏢 Cliente: {cliente_nome}
❌ Erro: {erro_msg}
🕐 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}

🔧 Verificação manual necessária.

*Sistema Orquestrador RPA - BGTELECOM*
            """
            
            email_html = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <div style="background-color: #f8f9fa; padding: 20px;">
                        <h2 style="color: #dc3545;">🚨 Erro na Execução RPA</h2>
                        
                        <div style="background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3>Detalhes do Erro:</h3>
                            <ul>
                                <li><strong>Operadora:</strong> {operadora}</li>
                                <li><strong>Cliente:</strong> {cliente_nome}</li>
                                <li><strong>Erro:</strong> {erro_msg}</li>
                                <li><strong>Data:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</li>
                            </ul>
                        </div>
                        
                        <p style="color: #dc3545;">
                            Verificação manual necessária. Acesse o sistema para mais detalhes.
                        </p>
                        
                        <hr>
                        <small style="color: #6c757d;">Sistema Orquestrador RPA - BGTELECOM</small>
                    </div>
                </body>
            </html>
            """
            
            await self._enviar_whatsapp(whatsapp_msg, destinatarios)
            await self._enviar_email(titulo, email_html, destinatarios)
            
            logger.info(f"Notificação de erro RPA enviada para {operadora}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação de erro RPA: {e}")
    
    async def _enviar_whatsapp(self, mensagem: str, destinatarios: List[str] = None):
        """Envia mensagem via EvolutionAPI WhatsApp"""
        try:
            if not self.configuracoes.EVOLUTION_API_URL or not self.configuracoes.EVOLUTION_API_KEY:
                logger.warning("EvolutionAPI não configurado. Mensagem WhatsApp não enviada.")
                return
            
            if not destinatarios:
                destinatarios = ["5511999999999"]  # Número padrão para teste
            
            headers = {
                "Content-Type": "application/json",
                "apikey": self.configuracoes.EVOLUTION_API_KEY
            }
            
            for destinatario in destinatarios:
                # Remove caracteres especiais do número
                numero_limpo = ''.join(filter(str.isdigit, destinatario))
                
                payload = {
                    "number": numero_limpo,
                    "text": mensagem
                }
                
                response = requests.post(
                    f"{self.configuracoes.EVOLUTION_API_URL}/message/sendText",
                    json=payload,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    logger.info(f"WhatsApp enviado para {numero_limpo}")
                else:
                    logger.error(f"Erro ao enviar WhatsApp para {numero_limpo}: {response.text}")
                    
        except Exception as e:
            logger.error(f"Erro no envio WhatsApp: {e}")
    
    async def _enviar_email(self, assunto: str, corpo_html: str, destinatarios: List[str] = None):
        """Envia email via SMTP"""
        try:
            if not self.configuracoes.SMTP_USERNAME or not self.configuracoes.SMTP_PASSWORD:
                logger.warning("SMTP não configurado. Email não enviado.")
                return
            
            if not destinatarios:
                destinatarios = ["admin@bgtelecom.com.br"]  # Email padrão para teste
            
            # Configurar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From'] = self.configuracoes.SMTP_USERNAME
            msg['To'] = ", ".join(destinatarios)
            
            # Anexar HTML
            parte_html = MIMEText(corpo_html, 'html', 'utf-8')
            msg.attach(parte_html)
            
            # Enviar email
            with smtplib.SMTP(self.configuracoes.SMTP_SERVER, self.configuracoes.SMTP_PORT) as server:
                server.starttls()
                server.login(self.configuracoes.SMTP_USERNAME, self.configuracoes.SMTP_PASSWORD)
                
                for destinatario in destinatarios:
                    server.send_message(msg, to_addrs=[destinatario])
                    logger.info(f"Email enviado para {destinatario}")
                    
        except Exception as e:
            logger.error(f"Erro no envio de email: {e}")
    
    def obter_destinatarios_aprovadores(self, db_session) -> List[str]:
        """Obtém lista de emails/telefones dos aprovadores"""
        try:
            from ..main import Usuario
            
            aprovadores = db_session.query(Usuario).filter(
                Usuario.perfil_usuario.in_(["ADMINISTRADOR", "APROVADOR"]),
                Usuario.status_ativo == True
            ).all()
            
            emails = [u.email for u in aprovadores if u.email]
            telefones = [u.telefone for u in aprovadores if u.telefone]
            
            return {
                "emails": emails,
                "telefones": telefones
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter destinatários aprovadores: {e}")
            return {"emails": [], "telefones": []}

# Instância global do serviço
notificacao_service = NotificacaoService()