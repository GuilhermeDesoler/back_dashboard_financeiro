# 🔐 Endpoints Administrativos - Super Admin

Endpoints exclusivos para usuários com `is_super_admin = true`.

## 🎯 Autenticação

Todos os endpoints requerem token JWT com `is_super_admin: true`.

```bash
# 1. Login como super admin
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "email": "teste@teste.com",
  "password": "123456"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "user-uuid",
    "email": "teste@teste.com",
    "name": "Usuário Teste",
    "company_id": "company-uuid",
    "roles": ["Admin"],
    "features": [...],
    "is_super_admin": true
  }
}
```

---

## 📊 Dashboard

### GET /api/admin/dashboard

Estatísticas gerais do sistema.

```bash
GET http://localhost:5000/api/admin/dashboard
Authorization: Bearer {token}
```

**Response:**
```json
{
  "companies": {
    "total": 5,
    "active": 4,
    "inactive": 1,
    "by_plan": {
      "basic": 2,
      "premium": 2,
      "enterprise": 1
    }
  },
  "users": {
    "total": 15,
    "active": 14,
    "inactive": 1,
    "super_admins": 1
  },
  "features": {
    "total": 23
  }
}
```

---

## 🏢 Empresas

### GET /api/admin/companies

Lista todas as empresas com estatísticas.

```bash
GET http://localhost:5000/api/admin/companies?only_active=true
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": "company-uuid-1",
    "name": "Empresa Teste Ltda",
    "cnpj": "11.222.333/0001-44",
    "phone": "(11) 98765-4321",
    "plan": "premium",
    "is_active": true,
    "users_count": 3,
    "created_at": "2025-12-29T10:00:00",
    "updated_at": "2025-12-29T10:00:00"
  },
  {
    "id": "company-uuid-2",
    "name": "Outra Empresa S.A.",
    "cnpj": "22.333.444/0001-55",
    "phone": "(11) 91234-5678",
    "plan": "basic",
    "is_active": true,
    "users_count": 5,
    "created_at": "2025-12-29T11:00:00",
    "updated_at": "2025-12-29T11:00:00"
  }
]
```

### POST /api/admin/companies

Cria uma nova empresa.

```bash
POST http://localhost:5000/api/admin/companies
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Nova Empresa Ltda",
  "cnpj": "33.444.555/0001-66",
  "phone": "(11) 99999-8888",
  "plan": "basic"
}
```

**Response:**
```json
{
  "message": "Empresa criada com sucesso",
  "company": {
    "id": "new-company-uuid",
    "name": "Nova Empresa Ltda",
    "cnpj": "33.444.555/0001-66",
    "phone": "(11) 99999-8888",
    "plan": "basic",
    "is_active": true,
    "created_at": "2025-12-29T12:00:00"
  }
}
```

### GET /api/admin/companies/{company_id}

Detalhes de uma empresa específica com lista de usuários.

```bash
GET http://localhost:5000/api/admin/companies/{company_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "company-uuid",
  "name": "Empresa Teste Ltda",
  "cnpj": "11.222.333/0001-44",
  "phone": "(11) 98765-4321",
  "plan": "premium",
  "is_active": true,
  "users_count": 3,
  "users": [
    {
      "id": "user-uuid-1",
      "name": "João Silva",
      "email": "joao@empresa.com",
      "is_active": true,
      "is_super_admin": false
    },
    {
      "id": "user-uuid-2",
      "name": "Maria Santos",
      "email": "maria@empresa.com",
      "is_active": true,
      "is_super_admin": false
    }
  ],
  "created_at": "2025-12-29T10:00:00",
  "updated_at": "2025-12-29T10:00:00"
}
```

---

## 🎭 Impersonate (1 hora de validade)

### POST /api/admin/impersonate/{company_id}

Gera token para acessar dados de uma empresa específica. O token tem validade de **1 hora**.

```bash
POST http://localhost:5000/api/admin/impersonate/{company_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "company": {
    "id": "company-uuid",
    "name": "Empresa Teste Ltda",
    "cnpj": "11.222.333/0001-44",
    "phone": "(11) 98765-4321",
    "plan": "premium",
    "is_active": true
  },
  "message": "Impersonando empresa: Empresa Teste Ltda",
  "expires_in_hours": 1
}
```

**Usando o token de impersonate:**

Após receber o token, use-o para acessar os dados da empresa:

```bash
# Exemplo: Listar lançamentos financeiros da empresa
GET http://localhost:5000/api/financial-entries
Authorization: Bearer {impersonate_token}
```

O token de impersonate contém:
- `company_id`: ID da empresa alvo
- `is_super_admin`: true
- `impersonating`: true (flag de impersonate)
- `original_company_id`: ID da empresa original do super admin
- Todas as features do sistema

⚠️ **Importante:** O token expira em **1 hora**. Após isso, será necessário gerar um novo token de impersonate.

---

## 👥 Usuários

### GET /api/admin/users

Lista todos os usuários do sistema.

```bash
# Todos os usuários
GET http://localhost:5000/api/admin/users
Authorization: Bearer {token}

# Filtrar por empresa
GET http://localhost:5000/api/admin/users?company_id={company_id}
Authorization: Bearer {token}

# Apenas ativos
GET http://localhost:5000/api/admin/users?only_active=true
Authorization: Bearer {token}
```

