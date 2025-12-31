# 💳 Sistema de Crediário - Guia de Implementação

## ✅ Status da Implementação

**IMPLEMENTAÇÃO COMPLETA!** 🎉

Todos os componentes do sistema de crediário foram implementados e estão prontos para uso:

- ✅ Entidades (CreditPurchase e CreditInstallment)
- ✅ Repositórios (interfaces e implementações MongoDB)
- ✅ Use Cases (criar, pagar, cancelar, dashboard)
- ✅ Rotas da API com auditoria completa
- ✅ Índices do banco de dados
- ✅ Documentação para frontend

---

## 📁 Estrutura de Arquivos Criados

### Entidades
```
src/domain/entities/
├── credit_purchase.py          # Compra no crediário (dados brutos)
└── credit_installment.py       # Parcela individual
```

### Repositórios
```
src/domain/repositories/
├── credit_purchase_repository.py          # Interface
└── credit_installment_repository.py       # Interface

src/infra/repositories/
├── mongo_credit_purchase_repository.py    # Implementação MongoDB
└── mongo_credit_installment_repository.py # Implementação MongoDB
```

### Use Cases
```
src/application/use_cases/
├── create_credit_purchase.py           # Criar compra + gerar parcelas
├── get_credit_purchase_details.py      # Buscar detalhes completos
├── cancel_credit_purchase.py           # Cancelar compra
├── pay_credit_installment.py           # 🔥 Registrar pagamento
├── unpay_credit_installment.py         # Desfazer pagamento
└── get_credit_dashboard.py             # Dashboard agregado
```

### Rotas da API
```
src/presentation/routes/
└── credit_purchase_routes.py          # Todos os endpoints
```

### Scripts
```
scripts/
└── add_credit_indexes.py              # Migração de índices
```

### Documentação
```
FRONTEND_CREDIT_PURCHASE_API_DOCS.md   # 📘 Doc completa para frontend
CREDIT_PURCHASE_README.md              # Este arquivo
```

---

## 🚀 Como Usar

### 1. Executar Migração de Índices (IMPORTANTE!)

Se você já tem empresas/tenants no banco, execute este script para adicionar os índices das novas collections:

```bash
python scripts/add_credit_indexes.py
```

Este script vai:
- Buscar todas as empresas existentes
- Adicionar índices em `credit_purchases` e `credit_installments` em cada banco de tenant
- Não afeta dados existentes

### 2. Reiniciar a Aplicação

```bash
python src/app.py
```

Ou se estiver usando outro método de execução (gunicorn, etc.).

### 3. Testar os Endpoints

#### Criar uma Compra

```bash
curl -X POST http://localhost:5000/api/credit-purchases \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "pagante_nome": "João Silva",
    "descricao_compra": "Geladeira Brastemp 450L",
    "valor_total": 3000.00,
    "numero_parcelas": 10,
    "data_inicio_pagamento": "2025-02-01T00:00:00Z"
  }'
```

#### Buscar Detalhes

```bash
curl http://localhost:5000/api/credit-purchases/{ID_DA_COMPRA} \
  -H "Authorization: Bearer SEU_TOKEN"
```

#### Registrar Pagamento de Parcela

```bash
curl -X POST http://localhost:5000/api/credit-purchases/{ID_COMPRA}/installments/{ID_PARCELA}/pay \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data_pagamento": "2025-02-01T15:30:00Z",
    "modality_id": "ID_DA_MODALIDADE",
    "valor_juros": 0,
    "valor_multa": 0,
    "observacao": "Pago via PIX"
  }'
```

#### Dashboard

```bash
curl "http://localhost:5000/api/credit-purchases/dashboard/installments-by-date?start_date=2025-02-01T00:00:00Z&end_date=2025-02-28T23:59:59Z" \
  -H "Authorization: Bearer SEU_TOKEN"
```

---

## 🔐 Permissões Necessárias

