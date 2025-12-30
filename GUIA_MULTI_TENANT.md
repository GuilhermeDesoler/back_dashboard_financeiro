# 🚀 Guia de Uso - Dashboard Financeiro Multi-Tenant

## 📚 Visão Geral

O sistema agora suporta **multi-tenancy completo** com isolamento de dados por empresa usando **banco de dados separado por tenant**.

### Arquitetura de Banco de Dados

```
MongoDB
├── shared_db (Dados Globais)
│   ├── companies          # Todas as empresas
│   ├── users              # Todos os usuários
│   └── features           # Features do sistema
│
├── company_{id}_db (Empresa 1)
│   ├── financial_entries  # Lançamentos da empresa
│   ├── payment_modalities # Modalidades da empresa
│   └── roles              # Roles da empresa
│
└── company_{id}_db (Empresa 2)
    ├── financial_entries
    ├── payment_modalities
    └── roles
```

---

## 🔧 Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Crie/atualize o arquivo `.env`:

```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DATABASE=shared_db
JWT_SECRET=sua-chave-secreta-super-segura-aqui
```

**IMPORTANTE**: Mude `JWT_SECRET` para uma chave forte em produção!

### 3. Iniciar o Servidor

```bash
python src/app.py
```

---

## 🎯 Fluxo de Uso

### Passo 1: Registrar uma Nova Empresa e Usuário

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

**Response:**
```json
{
  "message": "Usuário registrado com sucesso",
  "user": {
    "id": "user-uuid",
    "email": "admin@empresa.com",
    "name": "Administrador",
    "company_id": "company-uuid",
    "role_ids": [],
    "is_active": true
  }
}
```

🔹 **O que acontece:**
- Cria a empresa no `shared_db`
- Cria o usuário no `shared_db`
- **Cria automaticamente** o banco `company_{id}_db` com índices

---

### Passo 2: Fazer Login

```bash
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "email": "admin@empresa.com",
  "password": "senha123"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": "user-uuid",
    "email": "admin@empresa.com",
    "name": "Administrador",
    "company_id": "company-uuid",
    "roles": [],
    "features": []
  }
}
```

🔹 **Guarde o `token`** - será usado em todas as próximas requisições!

---

### Passo 3: Acessar Recursos (Autenticado)

Todas as requisições agora precisam do header:

```
Authorization: Bearer {seu_token}
```

#### Criar Modalidade de Pagamento

```bash
POST http://localhost:5000/api/payment-modalities
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "name": "PIX",
  "color": "#00FF00"
}
```

🔒 **Dados salvos no DB da empresa** (`company_{id}_db.payment_modalities`)

#### Criar Lançamento Financeiro

```bash
POST http://localhost:5000/api/financial-entries
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
Content-Type: application/json

{
  "value": 1500.00,
  "date": "2025-12-29",
  "modality_id": "modality-uuid"
}
```

🔒 **Dados salvos no DB da empresa** (`company_{id}_db.financial_entries`)

#### Listar Lançamentos

```bash
GET http://localhost:5000/api/financial-entries?start_date=2025-12-01&end_date=2025-12-31
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

🔒 **Retorna APENAS dados da empresa do usuário autenticado**

---

## 🔐 Segurança

### Isolamento Total de Dados

✅ Cada empresa tem seu **próprio banco de dados**
✅ Impossível acessar dados de outra empresa
✅ Token JWT com `company_id` embutido
✅ Middleware valida autenticação em todas as rotas protegidas
✅ Senhas hash com bcrypt

### Sistema de Features (RBAC)

O sistema suporta controle de acesso baseado em features:

```
financial_entries.create
financial_entries.read
financial_entries.update
financial_entries.delete

payment_modalities.create
payment_modalities.read
payment_modalities.update
payment_modalities.delete
payment_modalities.toggle
```

---

## 📖 Endpoints Disponíveis

### Autenticação (Públicos)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/register` | Registrar empresa e usuário |
| POST | `/api/auth/login` | Fazer login |
| POST | `/api/auth/refresh` | Renovar token |
| GET | `/api/auth/me` | Dados do usuário logado (requer auth) |

### Modalidades de Pagamento (Protegidos)

| Método | Endpoint | Feature Requerida |
|--------|----------|-------------------|
| POST | `/api/payment-modalities` | `payment_modalities.create` |
| GET | `/api/payment-modalities` | `payment_modalities.read` |
| PUT | `/api/payment-modalities/<id>` | `payment_modalities.update` |
| DELETE | `/api/payment-modalities/<id>` | `payment_modalities.delete` |
| PATCH | `/api/payment-modalities/<id>/toggle` | `payment_modalities.toggle` |

### Lançamentos Financeiros (Protegidos)

| Método | Endpoint | Feature Requerida |
|--------|----------|-------------------|
| POST | `/api/financial-entries` | `financial_entries.create` |
| GET | `/api/financial-entries` | `financial_entries.read` |
| PUT | `/api/financial-entries/<id>` | `financial_entries.update` |
| DELETE | `/api/financial-entries/<id>` | `financial_entries.delete` |

---

## 🧪 Testando

### 1. Verificar API

```bash
curl http://localhost:5000/
```

### 2. Registrar

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@empresa.com",
    "password": "senha123",
    "name": "Teste",
    "company_name": "Empresa Teste",
    "cnpj": "11.222.333/0001-44"
  }'
```

### 3. Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@empresa.com",
    "password": "senha123"
  }'
```

### 4. Usar Token

```bash
TOKEN="seu_token_aqui"

curl http://localhost:5000/api/payment-modalities \
  -H "Authorization: Bearer $TOKEN"
```

---

## ⚠️ Notas Importantes

1. **Migração de Dados Antigos**: Dados existentes no banco antigo precisarão ser migrados para o novo formato
2. **JWT_SECRET**: SEMPRE mude em produção!
3. **HTTPS**: Use HTTPS em produção (nunca HTTP para tokens)
4. **Backup**: Faça backup regular dos bancos de dados
5. **Features**: Implemente sistema de roles/features conforme necessário

---

## 🚀 Próximos Passos

1. Implementar sistema de roles completo
2. Adicionar mais features granulares
3. Criar painel administrativo
4. Implementar auditoria de ações
5. Adicionar rate limiting

---

## 📞 Suporte

Sistema implementado com:
- ✅ Multi-tenancy por Database
- ✅ Autenticação JWT
- ✅ RBAC (Role-Based Access Control)
- ✅ Segurança bcrypt
- ✅ Isolamento total de dados

**Arquitetura Clean Architecture mantida!** 🎯