**Response:**
```json
[
  {
    "id": "user-uuid-1",
    "name": "João Silva",
    "email": "joao@empresa.com",
    "company_id": "company-uuid-1",
    "is_active": true,
    "is_super_admin": false,
    "created_at": "2025-12-29T10:00:00"
  },
  {
    "id": "user-uuid-2",
    "name": "Usuário Teste",
    "email": "teste@teste.com",
    "company_id": "company-uuid-2",
    "is_active": true,
    "is_super_admin": true,
    "created_at": "2025-12-29T09:00:00"
  }
]
```

### POST /api/admin/users

Cria um novo usuário.

```bash
POST http://localhost:5000/api/admin/users
Authorization: Bearer {token}
Content-Type: application/json

{
  "email": "novo@usuario.com",
  "password": "senha123",
  "name": "Novo Usuário",
  "company_id": "company-uuid",
  "is_super_admin": false
}
```

**Response:**
```json
{
  "message": "Usuário criado com sucesso",
  "user": {
    "id": "new-user-uuid",
    "email": "novo@usuario.com",
    "name": "Novo Usuário",
    "company_id": "company-uuid",
    "role_ids": [],
    "is_active": true,
    "is_super_admin": false,
    "created_at": "2025-12-29T12:00:00"
  }
}
```

### PATCH /api/admin/users/{user_id}/toggle-active

Ativa ou desativa um usuário.

```bash
# Ativar
PATCH http://localhost:5000/api/admin/users/{user_id}/toggle-active
Authorization: Bearer {token}
Content-Type: application/json

{
  "activate": true
}

# Desativar
PATCH http://localhost:5000/api/admin/users/{user_id}/toggle-active
Authorization: Bearer {token}
Content-Type: application/json

{
  "activate": false
}
```

**Response:**
```json
{
  "message": "Usuário ativado com sucesso"
}
```

---

## 🔒 Segurança

### Restrições de Acesso

Todos os endpoints administrativos verificam:

1. ✅ Token JWT válido
2. ✅ `is_super_admin = true` no payload
3. ✅ Token não expirado

### Código de Erro

| Código | Mensagem | Significado |
|--------|----------|-------------|
| 401 | Token não fornecido | Header Authorization ausente |
| 401 | Token inválido | Token mal formado ou expirado |
| 403 | Acesso negado | Usuário não é super admin |
| 404 | Não encontrado | Recurso não existe |
| 400 | Erro de validação | Dados inválidos na requisição |
| 500 | Erro interno | Erro no servidor |

---

## 📝 Fluxo de Uso Recomendado

### 1. Dashboard Inicial

```bash
GET /api/admin/dashboard
```

Visualize estatísticas gerais do sistema.

### 2. Listar Empresas

```bash
GET /api/admin/companies
```

Veja todas as empresas cadastradas.

### 3. Impersonate

```bash
POST /api/admin/impersonate/{company_id}
```

Gere um token de 1 hora para acessar dados da empresa.

### 4. Acessar Dados

Use o token de impersonate em endpoints normais:

```bash
GET /api/financial-entries
GET /api/payment-modalities
POST /api/financial-entries
...
```

### 5. Gerenciar Usuários

```bash
GET /api/admin/users?company_id={company_id}
POST /api/admin/users
PATCH /api/admin/users/{user_id}/toggle-active
```

---

## 🎯 Exemplo Completo

```bash
# 1. Login
POST http://localhost:5000/api/auth/login
{
  "email": "teste@teste.com",
  "password": "123456"
}
# Guarda o token: eyJ0eXAiOiJKV1Qi...

# 2. Ver dashboard
GET http://localhost:5000/api/admin/dashboard
Authorization: Bearer eyJ0eXAiOiJKV1Qi...

# 3. Listar empresas
GET http://localhost:5000/api/admin/companies
Authorization: Bearer eyJ0eXAiOiJKV1Qi...

# 4. Impersonate empresa específica
POST http://localhost:5000/api/admin/impersonate/company-uuid-123
Authorization: Bearer eyJ0eXAiOiJKV1Qi...
# Recebe novo token de impersonate: eyJpbXBlcnNvbmF0aW5n...

# 5. Acessar dados da empresa com token de impersonate
GET http://localhost:5000/api/financial-entries
Authorization: Bearer eyJpbXBlcnNvbmF0aW5n...

# 6. Criar lançamento como se fosse usuário da empresa
POST http://localhost:5000/api/financial-entries
Authorization: Bearer eyJpbXBlcnNvbmF0aW5n...
{
  "value": 1000.00,
  "date": "2025-12-29",
  "modality_id": "modality-uuid"
}
```

---

## ⚡ Dicas

1. **Token de Impersonate expira em 1 hora** - Gere um novo quando necessário
2. **Super Admin tem bypass de features** - Acesso total mesmo sem features atribuídas
3. **company_id no impersonate** - O token de impersonate substitui o company_id para a empresa alvo
4. **Auditoria** - O campo `impersonating: true` identifica ações feitas via impersonate
5. **Empresa original** - `original_company_id` preserva a empresa do super admin

---

## 🚀 Usuário de Teste

Criado pelo seed:

- **Email:** teste@teste.com
- **Senha:** 123456
- **Super Admin:** SIM
- **Empresa:** Empresa Teste Ltda

Use este usuário para testar todos os endpoints administrativos!
