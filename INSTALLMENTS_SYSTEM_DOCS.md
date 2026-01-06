# Sistema de Parcelamento - Documentação Completa

## Visão Geral

O sistema foi atualizado para suportar parcelamento de transações financeiras quando a modalidade de pagamento for "crediário" (`is_credit_plan: true`).

## Conceitos Principais

### 1. Tipos de Entrada Financeira (`type`)

- **`received`**: Valor recebido (padrão para modalidades normais)
- **`receivable`**: Valor a haver (usado quando `allows_credit_payment: true`)

### 2. Fluxo de Crediário

Quando uma modalidade tem `is_credit_plan: true`:
1. A transação é registrada na tabela `financial_entries`
2. O sistema cria automaticamente parcelas na tabela `installments`
3. Cada parcela tem valor proporcional e data de vencimento calculada

### 3. Fluxo de Pagamento de Crediário

Quando uma modalidade tem `allows_credit_payment: true` E o usuário marca `is_credit_payment: true` no request:
1. A transação é registrada como `type: "receivable"` (a haver)
2. Representa o valor bruto de recebimento futuro
3. O campo `allows_credit_payment` da modalidade apenas **permite** que seja marcado como pagamento de crediário, mas não força isso

---

## Estrutura de Dados

### Financial Entry (Entrada Financeira)

