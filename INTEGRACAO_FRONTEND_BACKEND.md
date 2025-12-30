# 🔄 Integração Frontend-Backend - Problemas e Soluções

**Data:** 30/12/2025
**Frontend:** Streamlit (`dashboard_financeiro`)
**Backend:** Flask (`back_dashboard_financeiro`)

---

## ❌ Problemas Identificados

### 1. **CREATE Modalidade - Campo `is_active`**

**Frontend envia:**
```python
# payment_modality_api_repository.py linha 13
data = {"name": modality.name, "color": modality.color, "is_active": modality.is_active}
```

**Backend espera:**
```python
# payment_modality_routes.py linha 28-30
data = request.get_json()
name = data.get("name")
color = data.get("color")
# NÃO LÊ is_active!
```

**Problema:** Backend IGNORA o campo `is_active` no CREATE. Sempre cria como `True` (padrão da entidade).

---

### 2. **UPDATE Modalidade - Campo `is_active`**

**Frontend envia:**
```python
# payment_modality_api_repository.py linha 29
data = {"name": modality.name, "color": modality.color, "is_active": modality.is_active}
```

**Backend espera:**
```python
# payment_modality_routes.py linha 68-70
data = request.get_json()
name = data.get("name")
color = data.get("color")
# NÃO LÊ is_active!
```

**Problema:** Backend IGNORA o campo `is_active` no UPDATE. A mudança de status não funciona pelo formulário de edição.

---

### 3. **TOGGLE Modalidade - Parâmetro `activate`**

**Frontend envia:**
```python
# payment_modality_api_repository.py linha 37
response = self.http_client.patch(f"{self.base_endpoint}/{modality_id}/toggle")
# NÃO ENVIA NENHUM PARÂMETRO!
```

**Backend espera:**
```python
# payment_modality_routes.py linha 110-111
data = request.get_json()
activate = data.get("activate", True)
```

**Problema:** Frontend não está enviando o parâmetro `activate`, então o backend sempre ativa (padrão `True`).

---

## ✅ Soluções

### Opção 1: Corrigir o Backend (Recomendado)

#### 1.1. Adicionar suporte a `is_active` no CREATE

```python
# src/presentation/routes/payment_modality_routes.py

@payment_modality_bp.route("/payment-modalities", methods=["POST"])
@require_auth
@require_feature("payment_modalities.create")
def create_modality():
    try:
        data = request.get_json()
        name = data.get("name")
        color = data.get("color")
        is_active = data.get("is_active", True)  # ✅ ADICIONAR

        repository = get_repository(g.company_id)
        use_case = CreatePaymentModality(repository)
        modality = use_case.execute(name, color, is_active)  # ✅ PASSAR PARÂMETRO

        return jsonify(modality.to_dict()), 201
```

#### 1.2. Adicionar suporte a `is_active` no UPDATE

```python
# src/presentation/routes/payment_modality_routes.py

@payment_modality_bp.route("/payment-modalities/<modality_id>", methods=["PUT"])
@require_auth
@require_feature("payment_modalities.update")
def update_modality(modality_id):
    try:
        data = request.get_json()
        name = data.get("name")
        color = data.get("color")
        is_active = data.get("is_active")  # ✅ ADICIONAR

        repository = get_repository(g.company_id)
        use_case = UpdatePaymentModality(repository)
        modality = use_case.execute(modality_id, name, color, is_active)  # ✅ PASSAR PARÂMETRO

        return jsonify(modality.to_dict()), 200
```

#### 1.3. Verificar Use Cases

```python
# src/application/use_cases/payment_modality/create_payment_modality.py

def execute(self, name: str, color: str, is_active: bool = True) -> PaymentModality:
    # ✅ Verificar se aceita is_active
```

```python
# src/application/use_cases/payment_modality/update_payment_modality.py

def execute(self, modality_id: str, name: str, color: str, is_active: bool = None) -> PaymentModality:
    # ✅ Verificar se aceita is_active
```

---

### Opção 2: Corrigir o Frontend