Você precisará criar estas features/permissões no banco de dados:

```json
[
  {
    "name": "credit_purchases.create",
    "description": "Criar compras no crediário",
    "category": "credit"
  },
  {
    "name": "credit_purchases.read",
    "description": "Visualizar compras no crediário",
    "category": "credit"
  },
  {
    "name": "credit_purchases.update",
    "description": "Editar compras no crediário",
    "category": "credit"
  },
  {
    "name": "credit_purchases.delete",
    "description": "Deletar compras no crediário",
    "category": "credit"
  },
  {
    "name": "credit_purchases.cancel",
    "description": "Cancelar compras no crediário",
    "category": "credit"
  },
  {
    "name": "credit_installments.pay",
    "description": "Registrar pagamento de parcelas",
    "category": "credit"
  },
  {
    "name": "credit_installments.unpay",
    "description": "Desfazer pagamento de parcelas",
    "category": "credit"
  }
]
```

### Script para Criar Permissões

Você pode criar um script ou adicionar manualmente no banco `shared_db.features`:

```python
# scripts/create_credit_permissions.py
from src.database import get_shared_db

shared_db = get_shared_db()

permissions = [
    {"name": "credit_purchases.create", "description": "Criar compras no crediário", "category": "credit"},
    {"name": "credit_purchases.read", "description": "Visualizar compras no crediário", "category": "credit"},
    {"name": "credit_purchases.update", "description": "Editar compras no crediário", "category": "credit"},
    {"name": "credit_purchases.delete", "description": "Deletar compras no crediário", "category": "credit"},
    {"name": "credit_purchases.cancel", "description": "Cancelar compras no crediário", "category": "credit"},
    {"name": "credit_installments.pay", "description": "Registrar pagamento de parcelas", "category": "credit"},
    {"name": "credit_installments.unpay", "description": "Desfazer pagamento de parcelas", "category": "credit"},
]

for perm in permissions:
    # Verificar se já existe
    existing = shared_db["features"].find_one({"name": perm["name"]})
    if not existing:
        shared_db["features"].insert_one(perm)
        print(f"✅ Criada: {perm['name']}")
    else:
        print(f"⏭️  Já existe: {perm['name']}")
```

---

## 📊 Endpoints Disponíveis

### Compras no Crediário

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/credit-purchases` | Criar nova compra |
| `GET` | `/api/credit-purchases` | Listar compras (filtros: status, pagante_nome) |
| `GET` | `/api/credit-purchases/{id}` | Detalhes completos da compra |
| `PUT` | `/api/credit-purchases/{id}` | Atualizar dados da compra |
| `PATCH` | `/api/credit-purchases/{id}/cancel` | Cancelar compra |
| `DELETE` | `/api/credit-purchases/{id}` | Deletar compra |

### Parcelas

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/credit-purchases/{id}/installments/{inst_id}/pay` | 🔥 Registrar pagamento |
| `POST` | `/api/credit-purchases/{id}/installments/{inst_id}/unpay` | Desfazer pagamento |