```json
{
  "id": "uuid",
  "value": 1000.00,
  "date": "2024-01-15T10:30:00",
  "modality_id": "uuid",
  "modality_name": "Crediário",
  "modality_color": "#FF5733",
  "type": "received" | "receivable",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

### Installment (Parcela)

```json
{
  "id": "uuid",
  "financial_entry_id": "uuid-da-transacao-pai",
  "installment_number": 1,
  "total_installments": 10,
  "amount": 100.00,
  "due_date": "2024-02-15T00:00:00",
  "is_paid": false,
  "payment_date": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

---

## API Endpoints

### 1. Criar Transação Financeira

**Endpoint:** `POST /api/financial-entries`

**Caso 1: Modalidade Normal (sem parcelamento)**
```json
{
  "value": 500.00,
  "date": "2024-01-15T10:30:00",
  "modality_id": "uuid-modalidade"
}
```

**Response (201):**
```json
{
  "entry": {
    "id": "uuid",
    "value": 500.00,
    "date": "2024-01-15T10:30:00",
    "modality_id": "uuid",
    "modality_name": "PIX",
    "modality_color": "#00FF00",
    "type": "received",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  },
  "installments": []
}
```

**Caso 2: Modalidade Crediário (com parcelamento)**
```json
{
  "value": 1000.00,
  "date": "2024-01-15T10:30:00",
  "modality_id": "uuid-crediario",
  "installments_count": 10,
  "start_date": "2024-02-01T00:00:00"
}
```

**Response (201):**
```json
{
  "entry": {
    "id": "entry-uuid",
    "value": 1000.00,
    "date": "2024-01-15T10:30:00",
    "modality_id": "uuid",
    "modality_name": "Crediário",
    "modality_color": "#FF5733",
    "type": "receivable",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  },
  "installments": [
    {
      "id": "inst-1-uuid",
      "financial_entry_id": "entry-uuid",
      "installment_number": 1,
      "total_installments": 10,
      "amount": 100.00,
      "due_date": "2024-02-01T00:00:00",
      "is_paid": false,
      "payment_date": null,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    },
    {
      "id": "inst-2-uuid",
      "financial_entry_id": "entry-uuid",
      "installment_number": 2,
      "total_installments": 10,
      "amount": 100.00,
      "due_date": "2024-03-01T00:00:00",
      "is_paid": false,
      "payment_date": null,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
    // ... mais 8 parcelas
  ]
}
```

**Caso 3: Modalidade que Permite Pagamento de Crediário (usuário marca como tal)**
```json
{
  "value": 100.00,
  "date": "2024-01-15T10:30:00",
  "modality_id": "uuid-que-permite-crediario",
  "is_credit_payment": true
}
```

**Response (201):**
```json
{
  "entry": {
    "id": "uuid",
    "value": 100.00,
    "date": "2024-01-15T10:30:00",
    "modality_id": "uuid",
    "modality_name": "Dinheiro",
    "modality_color": "#4CAF50",
    "type": "receivable",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  },
  "installments": []
}
```

**Caso 4: Mesma Modalidade, mas SEM marcar como pagamento de crediário**
```json
{
  "value": 100.00,
  "date": "2024-01-15T10:30:00",
  "modality_id": "uuid-que-permite-crediario",
  "is_credit_payment": false
}
```

**Response (201):**
```json
{
  "entry": {
    "id": "uuid",
    "value": 100.00,
    "date": "2024-01-15T10:30:00",
    "modality_id": "uuid",
    "modality_name": "Dinheiro",
    "modality_color": "#4CAF50",
    "type": "received",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  },
  "installments": []
}
```

---

### 2. Listar Parcelas

**Endpoint:** `GET /api/installments?financial_entry_id={entry_id}`

**Response (200):**
```json
[
  {
    "id": "uuid",
    "financial_entry_id": "entry-uuid",
    "installment_number": 1,
    "total_installments": 10,
    "amount": 100.00,
    "due_date": "2024-02-01T00:00:00",
    "is_paid": false,
    "payment_date": null,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

---

### 3. Marcar Parcela como Paga

**Endpoint:** `PATCH /api/installments/{installment_id}/pay`

**Request Body (opcional):**
```json
{
  "payment_date": "2024-02-05T14:30:00"
}
```

**Response (200):**
```json
{
  "id": "uuid",
  "financial_entry_id": "entry-uuid",
  "installment_number": 1,
  "total_installments": 10,
  "amount": 100.00,
  "due_date": "2024-02-01T00:00:00",
  "is_paid": true,
  "payment_date": "2024-02-05T14:30:00",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-02-05T14:30:00"
}
```

---

### 4. Desmarcar Parcela como Paga

**Endpoint:** `PATCH /api/installments/{installment_id}/unpay`

**Response (200):**
```json
{
  "id": "uuid",
  "financial_entry_id": "entry-uuid",
  "installment_number": 1,
  "total_installments": 10,
  "amount": 100.00,
  "due_date": "2024-02-01T00:00:00",
  "is_paid": false,
  "payment_date": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-02-05T14:35:00"
}
```

---

## Lógica de Negócio

### Regras de Validação

1. **Modalidade Crediário:**
   - `installments_count` é obrigatório (deve ser >= 1)
   - `start_date` é obrigatório

2. **Cálculo de Parcelas:**
   - Valor da parcela = valor total / número de parcelas
   - Data de vencimento = start_date + (30 dias * número da parcela)
   - Exemplo: 10 parcelas começando em 01/02/2024
     - Parcela 1: 01/02/2024
     - Parcela 2: 03/03/2024
     - Parcela 3: 02/04/2024
     - etc.

3. **Tipo de Entrada:**
   - Se o usuário marcar `is_credit_payment: true` (e a modalidade permitir): `type = "receivable"`
   - Caso contrário: `type = "received"`
   - A modalidade deve ter `allows_credit_payment: true` para permitir marcar como pagamento de crediário

---

## Fluxo Frontend

### 1. Ao Criar Transação

```typescript
// Verificar se a modalidade selecionada é crediário
const selectedModality = modalities.find(m => m.id === selectedModalityId);

if (selectedModality.is_credit_plan) {
  // CASO 1: Modalidade de Crediário
  // Mostrar campos adicionais:
  // - Número de parcelas (input number, min=1)
  // - Data de início (date picker)

  const payload = {
    value: 1000,
    date: new Date().toISOString(),
    modality_id: selectedModality.id,
    installments_count: 10,
    start_date: "2024-02-01T00:00:00"
  };

  const response = await api.post('/financial-entries', payload);
  // response.entry = entrada criada (type: "receivable")
  // response.installments = array de parcelas criadas

} else if (selectedModality.allows_credit_payment) {
  // CASO 2: Modalidade que PERMITE pagamento de crediário
  // Mostrar checkbox: "Este é um pagamento de crediário?"

  const isCreditPayment = userSelectedCheckbox; // valor do checkbox

  const payload = {
    value: 100,
    date: new Date().toISOString(),
    modality_id: selectedModality.id,
    is_credit_payment: isCreditPayment
  };

  const response = await api.post('/financial-entries', payload);
  // Se isCreditPayment = true -> type: "receivable"
  // Se isCreditPayment = false -> type: "received"

} else {
  // CASO 3: Fluxo normal sem parcelas
  const payload = {
    value: 500,
    date: new Date().toISOString(),
    modality_id: selectedModality.id
  };

  const response = await api.post('/financial-entries', payload);
  // type: "received"
}
```

### 2. Exibir Parcelas

```typescript
// Buscar parcelas de uma transação
const installments = await api.get(`/installments?financial_entry_id=${entryId}`);

// Renderizar lista de parcelas
installments.forEach(inst => {
  console.log(`Parcela ${inst.installment_number}/${inst.total_installments}`);
  console.log(`Valor: R$ ${inst.amount.toFixed(2)}`);
  console.log(`Vencimento: ${new Date(inst.due_date).toLocaleDateString()}`);
  console.log(`Status: ${inst.is_paid ? 'PAGA' : 'PENDENTE'}`);
});
```

### 3. Marcar/Desmarcar Pagamento

```typescript
// Marcar como paga
await api.patch(`/installments/${installmentId}/pay`, {
  payment_date: new Date().toISOString() // opcional
});

// Desmarcar como paga
await api.patch(`/installments/${installmentId}/unpay`);
```

---

## Campos da Modalidade de Pagamento

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `is_credit_plan` | boolean | Define se é crediário (gera parcelas automaticamente) |
| `allows_anticipation` | boolean | Define se permite antecipação |
| `allows_credit_payment` | boolean | Define se permite **marcar** como pagamento de crediário na UI |

---

## Resumo Visual da Lógica

### Tabela de Decisão

| Situação | `is_credit_plan` | `allows_credit_payment` | Usuário marca `is_credit_payment` | Resultado `type` | Gera Parcelas? |
|----------|------------------|------------------------|----------------------------------|------------------|----------------|
| Venda no crediário | ✅ `true` | - | - | `receivable` | ✅ SIM |
| Recebimento de parcela (marcado) | ❌ `false` | ✅ `true` | ✅ `true` | `receivable` | ❌ NÃO |
| Recebimento normal (mesma modalidade) | ❌ `false` | ✅ `true` | ❌ `false` | `received` | ❌ NÃO |
| Recebimento PIX/Dinheiro normal | ❌ `false` | ❌ `false` | - | `received` | ❌ NÃO |

### Fluxograma Textual

```
RECEBE REQUEST com modality_id
    ↓
BUSCA modalidade no banco
    ↓
SE modality.is_credit_plan == true
    → Valida: installments_count E start_date obrigatórios
    → type = "receivable"
    → Gera parcelas
SENÃO SE is_credit_payment == true NO REQUEST
    → Valida: modality.allows_credit_payment deve ser true
    → type = "receivable"
    → NÃO gera parcelas
SENÃO
    → type = "received"
    → NÃO gera parcelas
```

---

## Exemplos de Uso

### Exemplo 1: Venda no Crediário (10x)

**Modalidade:** Crediário (`is_credit_plan: true`)

**Request:**
```json
{
  "value": 1000.00,
  "date": "2024-01-15T10:00:00",
  "modality_id": "crediario-uuid",
  "installments_count": 10,
  "start_date": "2024-02-01T00:00:00"
}
```

**Resultado:**
- 1 entrada financeira (`type: "receivable"`, valor: 1000)
- 10 parcelas de R$ 100 cada
- Vencimentos: 01/02, 03/03, 02/04, ..., 01/11/2024

### Exemplo 2: Recebimento de Parcela em Dinheiro

**Modalidade:** Dinheiro (`allows_credit_payment: true`)

**Request:**
```json
{
  "value": 100.00,
  "date": "2024-02-05T14:30:00",
  "modality_id": "dinheiro-uuid"
}
```

**Resultado:**
- 1 entrada financeira (`type: "receivable"`, valor: 100)
- Nenhuma parcela criada

### Exemplo 3: Venda à Vista em PIX

**Modalidade:** PIX (sem flags especiais)

**Request:**
```json
{
  "value": 500.00,
  "date": "2024-01-15T10:00:00",
  "modality_id": "pix-uuid"
}
```

**Resultado:**
- 1 entrada financeira (`type: "received"`, valor: 500)
- Nenhuma parcela criada

---

## Validações de Erro

| Erro | Condição |
|------|----------|
| "Número de parcelas é obrigatório para modalidade de crediário" | `is_credit_plan: true` mas `installments_count` não fornecido |
| "Data de início é obrigatória para modalidade de crediário" | `is_credit_plan: true` mas `start_date` não fornecido |
| "Esta modalidade não permite pagamento de crediário" | Usuário marca `is_credit_payment: true` mas modalidade tem `allows_credit_payment: false` |
| "Parcela não encontrada" | ID de parcela inválido |
| "Parcela já está paga" | Tentativa de marcar como paga uma parcela já paga |
| "Parcela já está como não paga" | Tentativa de desmarcar uma parcela já não paga |

---

## Coleções MongoDB

### `financial_entries`
- Armazena todas as transações financeiras
- Campo `type` diferencia "received" vs "receivable"

### `installments`
- Armazena todas as parcelas
- Relacionado com `financial_entries` via `financial_entry_id`
- Índices: `financial_entry_id`, `due_date`, `is_paid`

---

## Status de Implementação Backend

✅ Entidade `Installment` criada
✅ Repositório de parcelas implementado
✅ Use case `CreateFinancialEntry` atualizado com suporte a parcelas
✅ Use cases `ListInstallments`, `PayInstallment`, `UnpayInstallment` criados
🔄 Rotas de API (próximo passo)
🔄 Testes
