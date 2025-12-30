# 🏢 Empresa Administrativa

## 📋 Visão Geral

A **Empresa Administrativa** é uma empresa especial no sistema que serve para segregar usuários administrativos (super admins) dos usuários clientes das empresas.

## ⭐ Características

### 1. Isolamento de Super Admins

- **Super admins** são vinculados à empresa administrativa
- Empresas clientes não têm acesso aos super admins
- Super admins não "poluem" a listagem de usuários das empresas clientes

### 2. Invisível na Listagem

- Tem flag `is_admin_company=True`
- **NÃO aparece** em `GET /admin/companies`
- Apenas acessível por busca direta (CNPJ ou ID)

### 3. Database Isolado

- Tem seu próprio database: `cmp_{hash}_db`
- Contém apenas:
  - Collection `roles` com a role "Super Admin"
- **NÃO tem:**
  - `financial_entries`
  - `payment_modalities`

## 🚀 Como Inicializar

### Script de Inicialização

```bash
python scripts/init_admin_company.py
```

### O que o Script Faz

1. ✅ Cria empresa "Administração do Sistema"
   - CNPJ: `00.000.000/0000-00`
   - Plan: `system`
   - `is_admin_company=True`

2. ✅ Cria database isolado para a empresa
   - Nome: `cmp_{hash8}_db`
   - Collection: `roles`

3. ✅ Cria role "Super Admin"
   - Todas as features do sistema
   - `company_id` = empresa administrativa

4. ✅ Cria super admin
   - Email: `admin@sistema.com`
   - Senha: `admin123`
   - `is_super_admin=True`
   - `company_id` = empresa administrativa

## 📊 Estrutura no MongoDB

```
shared_db
├── companies
│   ├── {empresa_administrativa}  ← is_admin_company=true
│   ├── {empresa_1}
│   └── {empresa_2}
│
└── users
    ├── {super_admin}  ← company_id = empresa_administrativa
    ├── {user_empresa_1}
    └── {user_empresa_2}

cmp_{hash_admin}_db (Empresa Administrativa)
└── roles
    └── {super_admin_role}

cmp_{hash1}_db (Empresa Cliente 1)
├── financial_entries
├── payment_modalities
└── roles

cmp_{hash2}_db (Empresa Cliente 2)
├── financial_entries
├── payment_modalities
└── roles
```

## 🔍 Como Identificar

### Via Código

```python
from src.database import get_shared_db
from src.infra.repositories import MongoCompanyRepository

shared_db = get_shared_db()
company_repo = MongoCompanyRepository(shared_db["companies"])

# Buscar empresa administrativa
admin_company = company_repo.find_by_cnpj("00.000.000/0000-00")
print(admin_company.is_admin_company)  # True

# Listar empresas clientes (exclui administrativa)
companies = company_repo.find_all()  # Não retorna a administrativa
```

### Via MongoDB Compass

Filtro na collection `companies`:

```json
{
  "is_admin_company": true
}
```

## 🔐 Credenciais Padrão

**⚠️ ATENÇÃO: Trocar em produção!**

```
Email: admin@sistema.com
Senha: admin123
```

## 🎯 Por Que Existe?

### Problema Anterior

- Super admin estava vinculado a uma empresa cliente qualquer
- Não havia separação clara entre administração e clientes
- Confusão sobre qual empresa o super admin "pertencia"

### Solução Atual

- Super admin tem sua própria "empresa"
- Separação clara: empresa administrativa vs empresas clientes
- Listagem de empresas mostra apenas empresas clientes
- Super admin pode criar empresas e usuários sem estar atrelado a nenhuma empresa cliente

## 📝 Campos da Entidade Company

```python
@dataclass
class Company:
    name: str
    cnpj: str
    phone: str
    plan: str = "basic"
    is_active: bool = True
    is_admin_company: bool = False  # ← Novo campo
    settings: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

## 🔄 Impacto nos Endpoints

### `GET /admin/companies`

**Antes:**
```json
[
  {"id": "xxx", "name": "Empresa Teste", "is_admin_company": false},
  {"id": "yyy", "name": "Administração do Sistema", "is_admin_company": true}
]
```

**Depois:**
```json
[
  {"id": "xxx", "name": "Empresa Teste", "is_admin_company": false}
]
```

A empresa administrativa **não aparece** mais na listagem.

### `GET /admin/companies/{id}` ou `/admin/companies/cnpj/{cnpj}`

Continuam funcionando normalmente. Você pode buscar a empresa administrativa diretamente se souber o ID ou CNPJ.

## 🧪 Testes

### 1. Verificar que Empresa Administrativa Existe

```bash
python3 -c "
from src.database import MongoConnection, get_shared_db
from src.infra.repositories import MongoCompanyRepository

MongoConnection()
shared_db = get_shared_db()
company_repo = MongoCompanyRepository(shared_db['companies'])

admin_company = company_repo.find_by_cnpj('00.000.000/0000-00')
print(f'Empresa: {admin_company.name}')
print(f'is_admin_company: {admin_company.is_admin_company}')
"
```

### 2. Verificar que Não Aparece na Listagem

```bash
python3 -c "
from src.database import MongoConnection, get_shared_db
from src.infra.repositories import MongoCompanyRepository

MongoConnection()
shared_db = get_shared_db()
company_repo = MongoCompanyRepository(shared_db['companies'])

companies = company_repo.find_all()
admin_companies = [c for c in companies if c.is_admin_company]
print(f'Empresas administrativas na listagem: {len(admin_companies)}')  # Deve ser 0
"
```

### 3. Verificar Super Admin Vinculado

```bash
python3 -c "
from src.database import MongoConnection, get_shared_db
from src.infra.repositories import MongoUserRepository, MongoCompanyRepository

MongoConnection()
shared_db = get_shared_db()
user_repo = MongoUserRepository(shared_db['users'])
company_repo = MongoCompanyRepository(shared_db['companies'])

super_admin = user_repo.find_by_email('admin@sistema.com')
company = company_repo.find_by_id(super_admin.company_id)
print(f'Super admin: {super_admin.email}')
print(f'Empresa: {company.name}')
print(f'is_admin_company: {company.is_admin_company}')
"
```

## ✅ Checklist de Implementação

- [x] Adicionar campo `is_admin_company` em `Company` entity
- [x] Atualizar `to_dict()` em `Company`
- [x] Atualizar `_doc_to_entity()` em `MongoCompanyRepository`
- [x] Filtrar empresas administrativas em `find_all()`
- [x] Criar script `init_admin_company.py`
- [x] Atualizar README.md com documentação
- [x] Testar inicialização
- [x] Testar listagem (deve excluir administrativa)
- [x] Testar busca direta (deve funcionar)

## 🎉 Resultado Final

✅ **Super admin** agora está em uma empresa separada e exclusiva para administração

✅ **Listagem de empresas** mostra apenas empresas clientes

✅ **Segregação clara** entre administração e clientes

✅ **Melhor organização** do sistema multi-tenant
