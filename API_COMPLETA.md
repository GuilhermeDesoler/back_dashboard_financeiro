# 📚 API Completa - Dashboard Financeiro Multi-Tenant

Documentação completa de todos os endpoints da API com exemplos de uso.

---

## 🌐 Informações Gerais

- **Base URL:** `http://localhost:5000`
- **Versão:** 2.0.0
- **Arquitetura:** Multi-Tenant (Database por empresa)
- **Autenticação:** JWT Bearer Token

### Estrutura de Bancos de Dados

```
MongoDB
├── shared_db (Dados Globais)
│   ├── companies          # Todas as empresas
│   ├── users              # Todos os usuários
│   └── features           # Features do sistema
│
└── cmp_{hash}_db (Por Empresa)
    ├── financial_entries  # Lançamentos financeiros
    ├── payment_modalities # Modalidades de pagamento
    └── roles              # Roles/Papéis
```

---

## 📑 Índice de Endpoints

1. [Autenticação](#-autenticação)
2. [Administração (Super Admin)](#-administração-super-admin)
3. [Empresas](#-empresas)
4. [Usuários](#-usuários)
5. [Modalidades de Pagamento](#-modalidades-de-pagamento)
6. [Lançamentos Financeiros](#-lançamentos-financeiros)

---

## 🔐 Autenticação

### POST /api/auth/register

Registra uma nova empresa e o primeiro usuário (admin).

**⚠️ PÚBLICO** (não requer autenticação)

```bash
POST http://localhost:5000/api/auth/register
Content-Type: application/json

{
  "email": "admin@empresa.com",
  "password": "senha123",
  "name": "Administrador",
  "company_name": "Minha Empresa Ltda",
  "cnpj": "12.345.678/0001-90"
}
```

**Response 201:**
```json
{
  "message": "Usuário registrado com sucesso",
  "user": {
    "id": "user-uuid",
    "email": "admin@empresa.com",
    "name": "Administrador",
    "company_id": "company-uuid",
    "role_ids": ["role-admin-uuid"],
    "is_active": true,
    "is_super_admin": false
  }
}
```

**O que acontece:**
- ✅ Cria a empresa no `shared_db`
- ✅ Cria o banco `cmp_{hash}_db` da empresa
- ✅ Cria role "Admin" com todas as features
- ✅ Cria o usuário com role Admin
- ✅ Usuário fica pronto para fazer login

---

### POST /api/auth/login

Autentica um usuário e retorna tokens JWT.

**⚠️ PÚBLICO** (não requer autenticação)

```bash
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "email": "admin@empresa.com",
  "password": "senha123"
}
```

**Response 200:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "user-uuid",
    "email": "admin@empresa.com",
    "name": "Administrador",
    "company_id": "company-uuid",
    "roles": ["Admin"],
    "features": [
      "financial_entries.create",
      "financial_entries.read",
      "payment_modalities.create",
      ...
    ],
    "is_super_admin": false
  }
}
```

**Token contém:**
- `user_id`: ID do usuário
- `email`: Email do usuário
- `name`: Nome do usuário
- `company_id`: ID da empresa (define isolamento de dados)
- `roles`: Array de roles
- `features`: Array de features (permissões)
- `is_super_admin`: Se é super administrador

**Validade:** 24 horas

---

### POST /api/auth/refresh

Renova o token de acesso usando refresh token.

**⚠️ PÚBLICO** (não requer autenticação)

```bash
POST http://localhost:5000/api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response 200:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { ... }
}
```

---

### GET /api/auth/me

Retorna informações do usuário autenticado.

**🔒 Requer:** Autenticação

```bash
GET http://localhost:5000/api/auth/me
Authorization: Bearer eyJ0eXAiOiJKV1Qi...
```

**Response 200:**
```json
{
  "user_id": "user-uuid",
  "email": "admin@empresa.com",
  "name": "Administrador",
  "company_id": "company-uuid",
  "roles": ["Admin"],
  "features": [...]
}
```

---

## 👑 Administração (Super Admin)

**🔒 Todos os endpoints requerem:** `is_super_admin = true`

### GET /api/admin/dashboard

Dashboard com estatísticas gerais do sistema.

```bash
GET http://localhost:5000/api/admin/dashboard
Authorization: Bearer {super_admin_token}
```

**Response 200:**
```json
{
  "companies": {
    "total": 10,
    "active": 9,
    "inactive": 1,
    "by_plan": {
      "basic": 5,
      "premium": 4,
      "enterprise": 1
    }
  },
  "users": {
    "total": 45,
    "active": 42,
    "inactive": 3,
    "super_admins": 1
  },
  "features": {
    "total": 23
  }
}
```

---

### GET /api/admin/companies

Lista todas as empresas do sistema.

```bash
# Todas as empresas ativas
GET http://localhost:5000/api/admin/companies
Authorization: Bearer {super_admin_token}

# Incluir inativas
GET http://localhost:5000/api/admin/companies?only_active=false
Authorization: Bearer {super_admin_token}
```

**Response 200:**
```json
[
  {
    "id": "company-uuid-1",
    "name": "Empresa A Ltda",
    "cnpj": "11.222.333/0001-44",
    "phone": "(11) 98765-4321",
    "plan": "premium",
    "is_active": true,
    "users_count": 5,
    "created_at": "2025-12-29T10:00:00",
    "updated_at": "2025-12-29T10:00:00"
  },
  {
    "id": "company-uuid-2",
    "name": "Empresa B S.A.",
    "cnpj": "22.333.444/0001-55",
    "phone": "(11) 91234-5678",
    "plan": "basic",
    "is_active": true,
    "users_count": 3,
    "created_at": "2025-12-29T11:00:00",
    "updated_at": "2025-12-29T11:00:00"
  }
]
```

---

### POST /api/admin/companies

Cria uma nova empresa.

```bash
POST http://localhost:5000/api/admin/companies
Authorization: Bearer {super_admin_token}
Content-Type: application/json

{
  "name": "Nova Empresa Ltda",
  "cnpj": "33.444.555/0001-66",
  "phone": "(11) 99999-8888",
  "plan": "basic"
}
```

**Response 201:**
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

**O que acontece:**
- ✅ Cria empresa no `shared_db`
- ✅ Cria banco `cmp_{hash}_db` com índices
- ✅ Banco pronto para receber dados

---

### GET /api/admin/companies/{company_id}

Detalhes de uma empresa específica.

```bash
GET http://localhost:5000/api/admin/companies/company-uuid-123
Authorization: Bearer {super_admin_token}
```

**Response 200:**
```json
{
  "id": "company-uuid-123",
  "name": "Empresa A Ltda",
  "cnpj": "11.222.333/0001-44",
  "phone": "(11) 98765-4321",
  "plan": "premium",
  "is_active": true,
  "users_count": 5,
  "users": [
    {
      "id": "user-uuid-1",
      "name": "João Silva",
      "email": "joao@empresaa.com",
      "is_active": true,
      "is_super_admin": false
    },
    {
      "id": "user-uuid-2",
      "name": "Maria Santos",
      "email": "maria@empresaa.com",
      "is_active": true,
      "is_super_admin": false
    }
  ],
  "created_at": "2025-12-29T10:00:00",
  "updated_at": "2025-12-29T10:00:00"
}
```

---

### POST /api/admin/impersonate/{company_id}

**⭐ IMPERSONATE:** Gera token para acessar dados de uma empresa.

**Validade do token:** 1 HORA

```bash
POST http://localhost:5000/api/admin/impersonate/company-uuid-123
Authorization: Bearer {super_admin_token}
```

**Response 200:**
```json
{
  "token": "eyJpbXBlcnNvbmF0aW5n...",
  "company": {
    "id": "company-uuid-123",
    "name": "Empresa A Ltda",
    "cnpj": "11.222.333/0001-44",
    "phone": "(11) 98765-4321",
    "plan": "premium",
    "is_active": true
  },
  "message": "Impersonando empresa: Empresa A Ltda",
  "expires_in_hours": 1
}
```

**Token de impersonate contém:**
- `company_id`: ID da empresa alvo (não do super admin!)
- `is_super_admin`: true
- `impersonating`: true
- `original_company_id`: Empresa original do super admin
- Todas as features do sistema

**Como usar:**

Após receber o token, use-o em qualquer endpoint normal:

```bash
# Listar lançamentos da empresa
GET http://localhost:5000/api/financial-entries
Authorization: Bearer {impersonate_token}

# Criar modalidade na empresa
POST http://localhost:5000/api/payment-modalities
Authorization: Bearer {impersonate_token}
Content-Type: application/json

{
  "name": "PIX",
  "color": "#00FF00"
}
```

**⚠️ IMPORTANTE:** Token expira em 1 hora!

---

### GET /api/admin/users

Lista todos os usuários do sistema.

```bash
# Todos os usuários
GET http://localhost:5000/api/admin/users
Authorization: Bearer {super_admin_token}

# Filtrar por empresa
GET http://localhost:5000/api/admin/users?company_id=company-uuid-123
Authorization: Bearer {super_admin_token}

# Apenas ativos
GET http://localhost:5000/api/admin/users?only_active=true
Authorization: Bearer {super_admin_token}
```

**Response 200:**
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
    "name": "Super Admin",
    "email": "teste@teste.com",
    "company_id": "company-uuid-2",
    "is_active": true,
    "is_super_admin": true,
    "created_at": "2025-12-29T09:00:00"
  }
]
```

---

### POST /api/admin/users

Cria um novo usuário.

```bash
POST http://localhost:5000/api/admin/users
Authorization: Bearer {super_admin_token}
Content-Type: application/json

{
  "email": "novo@usuario.com",
  "password": "senha123",
  "name": "Novo Usuário",
  "company_id": "company-uuid-123",
  "is_super_admin": false
}
```

**Response 201:**
```json
{
  "message": "Usuário criado com sucesso",
  "user": {
    "id": "new-user-uuid",
    "email": "novo@usuario.com",
    "name": "Novo Usuário",
    "company_id": "company-uuid-123",
    "role_ids": [],
    "is_active": true,
    "is_super_admin": false,
    "created_at": "2025-12-29T12:00:00"
  }
}
```

---

### PATCH /api/admin/users/{user_id}/toggle-active

Ativa ou desativa um usuário.

```bash
# Ativar
PATCH http://localhost:5000/api/admin/users/user-uuid-123/toggle-active
Authorization: Bearer {super_admin_token}
Content-Type: application/json

{
  "activate": true
}

# Desativar
PATCH http://localhost:5000/api/admin/users/user-uuid-123/toggle-active
Authorization: Bearer {super_admin_token}
Content-Type: application/json

{
  "activate": false
}
```

**Response 200:**
```json
{
  "message": "Usuário ativado com sucesso"
}
```

---

## 🏢 Empresas

### GET /api/companies

Lista empresas (mesmo endpoint que admin, mas separado).

**🔒 Requer:** Super Admin

```bash
GET http://localhost:5000/api/companies
Authorization: Bearer {super_admin_token}
```

---

### POST /api/companies

Cria empresa (mesmo endpoint que admin, mas separado).

**🔒 Requer:** Super Admin

```bash
POST http://localhost:5000/api/companies
Authorization: Bearer {super_admin_token}
Content-Type: application/json

{
  "name": "Empresa Nova",
  "cnpj": "44.555.666/0001-77",
  "phone": "(11) 88888-7777",
  "plan": "premium"
}
```

---

## 💳 Modalidades de Pagamento

**🔒 Todos requerem:** Autenticação + Features específicas

### GET /api/payment-modalities

Lista modalidades de pagamento da empresa.

**🔒 Requer:** `payment_modalities.read`

```bash
# Apenas ativas
GET http://localhost:5000/api/payment-modalities
Authorization: Bearer {token}

# Incluir inativas
GET http://localhost:5000/api/payment-modalities?only_active=false
Authorization: Bearer {token}
```

**Response 200:**
```json
[
  {
    "id": "modality-uuid-1",
    "name": "PIX",
    "color": "#00FF00",
    "is_active": true,
    "created_at": "2025-12-29T10:00:00",
    "updated_at": "2025-12-29T10:00:00"
  },
  {
    "id": "modality-uuid-2",
    "name": "Cartão de Crédito",
    "color": "#0000FF",
    "is_active": true,
    "created_at": "2025-12-29T10:00:00",
    "updated_at": "2025-12-29T10:00:00"
  }
]
```

---

### POST /api/payment-modalities

Cria uma nova modalidade de pagamento.

**🔒 Requer:** `payment_modalities.create`

```bash
POST http://localhost:5000/api/payment-modalities
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Boleto",
  "color": "#FF0000"
}
```

**Response 201:**
```json
{
  "id": "new-modality-uuid",
  "name": "Boleto",
  "color": "#FF0000",
  "is_active": true,
  "created_at": "2025-12-29T12:00:00",
  "updated_at": "2025-12-29T12:00:00"
}
```

---

### PUT /api/payment-modalities/{modality_id}

Atualiza uma modalidade de pagamento.

**🔒 Requer:** `payment_modalities.update`

```bash
PUT http://localhost:5000/api/payment-modalities/modality-uuid-123
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "PIX Atualizado",
  "color": "#00AA00"
}
```

**Response 200:**
```json
{
  "id": "modality-uuid-123",
  "name": "PIX Atualizado",
  "color": "#00AA00",
  "is_active": true,
  "created_at": "2025-12-29T10:00:00",
  "updated_at": "2025-12-29T12:30:00"
}
```

---

### DELETE /api/payment-modalities/{modality_id}

Deleta uma modalidade de pagamento.

**🔒 Requer:** `payment_modalities.delete`

```bash
DELETE http://localhost:5000/api/payment-modalities/modality-uuid-123
Authorization: Bearer {token}
```

**Response 200:**
```json
{
  "message": "Modalidade deletada com sucesso"
}
```

---

### PATCH /api/payment-modalities/{modality_id}/toggle

Ativa ou desativa uma modalidade.

**🔒 Requer:** `payment_modalities.toggle`

```bash
# Ativar
PATCH http://localhost:5000/api/payment-modalities/modality-uuid-123/toggle
Authorization: Bearer {token}
Content-Type: application/json

{
  "activate": true
}

# Desativar
PATCH http://localhost:5000/api/payment-modalities/modality-uuid-123/toggle
Authorization: Bearer {token}
Content-Type: application/json

{
  "activate": false
}
```

**Response 200:**
```json
{
  "id": "modality-uuid-123",
  "name": "PIX",
  "color": "#00FF00",
  "is_active": false,
  "created_at": "2025-12-29T10:00:00",
  "updated_at": "2025-12-29T13:00:00"
}
```

---

## 💰 Lançamentos Financeiros

**🔒 Todos requerem:** Autenticação + Features específicas

### GET /api/financial-entries

Lista lançamentos financeiros da empresa.

**🔒 Requer:** `financial_entries.read`

```bash
# Todos os lançamentos
GET http://localhost:5000/api/financial-entries
Authorization: Bearer {token}

# Filtrar por modalidade
GET http://localhost:5000/api/financial-entries?modality_id=modality-uuid-123
Authorization: Bearer {token}

# Filtrar por período
GET http://localhost:5000/api/financial-entries?start_date=2025-12-01&end_date=2025-12-31
Authorization: Bearer {token}

# Combinar filtros
GET http://localhost:5000/api/financial-entries?modality_id=modality-uuid-123&start_date=2025-12-01&end_date=2025-12-31
Authorization: Bearer {token}
```

**Response 200:**
```json
[
  {
    "id": "entry-uuid-1",
    "value": 1500.00,
    "date": "2025-12-29T00:00:00",
    "modality_id": "modality-uuid-1",
    "modality_name": "PIX",
    "modality_color": "#00FF00",
    "created_at": "2025-12-29T10:00:00",
    "updated_at": "2025-12-29T10:00:00"
  },
  {
    "id": "entry-uuid-2",
    "value": 2300.50,
    "date": "2025-12-28T00:00:00",
    "modality_id": "modality-uuid-2",
    "modality_name": "Cartão de Crédito",
    "modality_color": "#0000FF",
    "created_at": "2025-12-29T11:00:00",
    "updated_at": "2025-12-29T11:00:00"
  }
]
```

---

### POST /api/financial-entries

Cria um novo lançamento financeiro.

**🔒 Requer:** `financial_entries.create`

```bash
POST http://localhost:5000/api/financial-entries
Authorization: Bearer {token}
Content-Type: application/json

{
  "value": 1000.00,
  "date": "2025-12-29",
  "modality_id": "modality-uuid-123"
}
```

**Response 201:**
```json
{
  "id": "new-entry-uuid",
  "value": 1000.00,
  "date": "2025-12-29T00:00:00",
  "modality_id": "modality-uuid-123",
  "modality_name": "PIX",
  "modality_color": "#00FF00",
  "created_at": "2025-12-29T12:00:00",
  "updated_at": "2025-12-29T12:00:00"
}
```

**Validações:**
- ✅ Modalidade deve existir
- ✅ Modalidade deve estar ativa
- ✅ Value deve ser número válido
- ✅ Date deve ser formato ISO (YYYY-MM-DD)

---

### PUT /api/financial-entries/{entry_id}

Atualiza um lançamento financeiro.

**🔒 Requer:** `financial_entries.update`

```bash
PUT http://localhost:5000/api/financial-entries/entry-uuid-123
Authorization: Bearer {token}
Content-Type: application/json

{
  "value": 1500.00,
  "date": "2025-12-30",
  "modality_id": "modality-uuid-456"
}
```

**Response 200:**
```json
{
  "id": "entry-uuid-123",
  "value": 1500.00,
  "date": "2025-12-30T00:00:00",
  "modality_id": "modality-uuid-456",
  "modality_name": "Boleto",
  "modality_color": "#FF0000",
  "created_at": "2025-12-29T10:00:00",
  "updated_at": "2025-12-29T13:00:00"
}
```

---

### DELETE /api/financial-entries/{entry_id}

Deleta um lançamento financeiro.

**🔒 Requer:** `financial_entries.delete`

```bash
DELETE http://localhost:5000/api/financial-entries/entry-uuid-123
Authorization: Bearer {token}
```

**Response 200:**
```json
{
  "message": "Lançamento deletado com sucesso"
}
```

---

## 🔑 Códigos de Erro

| Código | Mensagem | Significado |
|--------|----------|-------------|
| **200** | OK | Requisição bem-sucedida |
| **201** | Created | Recurso criado com sucesso |
| **400** | Bad Request | Dados inválidos na requisição |
| **401** | Unauthorized | Token ausente, inválido ou expirado |
| **403** | Forbidden | Usuário sem permissão (falta feature ou não é super admin) |
| **404** | Not Found | Recurso não encontrado |
| **500** | Internal Server Error | Erro no servidor |

---

## 🎯 Fluxos de Uso Completos

### 📝 Fluxo 1: Nova Empresa se Registrando

```bash
# 1. Registrar empresa e primeiro usuário
POST /api/auth/register
{
  "email": "admin@minhaempresa.com",
  "password": "senha123",
  "name": "Administrador",
  "company_name": "Minha Empresa Ltda",
  "cnpj": "12.345.678/0001-90"
}

# 2. Fazer login
POST /api/auth/login
{
  "email": "admin@minhaempresa.com",
  "password": "senha123"
}
# Recebe: token

# 3. Criar modalidades de pagamento
POST /api/payment-modalities
Authorization: Bearer {token}
{
  "name": "PIX",
  "color": "#00FF00"
}

POST /api/payment-modalities
Authorization: Bearer {token}
{
  "name": "Cartão",
  "color": "#0000FF"
}

# 4. Criar lançamentos financeiros
POST /api/financial-entries
Authorization: Bearer {token}
{
  "value": 1500.00,
  "date": "2025-12-29",
  "modality_id": "modality-uuid"
}

# 5. Listar lançamentos
GET /api/financial-entries?start_date=2025-12-01&end_date=2025-12-31
Authorization: Bearer {token}
```

---

### 👑 Fluxo 2: Super Admin Gerenciando Sistema

```bash
# 1. Login como super admin
POST /api/auth/login
{
  "email": "teste@teste.com",
  "password": "123456"
}
# Recebe: token com is_super_admin = true

# 2. Ver dashboard
GET /api/admin/dashboard
Authorization: Bearer {token}

# 3. Listar todas as empresas
GET /api/admin/companies
Authorization: Bearer {token}

# 4. Ver detalhes de uma empresa
GET /api/admin/companies/company-uuid-123
Authorization: Bearer {token}

# 5. Impersonate empresa (gera token de 1h)
POST /api/admin/impersonate/company-uuid-123
Authorization: Bearer {token}
# Recebe: impersonate_token

# 6. Acessar dados da empresa com impersonate
GET /api/financial-entries
Authorization: Bearer {impersonate_token}

POST /api/payment-modalities
Authorization: Bearer {impersonate_token}
{
  "name": "Nova Modalidade",
  "color": "#AABBCC"
}

# 7. Criar novo usuário para a empresa
POST /api/admin/users
Authorization: Bearer {token}
{
  "email": "novo@empresax.com",
  "password": "senha123",
  "name": "Novo Usuário",
  "company_id": "company-uuid-123",
  "is_super_admin": false
}

# 8. Desativar usuário
PATCH /api/admin/users/user-uuid-456/toggle-active
Authorization: Bearer {token}
{
  "activate": false
}
```

---

### 📊 Fluxo 3: Usuário Normal Operando

```bash
# 1. Login
POST /api/auth/login
{
  "email": "usuario@empresa.com",
  "password": "senha123"
}
# Recebe: token (sem is_super_admin)

# 2. Ver minhas informações
GET /api/auth/me
Authorization: Bearer {token}

# 3. Listar modalidades disponíveis
GET /api/payment-modalities
Authorization: Bearer {token}

# 4. Criar lançamento financeiro
POST /api/financial-entries
Authorization: Bearer {token}
{
  "value": 2500.00,
  "date": "2025-12-29",
  "modality_id": "modality-uuid"
}

# 5. Listar meus lançamentos do mês
GET /api/financial-entries?start_date=2025-12-01&end_date=2025-12-31
Authorization: Bearer {token}

# 6. Editar lançamento
PUT /api/financial-entries/entry-uuid-123
Authorization: Bearer {token}
{
  "value": 2600.00,
  "date": "2025-12-29",
  "modality_id": "modality-uuid"
}

# 7. Deletar lançamento
DELETE /api/financial-entries/entry-uuid-123
Authorization: Bearer {token}
```

---

## 🔐 Sistema de Permissões (RBAC)

### Features Disponíveis

#### Financial Entries
- `financial_entries.create` - Criar lançamentos
- `financial_entries.read` - Visualizar lançamentos
- `financial_entries.update` - Atualizar lançamentos
- `financial_entries.delete` - Deletar lançamentos

#### Payment Modalities
- `payment_modalities.create` - Criar modalidades
- `payment_modalities.read` - Visualizar modalidades
- `payment_modalities.update` - Atualizar modalidades
- `payment_modalities.delete` - Deletar modalidades
- `payment_modalities.toggle` - Ativar/desativar modalidades

#### Users (Admin)
- `users.create` - Criar usuários
- `users.read` - Visualizar usuários
- `users.update` - Atualizar usuários
- `users.delete` - Deletar usuários

#### Roles (Admin)
- `roles.create` - Criar roles
- `roles.read` - Visualizar roles
- `roles.update` - Atualizar roles
- `roles.delete` - Deletar roles

#### Company (Admin)
- `company.create` - Criar empresas (super admin)
- `company.read` - Visualizar empresas (super admin)
- `company.settings.read` - Ver configurações
- `company.settings.update` - Atualizar configurações

#### Reports
- `reports.financial_summary` - Ver resumo financeiro
- `reports.export` - Exportar relatórios

### Hierarquia de Permissões

1. **Super Admin** (`is_super_admin = true`)
   - Acesso TOTAL a tudo
   - Bypass automático de features
   - Pode impersonate qualquer empresa
   - Pode criar/gerenciar empresas
   - Pode criar/gerenciar usuários de qualquer empresa

2. **Admin** (Role padrão na empresa)
   - Todas as features da empresa
   - Não pode acessar outras empresas
   - Não pode criar empresas
   - Pode gerenciar usuários da própria empresa

3. **Usuário** (Roles personalizadas)
   - Features específicas atribuídas via role
   - Acesso apenas aos recursos permitidos
   - Dados isolados por empresa

---

## 🚀 Inicialização do Sistema

### 1. Setup Inicial

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar .env
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=shared_db
JWT_SECRET=sua-chave-secreta-super-segura-aqui
```

### 2. Popular Dados Iniciais

```bash
# Executar seed completo
python scripts/seed_all.py
```

**O que o seed faz:**
- ✅ Cria 23 features do sistema
- ✅ Cria empresa de teste "Empresa Teste Ltda"
- ✅ Cria banco da empresa com índices
- ✅ Cria role "Admin" com todas as features
- ✅ Cria super admin: `teste@teste.com` / `123456`

### 3. Iniciar Servidor

```bash
python src/app.py
```

Servidor inicia em: `http://localhost:5000`

### 4. Testar

```bash
# Ver informações da API
curl http://localhost:5000/

# Login como super admin
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "teste@teste.com",
    "password": "123456"
  }'
```

---

## 📚 Recursos Adicionais

### Headers Obrigatórios

Todas as requisições (exceto públicas):
```
Authorization: Bearer {token}
Content-Type: application/json
```

### Formato de Datas

- **Envio:** `YYYY-MM-DD` (ex: `2025-12-29`)
- **Resposta:** ISO 8601 (ex: `2025-12-29T10:30:00`)

### Paginação

Atualmente não implementada. Retorna todos os resultados.

### Rate Limiting

Não implementado. Considerar adicionar em produção.

---

## ⚠️ Notas Importantes

1. **JWT_SECRET:** SEMPRE mude em produção!
2. **HTTPS:** Use HTTPS em produção (nunca HTTP para tokens)
3. **Backup:** Faça backup regular dos bancos de dados
4. **Impersonate:** Token expira em 1 hora
5. **Super Admin:** Muito poder - use com cuidado
6. **Isolamento:** Dados entre empresas são 100% isolados
7. **company_id:** Define qual empresa o usuário acessa

---

## 🎯 Próximos Passos Recomendados

1. ✅ Implementar renovação automática de token
2. ✅ Adicionar paginação aos endpoints de listagem
3. ✅ Implementar soft delete para auditoria
4. ✅ Adicionar logs de auditoria para ações sensíveis
5. ✅ Criar relatórios financeiros
6. ✅ Adicionar exportação de dados (CSV, Excel, PDF)
7. ✅ Implementar webhooks para eventos
8. ✅ Adicionar rate limiting
9. ✅ Criar testes automatizados

---

**Sistema implementado com Clean Architecture e SOLID! 🎯**
