# Scripts de Seed

## Reset e Seed Completo

Script para resetar TUDO no banco de dados e popular com dados de teste limpos.

### Executar

```bash
# Com confirmação interativa
python scripts/reset_and_seed.py

# Auto-confirma a deleção (recomendado para desenvolvimento)
python scripts/reset_and_seed.py --yes
```

### O que o script faz

1. **Deleta TODOS os bancos de dados** (exceto admin, config, local)
2. **Cria 33 features** do sistema
3. **Cria 1 empresa de teste**: Empresa Teste Ltda
4. **Cria 1 role Admin** com todas as features
5. **Cria 3 usuários de teste**:

#### Usuários Criados

| Email | Senha | Nome | Empresa | Role | Super Admin |
|-------|-------|------|---------|------|-------------|
| super@teste.com | 123456 | Super Admin | - | - | ✅ SIM |
| admin@teste.com | 123456 | Admin da Empresa | Empresa Teste Ltda | Admin | ❌ NÃO |
| usuario@teste.com | 123456 | Usuário Comum | Empresa Teste Ltda | - | ❌ NÃO |

#### Detalhes dos Usuários

**1. Super Admin** (`super@teste.com`)
- **NÃO vinculado a nenhuma empresa** (company_id = None)
- Sem roles específicas
- Acesso global ao sistema
- Pode acessar qualquer empresa

**2. Admin** (`admin@teste.com`)
- Vinculado à "Empresa Teste Ltda"
- Role: Admin (com todas as 33 features)
- Acesso total à empresa
- Não pode acessar outras empresas

**3. Usuário Comum** (`usuario@teste.com`)
- Vinculado à "Empresa Teste Ltda"
- **SEM role** (role_ids = [])
- Acesso limitado (depende das validações de permissão)
- Não pode acessar outras empresas

### Database Criado

O script cria um banco de dados para a empresa com **nome legível**:

```
company_empresa_teste_ltda
```

Ao invés de usar hash (`cmp_4e0d4a9c_db`), agora os databases usam o nome sanitizado da empresa, facilitando a identificação no MongoDB.

### Collections Criadas

**Shared DB** (`shared_db`):
- `companies` - 1 empresa
- `users` - 3 usuários
- `features` - 33 features

**Tenant DB** (`company_empresa_teste_ltda`):
- `roles` - 1 role (Admin)
- `payment_modalities` - vazio
- `financial_entries` - vazio
- `installments` - vazio
- `bank_limits` - vazio
- `platform_settings` - vazio

### Testar Login

```bash
# 1. Iniciar o backend
python src/app.py

# 2. Fazer login com qualquer usuário
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@teste.com",
    "password": "123456"
  }'
```

### ATENÇÃO

⚠️ **Este script DELETA TODOS os dados existentes!**
- Use apenas em ambiente de desenvolvimento
- Nunca execute em produção
- Todos os dados serão perdidos
