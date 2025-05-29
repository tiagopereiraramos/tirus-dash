"""
Serviço de inicialização do sistema
Carrega dados reais da BGTELECOM do CSV
"""

import csv
import hashlib
from sqlalchemy.orm import Session
from config.database import SessionLocal
from models.operadora import Operadora
from models.cliente import Cliente


class InicializacaoService:
    """Serviço para inicializar dados do sistema"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def generate_hash_cad(self, nome_filtro: str, operadora: str, servico: str, 
                         dados_sat: str = "", filtro: str = "", unidade: str = "") -> str:
        """Gera hash único para identificação do cliente/processo"""
        combined = f"{nome_filtro}_{operadora}_{servico}_{dados_sat}_{filtro}_{unidade}"
        return hashlib.md5(combined.encode()).hexdigest()[:12]
    
    async def inicializar_dados_sistema(self):
        """Inicializa dados do sistema com base no CSV da BGTELECOM"""
        try:
            # Verificar se já existe dados
            if self.db.query(Operadora).count() > 0:
                print("✅ Dados do sistema já inicializados")
                return
            
            print("🔄 Inicializando dados do sistema...")
            
            # Criar operadoras
            operadoras_data = [
                {"nome": "EMBRATEL", "codigo": "EMBRATEL", "possui_rpa": True},
                {"nome": "DIGITALNET", "codigo": "DIGITALNET", "possui_rpa": True},
                {"nome": "AZUTON", "codigo": "AZUTON", "possui_rpa": True},
                {"nome": "OI", "codigo": "OI", "possui_rpa": True},
                {"nome": "VIVO", "codigo": "VIVO", "possui_rpa": True},
                {"nome": "SAT", "codigo": "SAT", "possui_rpa": True}
            ]
            
            operadoras = {}
            for op_data in operadoras_data:
                operadora = Operadora(**op_data)
                self.db.add(operadora)
                self.db.flush()
                operadoras[op_data["codigo"]] = operadora
                print(f"✅ Operadora criada: {op_data['nome']}")
            
            # Carregar dados reais do CSV da BGTELECOM
            clientes_data = self._carregar_dados_csv_bgtelecom()
            
            for cliente_data in clientes_data:
                try:
                    # Encontrar operadora
                    operadora = operadoras.get(cliente_data["operadora"])
                    if not operadora:
                        print(f"⚠️ Operadora não encontrada: {cliente_data['operadora']}")
                        continue
                    
                    # Gerar hash único
                    hash_unico = self.generate_hash_cad(
                        cliente_data["nome_filtro"],
                        cliente_data["operadora"],
                        cliente_data["servico"],
                        cliente_data.get("dados_sat", ""),
                        cliente_data.get("filtro", ""),
                        cliente_data["unidade"]
                    )
                    
                    # Criar cliente
                    cliente = Cliente(
                        hash_unico=hash_unico,
                        razao_social=cliente_data["razao_social"],
                        nome_sat=cliente_data["nome_sat"],
                        cnpj=cliente_data["cnpj"],
                        operadora_id=operadora.id,
                        filtro=cliente_data.get("filtro"),
                        servico=cliente_data["servico"],
                        dados_sat=cliente_data.get("dados_sat"),
                        unidade=cliente_data["unidade"],
                        site_emissao=cliente_data.get("site_emissao"),
                        login_portal=cliente_data.get("login_portal"),
                        senha_portal=cliente_data.get("senha_portal"),
                        cpf=cliente_data.get("cpf")
                    )
                    
                    self.db.add(cliente)
                    print(f"✅ Cliente criado: {cliente_data['razao_social']}")
                    
                except Exception as e:
                    print(f"❌ Erro ao criar cliente {cliente_data.get('razao_social', 'N/A')}: {e}")
                    continue
            
            self.db.commit()
            print("✅ Dados do sistema inicializados com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar dados do sistema: {e}")
            self.db.rollback()
        finally:
            self.db.close()
    
    def _carregar_dados_csv_bgtelecom(self) -> list:
        """Carrega dados reais do CSV da BGTELECOM"""
        clientes = []
        
        try:
            with open("attached_assets/DADOS SAT - BGTELECOM - BGTELECOM .csv", "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    cliente_data = {
                        "nome_filtro": row.get("NOME FILTRO", "").strip(),
                        "operadora": row.get("OPERADORA", "").strip(),
                        "servico": row.get("SERVIÇO", "").strip(),
                        "dados_sat": row.get("DADOS SAT", "").strip(),
                        "filtro": row.get("FILTRO", "").strip(),
                        "unidade": row.get("UNIDADE", "").strip(),
                        "razao_social": row.get("NOME FILTRO", "").strip(),
                        "nome_sat": row.get("DADOS SAT", "").strip(),
                        "cnpj": "00.000.000/0001-00",  # CNPJ padrão
                        "site_emissao": row.get("SITE DE EMISSÃO", "").strip(),
                        "login_portal": None,
                        "senha_portal": None,
                        "cpf": None
                    }
                    
                    # Validar dados obrigatórios
                    if cliente_data["nome_filtro"] and cliente_data["operadora"] and cliente_data["unidade"]:
                        clientes.append(cliente_data)
                
                print(f"📊 Carregados {len(clientes)} clientes do CSV da BGTELECOM")
                
        except FileNotFoundError:
            print("⚠️ Arquivo CSV não encontrado, criando dados de exemplo")
            # Dados de exemplo baseados no CSV real
            clientes = [
                {
                    "nome_filtro": "RICAL",
                    "operadora": "EMBRATEL",
                    "servico": "MPLS",
                    "dados_sat": "RICAL COMERCIO",
                    "filtro": "RICAL",
                    "unidade": "MATRIZ",
                    "razao_social": "RICAL COMERCIO LTDA",
                    "nome_sat": "RICAL COMERCIO",
                    "cnpj": "12.345.678/0001-90",
                    "site_emissao": "portal.embratel.com.br"
                },
                {
                    "nome_filtro": "ALVORADA",
                    "operadora": "DIGITALNET",
                    "servico": "INTERNET",
                    "dados_sat": "ALVORADA TRANSPORTES",
                    "filtro": "ALVORADA",
                    "unidade": "FILIAL 01",
                    "razao_social": "ALVORADA TRANSPORTES SA",
                    "nome_sat": "ALVORADA TRANSPORTES",
                    "cnpj": "23.456.789/0001-01",
                    "site_emissao": "portal.digitalnet.com.br"
                }
            ]
        
        except Exception as e:
            print(f"❌ Erro ao carregar CSV: {e}")
            clientes = []
        
        return clientes