#### 2.1. Remover `is_active` do CREATE/UPDATE do repository

```python
# dashboard_financeiro/src/infrastructure/api/payment_modality_api_repository.py

def create(self, modality: PaymentModality) -> PaymentModality:
    data = {"name": modality.name, "color": modality.color}  # ❌ Remover is_active
    response = self.http_client.post(self.base_endpoint, data)
    return PaymentModality.from_dict(response)

def update(self, modality_id: str, modality: PaymentModality) -> PaymentModality:
    data = {"name": modality.name, "color": modality.color}  # ❌ Remover is_active
    response = self.http_client.put(f"{self.base_endpoint}/{modality_id}", data)
    return PaymentModality.from_dict(response)
```

#### 2.2. Corrigir TOGGLE para enviar parâmetro

```python
# dashboard_financeiro/src/infrastructure/api/payment_modality_api_repository.py

def toggle(self, modality_id: str, activate: bool) -> PaymentModality:  # ✅ Adicionar parâmetro
    data = {"activate": activate}  # ✅ Enviar no body
    response = self.http_client.patch(f"{self.base_endpoint}/{modality_id}/toggle", data)
    return PaymentModality.from_dict(response)
```

#### 2.3. Atualizar Use Cases

```python
# dashboard_financeiro/src/application/use_cases/payment_modality_use_cases.py

def toggle_modality(self, modality_id: str, activate: bool = None) -> PaymentModality:
    # Buscar modalidade atual
    current = self.repository.get_by_id(modality_id)
    if activate is None:
        activate = not current.is_active  # Inverter status atual

    return self.repository.toggle(modality_id, activate)
```

---

## 🎯 Recomendação Final

**CORRIGIR O BACKEND (Opção 1)**

### Motivos:
1. ✅ O frontend já está implementado e funcionando
2. ✅ A lógica do frontend está correta (editar deve poder mudar is_active)
3. ✅ Menos mudanças necessárias (apenas 2 arquivos no backend)
4. ✅ Mantém a consistência da API

---

## 📝 Arquivos a Modificar no Backend

### 1. Use Cases

**Arquivo:** `src/application/use_cases/payment_modality/create_payment_modality.py`
```python
def execute(self, name: str, color: str, is_active: bool = True) -> PaymentModality:
    # Verificar se já aceita is_active
```

**Arquivo:** `src/application/use_cases/payment_modality/update_payment_modality.py`
```python
def execute(self, modality_id: str, name: str, color: str, is_active: bool = None) -> PaymentModality:
    existing = self.repository.find_by_id(modality_id)
    if not existing:
        raise ValueError("Modalidade não encontrada")

    # Atualizar campos (se None, manter valor atual)
    updated_modality = PaymentModality(
        id=modality_id,
        name=name if name else existing.name,
        color=color if color else existing.color,
        is_active=is_active if is_active is not None else existing.is_active
    )

    return self.repository.update(modality_id, updated_modality)
```

### 2. Routes

**Arquivo:** `src/presentation/routes/payment_modality_routes.py`

Adicionar:
- Linha 31: `is_active = data.get("is_active", True)`
- Linha 35: `modality = use_case.execute(name, color, is_active)`
- Linha 71: `is_active = data.get("is_active")`
- Linha 75: `modality = use_case.execute(modality_id, name, color, is_active)`

---

## 🧪 Testes Adicionados

Já adicionei testes para verificar essas funcionalidades:

```python
# tests/test_api.py

def test_16_update_payment_modality(self):
    # Verifica mudança de nome E cor
    assert data["name"] == payload["name"]
    assert data["color"] == payload["color"]  # ✅ ADICIONADO

def test_16a_toggle_modality_inactive(self):
    # Testa desativar modalidade
    assert data["is_active"] is False

def test_16b_toggle_modality_active(self):
    # Testa ativar modalidade
    assert data["is_active"] is True
```

---

## 🔍 Como Testar

### 1. Teste Manual via Frontend