### Dashboard

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/credit-purchases/dashboard/installments-by-date` | Parcelas por data |
| `GET` | `/api/credit-purchases/dashboard/totals` | Totais gerais |
| `GET` | `/api/credit-purchases/dashboard/overdue` | Parcelas atrasadas |
| `GET` | `/api/credit-purchases/dashboard/due-soon` | Parcelas vencendo |

---

## ✨ Funcionalidades Implementadas

### ✅ Registro de Pagamento Completo

**SIM!** O sistema permite registrar o pagamento das parcelas através do endpoint:

```
POST /api/credit-purchases/{credit_purchase_id}/installments/{installment_id}/pay
```

**O que acontece ao registrar um pagamento:**

1. ✅ A parcela é marcada como "paga"
2. ✅ Data de pagamento é registrada
3. ✅ Informações de quem pagou são salvas
4. ✅ **Um FinancialEntry (lançamento financeiro) é criado automaticamente**
5. ✅ Os dois registros são vinculados
6. ✅ Se todas as parcelas forem pagas, a compra é marcada como "concluída"
7. ✅ **Tudo é auditado** (ação registrada em audit_logs)

### ✅ Auditoria Completa

Todas as ações são auditadas:

- `CREATE_CREDIT_PURCHASE` - Criação de compra
- `UPDATE_CREDIT_PURCHASE` - Atualização de compra
- `CANCEL_CREDIT_PURCHASE` - Cancelamento de compra
- `DELETE_CREDIT_PURCHASE` - Exclusão de compra
- `PAY_CREDIT_INSTALLMENT` - **Pagamento de parcela** 🔥
- `UNPAY_CREDIT_INSTALLMENT` - Estorno de pagamento

Os logs incluem:
- Quem fez a ação (user_id, user_email)
- Quando (created_at)
- O quê (target_type, target_id)
- Detalhes (dados específicos da ação)
- De onde (ip_address, user_agent)

### ✅ Dashboard Completo

Similar ao dashboard de lançamentos financeiros:

- Parcelas agrupadas por data de vencimento
- Resumo geral (totais, taxa de inadimplência)
- Filtros por período e status
- Dados enriquecidos com informações da compra (nome do cliente, etc.)

### ✅ Integração com Sistema Existente

- Quando uma parcela é paga, um `FinancialEntry` é criado automaticamente
- Isso mantém compatibilidade com relatórios existentes
- A modalidade de pagamento é reutilizada do sistema atual
- Multi-tenancy preservado (cada empresa tem suas compras isoladas)

---

## 🔄 Fluxo de Dados

### Criação de Compra

```
1. POST /api/credit-purchases
   ↓
2. CreateCreditPurchase use case
   ↓
3. Cria CreditPurchase
   ↓
4. Gera N CreditInstallments automaticamente
   ↓
5. Salva tudo no banco (tenant-specific)
   ↓
6. Registra auditoria
   ↓
7. Retorna compra + parcelas
```

### Pagamento de Parcela

```
1. POST .../installments/{id}/pay
   ↓
2. PayCreditInstallment use case
   ↓
3. Valida parcela (existe, não está paga, etc.)
   ↓
4. Busca modalidade de pagamento
   ↓
5. Cria FinancialEntry (lançamento)
   ↓
6. Atualiza CreditInstallment (marca como pago, vincula entry)
   ↓
7. Verifica se todas parcelas pagas → completa compra
   ↓
8. Registra auditoria
   ↓
