"""
Testes automatizados para todos os endpoints da API

Execute com: pytest tests/test_api.py -v
"""

import pytest
import requests
import json
from datetime import datetime, timedelta


# Configuração base
BASE_URL = "http://localhost:5000/api"
HEADERS = {"Content-Type": "application/json"}


class TestAPI:
    """Classe de testes para a API"""

    # Variáveis compartilhadas entre testes
    super_admin_token = None
    company_token = None
    created_company_id = None
    created_user_id = None
    created_modality_id = None
    created_entry_id = None
    test_company_id = None

    # ========== TESTES DE AUTENTICAÇÃO ==========

    def test_01_health_check(self):
        """Teste: Health check da API"""
        response = requests.get("http://localhost:5000/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✅ Health check passou")

    def test_02_login_super_admin(self):
        """Teste: Login do super admin"""
        payload = {
            "email": "admin@sistema.com",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, headers=HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user" in data
        assert data["user"]["is_super_admin"] is True

        # Salvar token para próximos testes
        TestAPI.super_admin_token = data["token"]
        print(f"✅ Login super admin passou - Token obtido")

    def test_03_get_me_super_admin(self):
        """Teste: Buscar dados do usuário logado (super admin)"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "admin@sistema.com"
        assert data["is_super_admin"] is True
        print("✅ GET /auth/me passou")

    def test_04_login_invalid_credentials(self):
        """Teste: Login com credenciais inválidas"""
        payload = {
            "email": "admin@sistema.com",
            "password": "senha_errada"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, headers=HEADERS)
        assert response.status_code == 401
        print("✅ Login com credenciais inválidas retornou 401")

    # ========== TESTES DE EMPRESAS (ADMIN) ==========

    def test_05_list_companies(self):
        """Teste: Listar empresas (deve excluir empresa administrativa)"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}
        response = requests.get(f"{BASE_URL}/admin/companies", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Verificar que empresa administrativa NÃO aparece
        for company in data:
            assert company.get("is_admin_company") is not True

        # Salvar ID de uma empresa para testes posteriores
        if len(data) > 0:
            TestAPI.test_company_id = data[0]["id"]

        print(f"✅ Listagem de empresas passou - {len(data)} empresas encontradas (excluindo administrativa)")

    def test_06_create_company(self):
        """Teste: Criar nova empresa"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}

        # Usa timestamp para garantir CNPJ único
        import time
        timestamp = str(int(time.time()))[-8:]  # Últimos 8 dígitos do timestamp
        unique_cnpj = f"99.{timestamp[:3]}.{timestamp[3:6]}/0001-{timestamp[6:8]}"

        payload = {
            "name": f"Empresa de Teste Auto {timestamp}",
            "cnpj": unique_cnpj,
            "phone": "(99) 99999-9999",
            "plan": "basic"
        }
        response = requests.post(f"{BASE_URL}/admin/companies", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["cnpj"] == payload["cnpj"]
        assert "id" in data

        # Salvar ID para próximos testes
        TestAPI.created_company_id = data["id"]
        print(f"✅ Criação de empresa passou - ID: {data['id']}")

    def test_07_get_company_by_id(self):
        """Teste: Buscar empresa por ID"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}
        response = requests.get(
            f"{BASE_URL}/admin/companies/{TestAPI.created_company_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == TestAPI.created_company_id
        print("✅ Busca de empresa por ID passou")

    def test_08_update_company(self):
        """Teste: Atualizar empresa"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}
        payload = {
            "name": "Empresa de Teste Automatizado - ATUALIZADA",
            "cnpj": "99.999.999/0001-99",
            "phone": "(88) 88888-8888",
            "plan": "premium"
        }
        response = requests.put(
            f"{BASE_URL}/admin/companies/{TestAPI.created_company_id}",
            json=payload,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["plan"] == "premium"
        print("✅ Atualização de empresa passou")

    # ========== TESTES DE USUÁRIOS (ADMIN) ==========

    def test_09_create_user(self):
        """Teste: Criar usuário para a empresa"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}
        payload = {
            "email": "usuario.teste@empresa.com",
            "password": "senha123",
            "name": "Usuário de Teste",
            "company_id": TestAPI.created_company_id,
            "role_ids": []
        }
        response = requests.post(f"{BASE_URL}/admin/users", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["company_id"] == TestAPI.created_company_id

        # Salvar ID para próximos testes
        TestAPI.created_user_id = data["id"]
        print(f"✅ Criação de usuário passou - ID: {data['id']}")

    def test_10_list_users_by_company(self):
        """Teste: Listar usuários de uma empresa"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}
        response = requests.get(
            f"{BASE_URL}/admin/users/company/{TestAPI.created_company_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        print(f"✅ Listagem de usuários por empresa passou - {len(data)} usuários encontrados")

    def test_11_deactivate_user(self):
        """Teste: Desativar usuário"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}
        response = requests.patch(
            f"{BASE_URL}/admin/users/{TestAPI.created_user_id}/deactivate",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False
        print("✅ Desativação de usuário passou")

    def test_12_activate_user(self):
        """Teste: Ativar usuário"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}
        response = requests.patch(
            f"{BASE_URL}/admin/users/{TestAPI.created_user_id}/activate",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is True
        print("✅ Ativação de usuário passou")

    # ========== TESTES DE IMPERSONATE ==========

    def test_13_impersonate_company(self):
        """Teste: Impersonate de empresa"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}

        # Usar empresa de teste existente
        if not TestAPI.test_company_id:
            pytest.skip("Nenhuma empresa de teste disponível")

        response = requests.post(
            f"{BASE_URL}/admin/impersonate/{TestAPI.test_company_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data

        # Salvar token da empresa
        TestAPI.company_token = data["token"]
        print("✅ Impersonate passou - Token de 1h obtido")

    # ========== TESTES DE MODALIDADES DE PAGAMENTO ==========

    def test_14_create_payment_modality(self):
        """Teste: Criar modalidade de pagamento"""
        if not TestAPI.company_token:
            pytest.skip("Token de empresa não disponível")

        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.company_token}"}
        payload = {
            "name": "PIX Teste",
            "color": "#00FF00"
        }
        response = requests.post(
            f"{BASE_URL}/payment-modalities",
            json=payload,
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["color"] == payload["color"]

        # Salvar ID para próximos testes
        TestAPI.created_modality_id = data["id"]
        print(f"✅ Criação de modalidade passou - ID: {data['id']}")

    def test_15_list_payment_modalities(self):
        """Teste: Listar modalidades de pagamento"""
        if not TestAPI.company_token:
            pytest.skip("Token de empresa não disponível")

        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.company_token}"}
        response = requests.get(f"{BASE_URL}/payment-modalities", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Listagem de modalidades passou - {len(data)} modalidades encontradas")

    def test_16_update_payment_modality(self):
        """Teste: Atualizar modalidade de pagamento"""
        if not TestAPI.company_token or not TestAPI.created_modality_id:
            pytest.skip("Token de empresa ou modalidade não disponível")

        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.company_token}"}
        payload = {
            "name": "PIX Teste Atualizado",
            "color": "#FF0000"
        }
        response = requests.put(
            f"{BASE_URL}/payment-modalities/{TestAPI.created_modality_id}",
            json=payload,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == payload["name"]
        print("✅ Atualização de modalidade passou")

    # ========== TESTES DE LANÇAMENTOS FINANCEIROS ==========

    def test_17_create_financial_entry(self):
        """Teste: Criar lançamento financeiro"""
        if not TestAPI.company_token or not TestAPI.created_modality_id:
            pytest.skip("Token de empresa ou modalidade não disponível")

        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.company_token}"}
        payload = {
            "value": 1500.50,
            "date": datetime.now().isoformat(),
            "modality_id": TestAPI.created_modality_id
        }
        response = requests.post(
            f"{BASE_URL}/financial-entries",
            json=payload,
            headers=headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["value"] == payload["value"]
        assert data["modality_id"] == TestAPI.created_modality_id

        # Salvar ID para próximos testes
        TestAPI.created_entry_id = data["id"]
        print(f"✅ Criação de lançamento passou - ID: {data['id']}")

    def test_18_list_financial_entries(self):
        """Teste: Listar lançamentos financeiros"""
        if not TestAPI.company_token:
            pytest.skip("Token de empresa não disponível")

        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.company_token}"}
        response = requests.get(f"{BASE_URL}/financial-entries", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Listagem de lançamentos passou - {len(data)} lançamentos encontrados")

    def test_19_get_financial_entry_by_id(self):
        """Teste: Buscar lançamento por ID"""
        if not TestAPI.company_token or not TestAPI.created_entry_id:
            pytest.skip("Token de empresa ou lançamento não disponível")

        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.company_token}"}
        response = requests.get(
            f"{BASE_URL}/financial-entries/{TestAPI.created_entry_id}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == TestAPI.created_entry_id
        print("✅ Busca de lançamento por ID passou")

    def test_20_update_financial_entry(self):
        """Teste: Atualizar lançamento financeiro"""
        if not TestAPI.company_token or not TestAPI.created_entry_id:
            pytest.skip("Token de empresa ou lançamento não disponível")

        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.company_token}"}
        payload = {
            "value": 2500.75,
            "date": datetime.now().isoformat(),
            "modality_id": TestAPI.created_modality_id
        }
        response = requests.put(
            f"{BASE_URL}/financial-entries/{TestAPI.created_entry_id}",
            json=payload,
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["value"] == payload["value"]
        print("✅ Atualização de lançamento passou")

    def test_21_filter_entries_by_date(self):
        """Teste: Filtrar lançamentos por data"""
        if not TestAPI.company_token:
            pytest.skip("Token de empresa não disponível")

        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.company_token}"}
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now().strftime("%Y-%m-%d")

        response = requests.get(
            f"{BASE_URL}/financial-entries?start_date={start_date}&end_date={end_date}",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✅ Filtro de lançamentos por data passou - {len(data)} encontrados")

    # ========== TESTES DE LOGS DE AUDITORIA ==========

    def test_22_list_audit_logs(self):
        """Teste: Listar logs de auditoria"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}
        response = requests.get(f"{BASE_URL}/admin/audit-logs", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "logs" in data
        assert "total" in data
        assert isinstance(data["logs"], list)
        print(f"✅ Listagem de audit logs passou - {data['total']} logs encontrados")

    def test_23_filter_audit_logs_by_action(self):
        """Teste: Filtrar logs por ação"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}
        response = requests.get(
            f"{BASE_URL}/admin/audit-logs?action=create_company",
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "logs" in data
        assert isinstance(data["logs"], list)
        print(f"✅ Filtro de audit logs por ação passou - {data['total']} encontrados")

    # ========== TESTES DE LIMPEZA ==========

    def test_24_delete_financial_entry(self):
        """Teste: Deletar lançamento financeiro"""
        if not TestAPI.company_token or not TestAPI.created_entry_id:
            pytest.skip("Token de empresa ou lançamento não disponível")

        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.company_token}"}
        response = requests.delete(
            f"{BASE_URL}/financial-entries/{TestAPI.created_entry_id}",
            headers=headers
        )
        assert response.status_code == 200
        print("✅ Deleção de lançamento passou")

    def test_25_delete_payment_modality(self):
        """Teste: Deletar modalidade de pagamento"""
        if not TestAPI.company_token or not TestAPI.created_modality_id:
            pytest.skip("Token de empresa ou modalidade não disponível")

        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.company_token}"}
        response = requests.delete(
            f"{BASE_URL}/payment-modalities/{TestAPI.created_modality_id}",
            headers=headers
        )
        assert response.status_code == 200
        print("✅ Deleção de modalidade passou")

    def test_26_delete_user(self):
        """Teste: Deletar usuário"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}
        response = requests.delete(
            f"{BASE_URL}/admin/users/{TestAPI.created_user_id}",
            headers=headers
        )
        assert response.status_code == 200
        print("✅ Deleção de usuário passou")

    def test_27_delete_company(self):
        """Teste: Deletar empresa"""
        headers = {**HEADERS, "Authorization": f"Bearer {TestAPI.super_admin_token}"}
        response = requests.delete(
            f"{BASE_URL}/admin/companies/{TestAPI.created_company_id}",
            headers=headers
        )
        assert response.status_code == 200
        print("✅ Deleção de empresa passou")

    # ========== TESTES DE AUTORIZAÇÃO ==========

    def test_28_unauthorized_access(self):
        """Teste: Acesso sem token deve retornar 401"""
        response = requests.get(f"{BASE_URL}/admin/companies", headers=HEADERS)
        assert response.status_code == 401
        print("✅ Acesso sem token retornou 401")

    def test_29_invalid_token(self):
        """Teste: Token inválido deve retornar 401"""
        headers = {**HEADERS, "Authorization": "Bearer token_invalido"}
        response = requests.get(f"{BASE_URL}/admin/companies", headers=headers)
        assert response.status_code == 401
        print("✅ Token inválido retornou 401")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