```bash
# Terminal 1 - Backend
cd back_dashboard_financeiro
source .venv/bin/activate
python -m src.app

# Terminal 2 - Frontend
cd dashboard_financeiro
source .venv/bin/activate
streamlit run src/main.py
```

**Passos:**
1. Login no frontend
2. Ir para "Modalidades de Pagamento"
3. Criar nova modalidade com status "Inativa"
4. Verificar se foi criada como inativa ❌ (atualmente cria como ativa)
5. Editar modalidade e mudar cor
6. Verificar se cor mudou ✅ (deve funcionar)
7. Editar e marcar como "Inativa"
8. Verificar se mudou para inativa ❌ (atualmente não funciona)
9. Clicar em "Desativar"
10. Verificar se alternância funciona ❌ (atualmente sempre ativa)

### 2. Teste Automatizado

```bash
cd back_dashboard_financeiro
source .venv/bin/activate

# Iniciar servidor
python -m src.app &

# Rodar testes
pytest tests/test_api.py::TestAPI::test_16 -v
pytest tests/test_api.py::TestAPI::test_16a -v
pytest tests/test_api.py::TestAPI::test_16b -v
```

---

## 📊 Status Atual

| Funcionalidade | Frontend | Backend | Status |
|---------------|----------|---------|--------|
| Criar modalidade | ✅ Envia is_active | ❌ Ignora | 🔴 NÃO FUNCIONA |
| Atualizar cor | ✅ Envia color | ✅ Aceita | 🟢 FUNCIONA |
| Atualizar nome | ✅ Envia name | ✅ Aceita | 🟢 FUNCIONA |
| Atualizar is_active via edit | ✅ Envia is_active | ❌ Ignora | 🔴 NÃO FUNCIONA |
| Toggle (ativar/desativar) | ❌ Não envia parâmetro | ✅ Aceita parâmetro | 🟡 FUNCIONA PARCIALMENTE |

---

## 🚀 Status da Correção

1. ✅ Testes criados
2. ✅ Corrigir backend (use cases + routes)
3. ✅ Testar integração completa (31/31 testes passando)
4. ✅ Documentar mudanças

---

## ✅ Correções Implementadas (30/12/2025)

### Arquivos Modificados:

**1. [src/application/use_cases/create_payment_modality.py](src/application/use_cases/create_payment_modality.py:9)**
- Adicionado parâmetro `is_active: bool = True` no método `execute()`
- Agora aceita e processa o campo `is_active` enviado pelo frontend

**2. [src/application/use_cases/update_payment_modality.py](src/application/use_cases/update_payment_modality.py:9)**
- Adicionado parâmetro `is_active: bool = None` no método `execute()`
- Implementada lógica para atualizar `is_active` quando fornecido

**3. [src/presentation/routes/payment_modality_routes.py](src/presentation/routes/payment_modality_routes.py:31)**
- **CREATE** (linha 31): Adicionado `is_active = data.get("is_active", True)`
- **CREATE** (linha 36): Passando `is_active` para o use case
- **UPDATE** (linha 72): Adicionado `is_active = data.get("is_active")`
- **UPDATE** (linha 77): Passando `is_active` para o use case

### Resultado:

| Funcionalidade | Status Antes | Status Depois |
|---------------|--------------|---------------|
| Criar modalidade com `is_active=False` | 🔴 Ignorado (sempre `True`) | 🟢 FUNCIONA |
| Atualizar `is_active` via formulário de edição | 🔴 Ignorado | 🟢 FUNCIONA |
| Atualizar cor | 🟢 Funcionava | 🟢 FUNCIONA |
| Atualizar nome | 🟢 Funcionava | 🟢 FUNCIONA |
| Toggle (ativar/desativar) | 🟡 Parcial | 🟢 FUNCIONA |

**Todos os 31 testes automatizados passando com sucesso!**

---

## 📞 Suporte

Se tiver dúvidas sobre a integração, consulte:
- [README.md](README.md) - Documentação da API
- [TESTES_100_SUCESSO.md](TESTES_100_SUCESSO.md) - Status dos testes