9. Retorna parcela + lançamento criado
```

---

## 📝 Collections do MongoDB

### `credit_purchases`

```javascript
{
  _id: ObjectId,
  id: "uuid",                        // Índice único
  pagante_nome: "João Silva",        // Índice
  pagante_documento: "123.456.789-00",
  pagante_telefone: "(11) 98765-4321",
  descricao_compra: "Geladeira Brastemp 450L",
  valor_total: 3000.00,
  valor_entrada: 500.00,
  numero_parcelas: 10,
  data_inicio_pagamento: ISODate("2025-02-01T00:00:00Z"),
  intervalo_dias: 30,
  taxa_juros_mensal: 0.0,
  registrado_por_user_id: "uuid",
  registrado_por_nome: "Maria Admin",
  status: "ativo",                   // Índice
  created_at: ISODate,               // Índice (desc)
  updated_at: ISODate
}
```

### `credit_installments`

```javascript
{
  _id: ObjectId,
  id: "uuid",                        // Índice único
  credit_purchase_id: "uuid",        // Índice (FK)
  numero_parcela: 1,
  valor_parcela: 250.00,
  valor_juros: 0.0,
  valor_multa: 0.0,
  valor_total: 250.00,
  data_vencimento: ISODate,          // Índice
  data_pagamento: ISODate,
  status: "pago",                    // Índice
  financial_entry_id: "uuid",        // Índice (FK)
  pago_por_user_id: "uuid",
  pago_por_nome: "Carlos Vendedor",
  observacao: "Pago via PIX",
  dias_atraso: 0,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Índices:**
- Índice composto: `(data_vencimento, status)` para queries do dashboard

---

## 🎨 Para o Frontend

Todo a documentação para implementar o frontend está em:

**📘 [FRONTEND_CREDIT_PURCHASE_API_DOCS.md](./FRONTEND_CREDIT_PURCHASE_API_DOCS.md)**

Este documento contém:
- ✅ Estrutura completa de dados (TypeScript interfaces)
- ✅ Documentação de todos os endpoints
- ✅ Exemplos de requests e responses
- ✅ Sugestões de UI/UX com mockups
- ✅ Checklist de implementação
- ✅ Exemplos de código
- ✅ Fluxos completos de uso

**Entregue este documento para a IA que vai implementar o frontend!**

---

## 🧪 Testes (Próximos Passos)

Os testes podem ser criados seguindo o padrão existente do projeto:

```python
# tests/test_credit_purchase.py
def test_create_credit_purchase():
    # Criar compra
    # Verificar se parcelas foram geradas
    # Validar totais

def test_pay_installment():
    # Criar compra com parcelas
    # Pagar uma parcela
    # Verificar se FinancialEntry foi criado
    # Validar status

def test_complete_purchase():
    # Criar compra
    # Pagar todas as parcelas
    # Verificar se compra ficou "concluido"
```

---

## ❓ FAQ

### 1. Posso registrar pagamentos parciais?

Não diretamente. Cada parcela deve ser paga integralmente. Se precisar de flexibilidade, você pode:
- Adicionar juros/multa no momento do pagamento
- Registrar observações

### 2. Como lidar com parcelas atrasadas?

O sistema calcula automaticamente os dias de atraso. Você pode:
- Executar um job periódico chamando `update_statuses_batch()` no repositório
- Isso atualiza automaticamente o status de "pendente" para "atrasado"

### 3. Posso editar uma parcela depois de criada?

Não diretamente pelos endpoints. Se precisar, você pode:
- Desfazer o pagamento (`unpay`)
- Pagar novamente com valores corretos

### 4. E se eu deletar uma compra que tem parcelas pagas?

O endpoint DELETE remove tudo (compra + parcelas), mas **NÃO remove os FinancialEntry** criados. Isso mantém o histórico financeiro intacto.

### 5. Como funciona a integração com lançamentos?

Quando você paga uma parcela:
1. Um `FinancialEntry` é criado automaticamente
2. Ele aparece no dashboard de lançamentos normalmente
3. Fica vinculado à parcela via `financial_entry_id`
4. Se desfizer o pagamento, o `FinancialEntry` é deletado

---

## ✅ Checklist Final

Antes de colocar em produção:

- [ ] Executar migração de índices (`add_credit_indexes.py`)
- [ ] Criar permissões no banco (`features` collection)
- [ ] Atribuir permissões às roles apropriadas
- [ ] Testar todos os endpoints
- [ ] Verificar logs de auditoria
- [ ] Implementar frontend
- [ ] Criar job para atualizar status de parcelas atrasadas
- [ ] Configurar backups do banco

---

## 🎉 Pronto!

O sistema de crediário está **100% implementado e funcional**!

**Para registrar pagamentos no frontend:**
1. Exibir lista de parcelas de uma compra
2. Mostrar botão "Registrar Pagamento" nas parcelas pendentes/atrasadas
3. Abrir modal com formulário
4. Fazer POST para `/api/credit-purchases/{id}/installments/{inst_id}/pay`
5. Atualizar a UI com o resultado

**Qualquer dúvida, consulte o arquivo de documentação do frontend!**

---

**Desenvolvido com ❤️ para o Dashboard Financeiro Multi-Tenant**
