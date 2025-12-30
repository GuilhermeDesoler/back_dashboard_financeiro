# 💰 Dashboard Financeiro - API Backend

Sistema completo de gestão financeira multi-tenant com controle administrativo centralizado.

**Versão:** 2.0.0
**Arquitetura:** Clean Architecture + SOLID
**Multi-Tenancy:** Database por empresa
**Autenticação:** JWT (24h) + Refresh Token (7 dias)

---

## 📋 Índice

1. [Visão Geral](#-visão-geral)
2. [Tecnologias](#-tecnologias)
3. [Arquitetura](#-arquitetura)
4. [Instalação](#-instalação)
5. [Configuração](#-configuração)
6. [Executando](#-executando)
7. [API Endpoints](#-api-endpoints)
8. [Sistema de Permissões](#-sistema-de-permissões)
9. [Logs de Auditoria](#-logs-de-auditoria)
10. [Multi-Tenancy](#-multi-tenancy)
11. [Fluxos de Uso](#-fluxos-de-uso)
12. [Para o Frontend](#-para-o-frontend)

---

## 🎯 Visão Geral

Sistema de **controle administrativo privado** onde:

- ✅ **Super Admin** cria e gerencia empresas
- ✅ **Super Admin** cria usuários para cada empresa
- ✅ **Empresas** têm dados completamente isolados (multi-tenancy)
- ✅ **Usuários** só acessam dados da própria empresa
- ✅ **Logs de auditoria** registram todas as ações críticas
- ✅ **Impersonate** permite super admin acessar qualquer empresa por 1h

**NÃO há auto-registro público.** Apenas o super admin controla quem entra no sistema.

---

## 🛠 Tecnologias

- **Python 3.14**
- **Flask** - Framework web
- **MongoDB** - Banco de dados NoSQL
- **PyJWT** - Autenticação JWT
- **bcrypt** - Hash de senhas
- **pymongo** - Driver MongoDB

---

## 🏗 Arquitetura

### Clean Architecture

```
src/
├── domain/              # Entidades e regras de negócio
│   ├── entities/        # Company, User, FinancialEntry, etc.
│   └── repositories/    # Interfaces dos repositórios
│
├── application/         # Casos de uso
│   ├── use_cases/       # Lógica de negócio
│   ├── services/        # Serviços (AuditService)
│   └── middleware/      # Auth, RBAC
│
├── infra/              # Implementações
│   ├── repositories/    # MongoDB repositories
│   ├── security/        # JWT, PasswordHash
│   └── database/        # TenantDatabaseManager
│
└── presentation/       # Controllers/Routes
    └── routes/          # Blueprints Flask
```

### Multi-Tenancy

```
MongoDB
├── shared_db (Dados Globais)
│   ├── companies          # Todas as empresas (incluindo administrativa)
│   ├── users              # Todos os usuários (incluindo super admin)
│   ├── features           # Features do sistema
│   └── audit_logs         # Logs de auditoria
│
├── cmp_{hash_admin}_db (Empresa Administrativa) ⭐
│   └── roles              # Role "Super Admin"
│
├── cmp_{hash1}_db (Empresa Cliente 1)
│   ├── financial_entries  # Lançamentos da Empresa 1
│   ├── payment_modalities # Modalidades da Empresa 1
│   └── roles              # Roles da Empresa 1
│
└── cmp_{hash2}_db (Empresa Cliente 2)
    ├── financial_entries  # Lançamentos da Empresa 2
    ├── payment_modalities # Modalidades da Empresa 2
    └── roles              # Roles da Empresa 2
```

**Isolamento total:** Cada empresa tem seu próprio database. Impossível vazar dados entre empresas.

**⭐ Empresa Administrativa:**

- Tem `is_admin_company=True`
- **NÃO aparece** na listagem `GET /admin/companies`
- Contém apenas o super admin e sua role
- Não tem lançamentos financeiros ou modalidades de pagamento
- Serve apenas para segregar usuários administrativos dos usuários clientes

---

## 📦 Instalação

### 1. Clonar o repositório

```bash
git clone <repo-url>
cd back_dashboard_financeiro
```

### 2. Criar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Instalar e iniciar MongoDB

```bash
# macOS
brew install mongodb-community
brew services start mongodb-community

# Ubuntu/Debian
sudo apt install mongodb
sudo systemctl start mongodb

# Windows - Download do site oficial
```

---

## ⚙️ Configuração

### 1. Criar arquivo `.env`

```bash
cp .env.example .env
```

### 2. Configurar variáveis de ambiente

```env
# MongoDB
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=shared_db

# JWT Secret (MUDE EM PRODUÇÃO!)
JWT_SECRET=sua-chave-secreta-super-segura-aqui-mude-em-producao

# Ambiente
ENVIRONMENT=development
```

**⚠️ IMPORTANTE:**
- **NUNCA** use a mesma `JWT_SECRET` em produção
- Use uma chave aleatória de 32+ caracteres
- Mantenha `.env` fora do Git (já está no `.gitignore`)

### 3. Inicializar Sistema

#### 3.1. Criar Empresa Administrativa e Super Admin

```bash
python scripts/init_admin_company.py
```

**O que faz:**

- ✅ Cria empresa administrativa "Administração do Sistema"
- ✅ Marca como `is_admin_company=True` (não aparece na listagem)
- ✅ Cria role "Super Admin" com todas as features
- ✅ **Cria super admin:** `admin@sistema.com` / `admin123`

**⚠️ IMPORTANTE:**

- A empresa administrativa **NÃO aparece** na listagem de empresas (`GET /admin/companies`)
- Super admin está vinculado à empresa administrativa, não às empresas clientes
- Super admin pode criar empresas, usuários e fazer impersonate

#### 3.2. Popular Features

```bash
python scripts/seed_all.py
```

**O que faz:**

- ✅ Cria 23 features do sistema
- ✅ Cria empresa de teste "Empresa Teste Ltda"
- ✅ Cria banco da empresa com índices
- ✅ Cria role "Admin" para a empresa teste

#### 3.3. Popular Dados de Teste (Opcional)

```bash
python scripts/seed_test_data.py
```

**O que faz:**

- ✅ Cria 3 empresas adicionais (Tech Solutions, Comercial ABC, Indústria XYZ)
- ✅ 3 usuários por empresa (admin, financeiro, operador)
- ✅ 6 modalidades de pagamento por empresa
- ✅ ~180 lançamentos financeiros por empresa (60 dias)

---

## 🚀 Executando

### Desenvolvimento

```bash
python src/app.py
```

Servidor inicia em: `http://localhost:5000`

### Produção

```bash
# Use gunicorn ou outro WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.app:app
```

### Testar se está funcionando

```bash
curl http://localhost:5000/
# ou
curl http://localhost:5000/health
```

---

## 📡 API Endpoints

### Base URL
```
http://localhost:5000/api
```

### Autenticação (Públicos)

#### POST `/auth/login`
Login de qualquer usuário (super admin ou usuário de empresa).

**Request:**
```json
{
  "email": "teste@teste.com",
  "password": "123456"
}
```

**Response 200:**
```json
{
  "token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {
    "id": "user-uuid",
    "email": "teste@teste.com",
    "name": "Super Admin",
    "company_id": "company-uuid",
    "roles": [],
    "features": [...],
    "is_super_admin": true
  }
}
```

#### POST `/auth/refresh`
Renova o token usando refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response 200:**
```json
{
  "token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {...}
}
```

#### GET `/auth/me`
Retorna dados do usuário autenticado.

**Headers:**
```
Authorization: Bearer {token}
```

**Response 200:**
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "name": "Nome",
  "company_id": "company-uuid",
  "roles": ["Admin"],
  "features": ["financial_entries.create", ...]
}
```

---

### Administrativos (Super Admin Only)

**⚠️ Todos requerem:** `is_super_admin = true` no token

#### GET `/admin/dashboard`
Dashboard com estatísticas do sistema.

**Response 200:**
```json
{
  "companies": {
    "total": 10,
    "active": 9,
    "inactive": 1,
    "by_plan": {"basic": 5, "premium": 4, "enterprise": 1}
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

#### GET `/admin/companies`
Lista todas as empresas.

**Query params:**
- `only_active=true|false` (default: true)

**Response 200:**
```json
[
  {
    "id": "company-uuid",
    "name": "Empresa ABC Ltda",
    "cnpj": "12.345.678/0001-90",
    "phone": "(11) 98765-4321",
    "plan": "premium",
    "is_active": true,
    "users_count": 5,
    "created_at": "2025-12-29T10:00:00",
    "updated_at": "2025-12-29T10:00:00"
  }
]
```

#### POST `/admin/companies`
Cria uma nova empresa.

**Request:**
```json
{
  "name": "Nova Empresa Ltda",
  "cnpj": "12.345.678/0001-90",
  "phone": "(11) 99999-9999",
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
    "cnpj": "12.345.678/0001-90",
    "plan": "basic",
    "is_active": true,
    "created_at": "2025-12-29T12:00:00"
  }
}
```

**O que acontece:**
- ✅ Cria empresa no `shared_db`
- ✅ Cria banco `cmp_{hash}_db` com índices
- ✅ **Registra log de auditoria**

#### GET `/admin/companies/{company_id}`
Detalhes de uma empresa específica com lista de usuários.

**Response 200:**
```json
{
  "id": "company-uuid",
  "name": "Empresa ABC Ltda",
  "cnpj": "12.345.678/0001-90",
  "plan": "premium",
  "is_active": true,
  "users_count": 5,
  "users": [
    {
      "id": "user-uuid-1",
      "name": "João Silva",
      "email": "joao@empresaabc.com",
      "is_active": true,
      "is_super_admin": false
    }
  ],
  "created_at": "2025-12-29T10:00:00",
  "updated_at": "2025-12-29T10:00:00"
}
```

#### POST `/admin/impersonate/{company_id}`
**⭐ CRÍTICO:** Gera token de 1 HORA para acessar dados de uma empresa.

**Response 200:**
```json
{
  "token": "eyJ...",
  "company": {
    "id": "company-uuid",
    "name": "Empresa ABC Ltda",
    "cnpj": "12.345.678/0001-90",
    "plan": "premium",
    "is_active": true
  },
  "message": "Impersonando empresa: Empresa ABC Ltda",
  "expires_in_hours": 1
}
```

**Como usar:**
```bash
# 1. Impersonate
POST /api/admin/impersonate/company-uuid-123
Authorization: Bearer {super_admin_token}

# 2. Usar token retornado em qualquer endpoint normal
GET /api/financial-entries
Authorization: Bearer {impersonate_token}
```

**⚠️ Token expira em 1h!**

**✅ Registra log de auditoria CRÍTICO**

#### GET `/admin/users`
Lista todos os usuários do sistema.

**Query params:**
- `company_id=company-uuid` (opcional)
- `only_active=true|false` (default: true)

**Response 200:**
```json
[
  {
    "id": "user-uuid",
    "name": "João Silva",
    "email": "joao@empresa.com",
    "company_id": "company-uuid",
    "is_active": true,
    "is_super_admin": false,
    "created_at": "2025-12-29T10:00:00"
  }
]
```

#### POST `/admin/users`
Cria um novo usuário.

**Request:**
```json
{
  "email": "novo@usuario.com",
  "password": "senha123",
  "name": "Novo Usuário",
  "company_id": "company-uuid",
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
    "company_id": "company-uuid",
    "role_ids": [],
    "is_active": true,
    "is_super_admin": false,
    "created_at": "2025-12-29T12:00:00"
  }
}
```

**✅ Registra log de auditoria**

#### PATCH `/admin/users/{user_id}/toggle-active`
Ativa ou desativa um usuário.

**Request:**
```json
{
  "activate": false
}
```

**Response 200:**
```json
{
  "message": "Usuário desativado com sucesso"
}
```

**✅ Registra log de auditoria CRÍTICO**

#### GET `/admin/audit-logs`
Lista logs de auditoria do sistema.

**Query params:**
- `user_id=uuid` (opcional)
- `company_id=uuid` (opcional)
- `action=create_company` (opcional)
- `start_date=2025-12-01` (opcional, formato YYYY-MM-DD)
- `end_date=2025-12-31` (opcional, formato YYYY-MM-DD)
- `limit=100` (default: 100, max: 500)
- `skip=0` (paginação)

**Response 200:**
```json
{
  "total": 25,
  "limit": 100,
  "skip": 0,
  "logs": [
    {
      "id": "log-uuid",
      "action": "create_company",
      "user_id": "super-admin-uuid",
      "user_email": "teste@teste.com",
      "company_id": null,
      "target_type": "company",
      "target_id": "new-company-uuid",
      "details": {
        "company_name": "Empresa ABC",
        "cnpj": "12.345.678/0001-90",
        "plan": "premium"
      },
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0...",
      "created_at": "2025-12-29T12:00:00"
    }
  ]
}
```

---

### Lançamentos Financeiros (Usuários Autenticados)

**🔒 Requerem:** Autenticação + Features específicas

#### GET `/financial-entries`
Lista lançamentos da empresa do usuário.

**Headers:**
```
Authorization: Bearer {token}
```

**Query params:**
- `modality_id=uuid` (opcional)
- `start_date=2025-12-01` (opcional)
- `end_date=2025-12-31` (opcional)

**Response 200:**
```json
[
  {
    "id": "entry-uuid",
    "value": 1500.00,
    "date": "2025-12-29T00:00:00",
    "modality_id": "modality-uuid",
    "modality_name": "PIX",
    "modality_color": "#00FF00",
    "created_at": "2025-12-29T10:00:00",
    "updated_at": "2025-12-29T10:00:00"
  }
]
```

#### POST `/financial-entries`
Cria lançamento financeiro.

**Requer feature:** `financial_entries.create`

**Request:**
```json
{
  "value": 1500.00,
  "date": "2025-12-29",
  "modality_id": "modality-uuid"
}
```

**Response 201:**
```json
{
  "id": "new-entry-uuid",
  "value": 1500.00,
  "date": "2025-12-29T00:00:00",
  "modality_id": "modality-uuid",
  "modality_name": "PIX",
  "modality_color": "#00FF00",
  "created_at": "2025-12-29T12:00:00",
  "updated_at": "2025-12-29T12:00:00"
}
```

#### PUT `/financial-entries/{entry_id}`
Atualiza lançamento.

**Requer feature:** `financial_entries.update`

#### DELETE `/financial-entries/{entry_id}`
Deleta lançamento.

**Requer feature:** `financial_entries.delete`

---

### Modalidades de Pagamento (Usuários Autenticados)

**🔒 Requerem:** Autenticação + Features específicas

#### GET `/payment-modalities`
Lista modalidades da empresa.

**Query params:**
- `only_active=true|false` (default: true)

**Response 200:**
```json
[
  {
    "id": "modality-uuid",
    "name": "PIX",
    "color": "#00FF00",
    "is_active": true,
    "created_at": "2025-12-29T10:00:00",
    "updated_at": "2025-12-29T10:00:00"
  }
]
```

#### POST `/payment-modalities`
Cria modalidade.

**Requer feature:** `payment_modalities.create`

**Request:**
```json
{
  "name": "PIX",
  "color": "#00FF00"
}
```

#### PUT `/payment-modalities/{modality_id}`
Atualiza modalidade.

**Requer feature:** `payment_modalities.update`

#### DELETE `/payment-modalities/{modality_id}`
Deleta modalidade.

**Requer feature:** `payment_modalities.delete`

#### PATCH `/payment-modalities/{modality_id}/toggle`
Ativa/desativa modalidade.

**Requer feature:** `payment_modalities.toggle`

**Request:**
```json
{
  "activate": false
}
```

---

## 🔐 Sistema de Permissões

### Hierarquia

```
1. Super Admin (is_super_admin = true)
   ├─ Acesso TOTAL ao sistema
   ├─ Bypass automático de features
   ├─ Pode impersonate qualquer empresa
   └─ Acesso ao /admin/*

2. Admin da Empresa (role "Admin")
   ├─ Todas as features da empresa
   ├─ Acesso apenas aos dados da própria empresa
   └─ NÃO pode criar usuários (apenas super admin pode)

3. Usuário Regular
   ├─ Features específicas via roles
   └─ Acesso apenas aos dados da própria empresa
```

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

#### Users (futuro)
- `users.create` - Criar usuários
- `users.read` - Visualizar usuários
- `users.update` - Atualizar usuários
- `users.delete` - Deletar usuários

---

## 📝 Logs de Auditoria

### Ações Registradas

**Críticas (sempre registradas):**
- ✅ `create_company` - Criação de empresa
- ✅ `create_user` - Criação de usuário
- ✅ `activate_user` - Ativação de usuário
- ✅ `deactivate_user` - Desativação de usuário
- ✅ `impersonate_company` - Impersonate de empresa (1h)

**Informativas:**
- ✅ `list_companies` - Listagem de empresas
- ✅ Outras ações conforme necessidade

### Estrutura do Log

```json
{
  "id": "log-uuid",
  "action": "create_company",
  "user_id": "uuid",
  "user_email": "admin@example.com",
  "company_id": "company-uuid",
  "target_type": "company",
  "target_id": "target-uuid",
  "details": {
    "company_name": "Empresa ABC",
    "cnpj": "12.345.678/0001-90"
  },
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "created_at": "2025-12-29T12:00:00"
}
```

### Consultar Logs

```bash
# Todos os logs
GET /api/admin/audit-logs?limit=100

# Por usuário
GET /api/admin/audit-logs?user_id=uuid

# Por empresa
GET /api/admin/audit-logs?company_id=uuid

# Por ação
GET /api/admin/audit-logs?action=create_company

# Por período
GET /api/admin/audit-logs?start_date=2025-12-01&end_date=2025-12-31

# Combinados
GET /api/admin/audit-logs?company_id=uuid&start_date=2025-12-01&limit=50
```

---

## 🏢 Multi-Tenancy

### Como Funciona

1. **Cada empresa tem seu próprio database:**
   ```
   cmp_abc123hash_db  # Empresa ABC
   cmp_xyz789hash_db  # Empresa XYZ
   ```

2. **Token JWT contém `company_id`:**
   ```json
   {
     "user_id": "uuid",
     "company_id": "company-uuid",
     "features": [...]
   }
   ```

3. **Middleware extrai `company_id` do token:**
   ```python
   # De: Authorization: Bearer {token}
   # Para: g.company_id
   ```

4. **Use case usa `company_id` para selecionar database:**
   ```python
   tenant_db = get_tenant_db(g.company_id)
   repository = MongoFinancialEntryRepository(tenant_db["financial_entries"])
   ```

### Garantias de Isolamento

- ✅ Usuário NUNCA pode mudar `company_id` no token (assinado)
- ✅ Cada request usa apenas o database da empresa do usuário
- ✅ Impossível acessar dados de outra empresa
- ✅ Super admin precisa fazer impersonate explícito (registrado em log)

---

## 🎯 Fluxos de Uso

### Fluxo 1: Criar Nova Empresa

```bash
# 1. Super admin faz login
POST /api/auth/login
{
  "email": "teste@teste.com",
  "password": "123456"
}
# ✅ Recebe: super_admin_token

# 2. Criar empresa
POST /api/admin/companies
Authorization: Bearer {super_admin_token}
{
  "name": "Empresa ABC Ltda",
  "cnpj": "12.345.678/0001-90",
  "phone": "(11) 98765-4321",
  "plan": "premium"
}
# ✅ Recebe: company_id
# ✅ Cria database cmp_{hash}_db
# ✅ Registra log de auditoria

# 3. Criar primeiro usuário da empresa
POST /api/admin/users
Authorization: Bearer {super_admin_token}
{
  "email": "admin@empresaabc.com",
  "password": "senha123",
  "name": "João Silva - Admin",
  "company_id": "company-uuid-do-passo-2",
  "is_super_admin": false
}
# ✅ Recebe: user criado
# ✅ Registra log de auditoria

# 4. Usuário faz login e começa a usar
POST /api/auth/login
{
  "email": "admin@empresaabc.com",
  "password": "senha123"
}
# ✅ Recebe: token com company_id
```

### Fluxo 2: Super Admin Fazendo Suporte (Impersonate)

```bash
# 1. Cliente reporta problema no dashboard
# 2. Super admin faz login
POST /api/auth/login
{"email": "teste@teste.com", "password": "123456"}

# 3. Super admin impersona empresa do cliente
POST /api/admin/impersonate/company-uuid-do-cliente
Authorization: Bearer {super_admin_token}
# ✅ Recebe: impersonate_token (1h)
# ✅ Registra log de auditoria CRÍTICO

# 4. Super admin usa token para ver dados do cliente
GET /api/financial-entries
Authorization: Bearer {impersonate_token}
# ✅ Vê exatamente o que o cliente vê

# 5. Identifica e resolve problema
# 6. Token expira em 1h (segurança)
```

### Fluxo 3: Usuário Normal Operando

```bash
# 1. Login
POST /api/auth/login
{"email": "usuario@empresa.com", "password": "senha123"}
# ✅ Recebe: token (company_id dentro)

# 2. Listar modalidades
GET /api/payment-modalities
Authorization: Bearer {token}
# ✅ Retorna apenas modalidades da própria empresa

# 3. Criar lançamento
POST /api/financial-entries
Authorization: Bearer {token}
{
  "value": 1500.00,
  "date": "2025-12-29",
  "modality_id": "modality-uuid"
}
# ✅ Salvo no database da própria empresa
# ✅ Impossível criar em outra empresa

# 4. Listar lançamentos
GET /api/financial-entries?start_date=2025-12-01&end_date=2025-12-31
Authorization: Bearer {token}
# ✅ Retorna apenas lançamentos da própria empresa
```

---

## 💻 Para o Frontend

### Informações Essenciais

#### 1. Autenticação

**Fazer Login:**
```javascript
const response = await fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'usuario@empresa.com',
    password: 'senha123'
  })
});

const { token, refresh_token, user } = await response.json();

// Salvar no localStorage ou cookie
localStorage.setItem('access_token', token);
localStorage.setItem('refresh_token', refresh_token);
localStorage.setItem('user', JSON.stringify(user));
```

**Usar Token:**
```javascript
const response = await fetch('http://localhost:5000/api/financial-entries', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json'
  }
});
```

**Renovar Token (quando expirar):**
```javascript
const response = await fetch('http://localhost:5000/api/auth/refresh', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    refresh_token: localStorage.getItem('refresh_token')
  })
});

const { token, refresh_token } = await response.json();
localStorage.setItem('access_token', token);
localStorage.setItem('refresh_token', refresh_token);
```

#### 2. Verificar Permissões

```javascript
const user = JSON.parse(localStorage.getItem('user'));

// É super admin?
if (user.is_super_admin) {
  // Mostrar menu /admin
}

// Tem permissão para criar lançamentos?
if (user.features.includes('financial_entries.create')) {
  // Mostrar botão "Novo Lançamento"
}

// Tem permissão para deletar modalidades?
if (user.features.includes('payment_modalities.delete')) {
  // Mostrar botão "Deletar"
}
```

#### 3. Tratamento de Erros

```javascript
const response = await fetch(...);

if (response.status === 401) {
  // Token expirado - tentar renovar
  await refreshToken();
  // Tentar request novamente
}

if (response.status === 403) {
  // Sem permissão
  alert('Você não tem permissão para esta ação');
}

if (response.status === 404) {
  // Não encontrado
  alert('Recurso não encontrado');
}

if (response.status === 400) {
  // Erro de validação
  const { error } = await response.json();
  alert(error);
}
```

#### 4. Estrutura de Páginas Sugerida

```
Frontend/
├── /login                    # Login público
├── /dashboard                # Dashboard do usuário
│   ├── /financial-entries    # Lançamentos financeiros
│   ├── /payment-modalities   # Modalidades de pagamento
│   └── /profile              # Perfil do usuário
│
└── /admin (is_super_admin)   # Apenas super admin
    ├── /dashboard            # Dashboard administrativo
    ├── /companies            # Gerenciar empresas
    ├── /users                # Gerenciar usuários
    └── /audit-logs           # Logs de auditoria
```

#### 5. Endpoints por Funcionalidade

**Dashboard do Usuário:**
- `GET /api/financial-entries` - Listar lançamentos
- `POST /api/financial-entries` - Criar lançamento
- `PUT /api/financial-entries/{id}` - Editar lançamento
- `DELETE /api/financial-entries/{id}` - Deletar lançamento
- `GET /api/payment-modalities` - Listar modalidades
- `POST /api/payment-modalities` - Criar modalidade
- `PUT /api/payment-modalities/{id}` - Editar modalidade
- `DELETE /api/payment-modalities/{id}` - Deletar modalidade
- `PATCH /api/payment-modalities/{id}/toggle` - Ativar/desativar

**Dashboard Admin (is_super_admin):**
- `GET /api/admin/dashboard` - Estatísticas
- `GET /api/admin/companies` - Listar empresas
- `POST /api/admin/companies` - Criar empresa
- `GET /api/admin/companies/{id}` - Detalhes da empresa
- `POST /api/admin/impersonate/{company_id}` - Impersonate (1h)
- `GET /api/admin/users` - Listar usuários
- `POST /api/admin/users` - Criar usuário
- `PATCH /api/admin/users/{id}/toggle-active` - Ativar/desativar usuário
- `GET /api/admin/audit-logs` - Logs de auditoria

#### 6. Formatos de Data

**Envio (POST/PUT):**
```javascript
// Date: YYYY-MM-DD
{
  "date": "2025-12-29"
}
```

**Resposta (GET):**
```javascript
// ISO 8601
{
  "created_at": "2025-12-29T10:30:00"
}

// Converter para exibição
const date = new Date(entry.created_at);
console.log(date.toLocaleDateString('pt-BR'));
```

#### 7. Cores das Modalidades

```javascript
// Retorno da API
{
  "color": "#00FF00"
}

// Usar no frontend
<div style={{ backgroundColor: modality.color }}>
  {modality.name}
</div>
```

#### 8. Exemplo Completo React

```jsx
import { useState, useEffect } from 'react';

function FinancialEntries() {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEntries();
  }, []);

  async function fetchEntries() {
    try {
      const response = await fetch('http://localhost:5000/api/financial-entries', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setEntries(data);
      } else if (response.status === 401) {
        // Token expirado - redirecionar para login
        window.location.href = '/login';
      }
    } catch (error) {
      console.error('Erro ao buscar lançamentos:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div>Carregando...</div>;

  return (
    <div>
      <h1>Lançamentos Financeiros</h1>
      {entries.map(entry => (
        <div key={entry.id}>
          <span>{entry.date}</span>
          <span>R$ {entry.value.toFixed(2)}</span>
          <span style={{ color: entry.modality_color }}>
            {entry.modality_name}
          </span>
        </div>
      ))}
    </div>
  );
}
```

---

## 🔒 Segurança

### Checklist de Produção

- [ ] Mudar `JWT_SECRET` para valor aleatório e seguro
- [ ] Configurar `ENVIRONMENT=production` no `.env`
- [ ] Usar HTTPS (não HTTP)
- [ ] Configurar CORS corretamente
- [ ] Adicionar rate limiting
- [ ] Desabilitar `debug=True` em produção
- [ ] Fazer backup regular do MongoDB
- [ ] Monitorar logs de auditoria
- [ ] Validar entrada do usuário
- [ ] Usar senha forte para super admin

---

## 📚 Documentação Adicional

- **[API_COMPLETA.md](API_COMPLETA.md)** - Documentação completa de todos os endpoints
- **[VALIDACAO_API.md](VALIDACAO_API.md)** - Análise técnica e validação do sistema
- **[FLUXO_CORRETO.md](FLUXO_CORRETO.md)** - Fluxos detalhados de uso

---

## 🐛 Troubleshooting

### MongoDB não conecta

```bash
# Verificar se está rodando
mongosh

# Se não estiver, iniciar
brew services start mongodb-community  # macOS
sudo systemctl start mongodb  # Linux
```

### Token expirado

```bash
# Use o refresh token
POST /api/auth/refresh
{
  "refresh_token": "..."
}
```

### Erro 403 (Forbidden)

- Verificar se usuário tem `is_super_admin = true` (para rotas `/admin/*`)
- Verificar se usuário tem feature necessária
- Verificar se token é válido

### Erro 401 (Unauthorized)

- Token não foi enviado
- Token está expirado
- Token é inválido

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs de auditoria: `GET /api/admin/audit-logs`
2. Verificar console do backend
3. Verificar MongoDB está rodando
4. Verificar variáveis de ambiente `.env`

---

## ✅ Status do Sistema

**Backend:** ✅ Completo e Funcional

**Implementado:**
- ✅ Multi-tenancy com databases isolados
- ✅ Autenticação JWT + Refresh Token
- ✅ Sistema RBAC com features
- ✅ Logs de auditoria completos
- ✅ Endpoints administrativos
- ✅ Impersonate de 1h
- ✅ CRUD de empresas, usuários, lançamentos e modalidades
- ✅ Clean Architecture + SOLID

**Pronto para desenvolvimento do Frontend!** 🚀

---

**Versão:** 2.0.0
**Última atualização:** 2025-12-29
**Arquitetura:** Clean Architecture + SOLID
**Status:** ✅ Produção Ready
