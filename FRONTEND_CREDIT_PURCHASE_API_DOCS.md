# 📘 Documentação da API - Sistema de Crediário

## Visão Geral

Este documento descreve todos os endpoints da API para o sistema de **Crediário** (compras parceladas). O sistema permite registrar compras que serão pagas em parcelas, controlar o status de cada parcela (pendente, pago, atrasado), e visualizar dashboards com os dados agregados.

**Base URL:** `/api`

**Autenticação:** Todos os endpoints requerem header `Authorization: Bearer <token>`

---

## 📋 Estrutura de Dados

### CreditPurchase (Compra no Crediário)

Representa o registro bruto de uma compra parcelada.

```typescript
interface CreditPurchase {
  id: string;                        // UUID da compra
  pagante_nome: string;              // Nome do cliente/pagante
  pagante_documento?: string;        // CPF/CNPJ (opcional)
  pagante_telefone?: string;         // Telefone de contato (opcional)
  descricao_compra: string;          // Descrição do que foi comprado
  valor_total: number;               // Valor total da compra
  valor_entrada: number;             // Valor da entrada paga (default: 0)
  numero_parcelas: number;           // Quantidade de parcelas
  data_inicio_pagamento: string;     // Data do primeiro vencimento (ISO 8601)
  intervalo_dias: number;            // Dias entre parcelas (default: 30)
  taxa_juros_mensal: number;         // Taxa de juros mensal (default: 0)
  registrado_por_user_id: string;    // ID do usuário que criou
  registrado_por_nome: string;       // Nome do usuário que criou
  status: "ativo" | "cancelado" | "concluido";  // Status da compra
  created_at: string;                // Data de criação (ISO 8601)
  updated_at: string;                // Data de atualização (ISO 8601)

  // Campos calculados (retornados em GET details)
  total_pago?: number;               // Total já pago
  total_pendente?: number;           // Total ainda pendente
  parcelas_pagas?: number;           // Quantidade de parcelas pagas
  parcelas_atrasadas?: number;       // Quantidade de parcelas atrasadas
  percentual_pago?: number;          // Percentual pago (0-100)
}
```

### CreditInstallment (Parcela do Crediário)

Representa uma parcela individual de uma compra.

```typescript
interface CreditInstallment {
  id: string;                        // UUID da parcela
  credit_purchase_id: string;        // ID da compra (FK)
  numero_parcela: number;            // Número da parcela (1, 2, 3...)
  valor_parcela: number;             // Valor original da parcela
  valor_juros: number;               // Juros aplicados (default: 0)
  valor_multa: number;               // Multa por atraso (default: 0)
  valor_total: number;               // parcela + juros + multa (calculado)
  data_vencimento: string;           // Data de vencimento (ISO 8601)
  data_pagamento?: string;           // Data do pagamento (null se não pago)
  status: "pendente" | "pago" | "atrasado" | "cancelado";
  financial_entry_id?: string;       // ID do lançamento financeiro (quando pago)
  pago_por_user_id?: string;         // ID do usuário que registrou o pagamento
  pago_por_nome?: string;            // Nome do usuário que registrou
  observacao: string;                // Observações sobre a parcela
  dias_atraso: number;               // Dias de atraso (calculado)
  created_at: string;                // Data de criação
  updated_at: string;                // Data de atualização

  // Campos enriquecidos (dashboard)
  pagante_nome?: string;             // Nome do cliente (vindo da compra)
  descricao_compra?: string;         // Descrição (vindo da compra)
  pagante_telefone?: string;         // Telefone (vindo da compra)
}
```

---

## 🔑 Endpoints

### 1. Criar Compra no Crediário

Cria uma nova compra no crediário e gera automaticamente as parcelas.

**Endpoint:** `POST /api/credit-purchases`

**Permissão:** `credit_purchases.create`

**Request Body:**
```json
{
  "pagante_nome": "João Silva",                      // Obrigatório
  "pagante_documento": "123.456.789-00",            // Opcional
  "pagante_telefone": "(11) 98765-4321",            // Opcional
  "descricao_compra": "Geladeira Brastemp 450L",    // Obrigatório
  "valor_total": 3000.00,                           // Obrigatório
  "valor_entrada": 500.00,                          // Opcional (default: 0)
  "numero_parcelas": 10,                            // Obrigatório
  "data_inicio_pagamento": "2025-02-01T00:00:00Z",  // Obrigatório (ISO 8601)
  "intervalo_dias": 30,                             // Opcional (default: 30)
  "taxa_juros_mensal": 0.0                          // Opcional (default: 0)
}
```

**Response:** `201 Created`
```json
{
  "credit_purchase": {
    "id": "uuid-compra",
    "pagante_nome": "João Silva",
    "valor_total": 3000.00,
    "numero_parcelas": 10,
    "status": "ativo",
    "created_at": "2025-01-15T10:00:00Z",
    ...
  },
  "installments": [
    {
      "id": "uuid-parcela-1",
      "numero_parcela": 1,
      "valor_parcela": 250.00,
      "data_vencimento": "2025-02-01T00:00:00Z",
      "status": "pendente",
      ...
    },
    // ... 9 parcelas restantes
  ]
}
```

**Erros:**
- `400`: Dados inválidos
- `401`: Não autenticado
- `403`: Sem permissão

---

### 2. Listar Compras no Crediário

Lista todas as compras com filtros e paginação.

**Endpoint:** `GET /api/credit-purchases`

**Permissão:** `credit_purchases.read`

**Query Parameters:**
- `status` (opcional): Filtrar por status (`ativo`, `cancelado`, `concluido`)
- `pagante_nome` (opcional): Busca parcial pelo nome do pagante
- `page` (opcional): Número da página (default: 1)
- `per_page` (opcional): Itens por página (default: 20, max: 100)

**Exemplo:** `GET /api/credit-purchases?status=ativo&pagante_nome=João&page=1&per_page=20`

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": "uuid-compra-1",
      "pagante_nome": "João Silva",
      "descricao_compra": "Geladeira Brastemp 450L",
      "valor_total": 3000.00,
      "numero_parcelas": 10,
      "status": "ativo",
      ...
    },
    ...
  ],
  "total": 25,          // Total de registros
  "page": 1,            // Página atual
  "per_page": 20        // Itens por página
}
```

---

### 3. Buscar Compra por ID (Detalhes Completos)

**🔥 IMPORTANTE:** Use este endpoint para exibir todos os detalhes de uma compra específica, incluindo todas as parcelas.

**Endpoint:** `GET /api/credit-purchases/{credit_purchase_id}`

**Permissão:** `credit_purchases.read`

**Response:** `200 OK`
```json
{
  "id": "uuid-compra",
  "pagante_nome": "João Silva",
  "pagante_documento": "123.456.789-00",
  "pagante_telefone": "(11) 98765-4321",
  "descricao_compra": "Geladeira Brastemp 450L",
  "valor_total": 3000.00,
  "valor_entrada": 500.00,
  "numero_parcelas": 10,
  "status": "ativo",
  "registrado_por_nome": "Maria Admin",
  "created_at": "2025-01-15T10:00:00Z",

  // Campos calculados
  "total_pago": 750.00,
  "total_pendente": 1750.00,
  "parcelas_pagas": 3,
  "parcelas_atrasadas": 2,
  "percentual_pago": 30.0,

  // Todas as parcelas
  "installments": [
    {
      "id": "uuid-parcela-1",
      "numero_parcela": 1,
      "valor_parcela": 250.00,
      "valor_total": 250.00,
      "data_vencimento": "2025-02-01T00:00:00Z",
      "data_pagamento": "2025-02-01T10:30:00Z",
      "status": "pago",
      "pago_por_nome": "Carlos Vendedor",
      "dias_atraso": 0
    },
    {
      "id": "uuid-parcela-2",
      "numero_parcela": 2,
      "valor_parcela": 250.00,
      "valor_total": 250.00,
      "data_vencimento": "2025-03-01T00:00:00Z",
      "data_pagamento": null,
      "status": "atrasado",
      "dias_atraso": 16
    },
    // ... demais parcelas
  ]
}
```

**Erros:**
- `404`: Compra não encontrada

---

### 4. Atualizar Compra

Atualiza informações de uma compra (apenas campos editáveis).

**Endpoint:** `PUT /api/credit-purchases/{credit_purchase_id}`

**Permissão:** `credit_purchases.update`

**Request Body:**
```json
{
  "pagante_telefone": "(11) 91111-2222",           // Opcional
  "pagante_documento": "123.456.789-00",           // Opcional
  "descricao_compra": "Geladeira + Garantia"       // Opcional
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid-compra",
  "pagante_telefone": "(11) 91111-2222",
  "updated_at": "2025-01-20T14:30:00Z",
  ...
}
```

---

### 5. Cancelar Compra

Cancela uma compra e todas as suas parcelas pendentes/atrasadas.

**Endpoint:** `PATCH /api/credit-purchases/{credit_purchase_id}/cancel`

**Permissão:** `credit_purchases.cancel`

**Response:** `200 OK`
```json
{
  "credit_purchase": {
    "id": "uuid-compra",
    "status": "cancelado",
    ...
  },
  "canceled_installments": 7  // Quantidade de parcelas canceladas
}
```

---

### 6. Deletar Compra

**⚠️ ATENÇÃO:** Operação irreversível! Remove a compra e todas as parcelas.

**Endpoint:** `DELETE /api/credit-purchases/{credit_purchase_id}`

**Permissão:** `credit_purchases.delete`

**Response:** `200 OK`
```json
{
  "message": "Compra deletada com sucesso",
  "deleted_installments": 10
}
```

---

## 💰 Gerenciamento de Parcelas

### 7. Registrar Pagamento de Parcela

**🔥 ENDPOINT PRINCIPAL:** Use este endpoint para registrar o pagamento de uma parcela.

**Endpoint:** `POST /api/credit-purchases/{credit_purchase_id}/installments/{installment_id}/pay`

**Permissão:** `credit_installments.pay`

**Request Body:**
```json
{
  "data_pagamento": "2025-02-01T15:30:00Z",  // Obrigatório (ISO 8601)
  "modality_id": "uuid-modalidade",          // Obrigatório (ex: PIX, Dinheiro)
  "valor_juros": 0.0,                        // Opcional (default: 0)
  "valor_multa": 0.0,                        // Opcional (default: 0)
  "observacao": "Pago em dinheiro"           // Opcional
}
```

**Response:** `200 OK`
```json
{
  "installment": {
    "id": "uuid-parcela",
    "status": "pago",
    "data_pagamento": "2025-02-01T15:30:00Z",
    "pago_por_nome": "Carlos Vendedor",
    "valor_total": 250.00,
    "financial_entry_id": "uuid-lancamento",
    ...
  },
  "financial_entry": {
    "id": "uuid-lancamento",
    "value": 250.00,
    "modality_name": "Dinheiro",
    "date": "2025-02-01T15:30:00Z"
  }
}
```

**Comportamento:**
1. Marca a parcela como paga
2. Cria automaticamente um `FinancialEntry` (lançamento financeiro)
3. Vincula os dois registros
4. Se todas as parcelas forem pagas, marca a compra como "concluido"

**Erros:**
- `400`: Parcela já está paga ou dados inválidos
- `404`: Parcela não encontrada

---

### 8. Desfazer Pagamento de Parcela

Remove o pagamento de uma parcela e o lançamento financeiro vinculado.

**Endpoint:** `POST /api/credit-purchases/{credit_purchase_id}/installments/{installment_id}/unpay`

**Permissão:** `credit_installments.unpay`

**Response:** `200 OK`
```json
{
  "installment": {
    "id": "uuid-parcela",
    "status": "atrasado",  // ou "pendente"
    "data_pagamento": null,
    "pago_por_nome": null,
    ...
  }
}
```

**Comportamento:**
1. Remove o `FinancialEntry` vinculado
2. Reseta os dados de pagamento da parcela
3. Recalcula o status (pendente ou atrasado)
4. Reativa a compra se estava concluída

---

## 📊 Dashboard e Relatórios

### 9. Dashboard - Parcelas por Data

**🔥 PRINCIPAL PARA DASHBOARD:** Obtém parcelas agrupadas por data de vencimento (similar ao dashboard de lançamentos).

**Endpoint:** `GET /api/credit-purchases/dashboard/installments-by-date`

**Permissão:** `credit_purchases.read`

**Query Parameters:**
- `start_date` (obrigatório): Data inicial (ISO 8601)
- `end_date` (obrigatório): Data final (ISO 8601)
- `status` (opcional): Filtrar por status (`pendente`, `pago`, `atrasado`)

**Exemplo:** `GET /api/credit-purchases/dashboard/installments-by-date?start_date=2025-02-01T00:00:00Z&end_date=2025-02-28T23:59:59Z&status=pendente`

**Response:** `200 OK`
```json
{
  "period": {
    "start_date": "2025-02-01T00:00:00Z",
    "end_date": "2025-02-28T23:59:59Z"
  },
  "summary": {
    "total_parcelas": 45,
    "total_valor": 11250.00,
    "parcelas_pagas": 20,
    "valor_pago": 5000.00,
    "parcelas_pendentes": 15,
    "valor_pendente": 3750.00,
    "parcelas_atrasadas": 10,
    "valor_atrasado": 2500.00,
    "taxa_inadimplencia": 22.22
  },
  "installments_by_date": [
    {
      "data_vencimento": "2025-02-01",
      "total_dia": 1250.00,
      "quantidade_parcelas": 5,
      "installments": [
        {
          "id": "uuid-parcela-1",
          "credit_purchase_id": "uuid-compra-1",  // ID para link/detalhes
          "pagante_nome": "João Silva",
          "descricao_compra": "Geladeira Brastemp 450L",
          "numero_parcela": 1,
          "valor_parcela": 250.00,
          "valor_total": 250.00,
          "status": "pago",
          "dias_atraso": 0
        },
        {
          "id": "uuid-parcela-2",
          "credit_purchase_id": "uuid-compra-2",
          "pagante_nome": "Maria Santos",
          "descricao_compra": "Notebook Dell",
          "numero_parcela": 3,
          "valor_parcela": 500.00,
          "valor_total": 500.00,
          "status": "atrasado",
          "dias_atraso": 5
        },
        // ... mais parcelas do dia
      ]
    },
    {
      "data_vencimento": "2025-02-15",
      "total_dia": 2000.00,
      "quantidade_parcelas": 8,
      "installments": [...]
    }
    // ... mais datas
  ]
}
```

**Uso no Frontend:**
- Exibir calendário/lista com parcelas agrupadas por data
- Mostrar resumo geral no topo
- Clicar no `credit_purchase_id` para ver detalhes completos da compra
- Usar ícones/cores baseados no `status` (pago ✅, atrasado ⚠️, pendente 🕐)

---

### 10. Totais Gerais

Obtém totais agregados das parcelas.

**Endpoint:** `GET /api/credit-purchases/dashboard/totals`

**Permissão:** `credit_purchases.read`

**Query Parameters:**
- `start_date` (opcional): Data inicial
- `end_date` (opcional): Data final

**Response:** `200 OK`
```json
{
  "total_parcelas": 120,
  "total_valor": 30000.00,
  "total_pago": 18000.00,
  "total_pendente": 8000.00,
  "total_atrasado": 4000.00,
  "parcelas_pagas": 72,
  "parcelas_pendentes": 32,
  "parcelas_atrasadas": 16,
  "taxa_inadimplencia": 13.33
}
```

---

### 11. Parcelas Atrasadas

Obtém todas as parcelas atrasadas.

**Endpoint:** `GET /api/credit-purchases/dashboard/overdue`

**Permissão:** `credit_purchases.read`

**Response:** `200 OK`
```json
{
  "total_atrasado": 3500.00,
  "quantidade_parcelas": 14,
  "installments": [
    {
      "id": "uuid-parcela",
      "credit_purchase_id": "uuid-compra",
      "pagante_nome": "Pedro Costa",
      "pagante_telefone": "(11) 99999-8888",
      "descricao_compra": "TV Samsung 55\"",
      "numero_parcela": 2,
      "valor_parcela": 300.00,
      "valor_total": 300.00,
      "data_vencimento": "2025-01-15T00:00:00Z",
      "dias_atraso": 16,
      "status": "atrasado"
    },
    // ... mais parcelas atrasadas
  ]
}
```

**Uso no Frontend:**
- Alertas/notificações de parcelas atrasadas
- Listar parcelas para cobranças
- Exibir telefone para contato

---

### 12. Parcelas Vencendo em Breve

Obtém parcelas que vencem nos próximos N dias.

**Endpoint:** `GET /api/credit-purchases/dashboard/due-soon`

**Permissão:** `credit_purchases.read`

**Query Parameters:**
- `days` (opcional): Próximos N dias (default: 7)

**Exemplo:** `GET /api/credit-purchases/dashboard/due-soon?days=7`

**Response:** `200 OK`
```json
{
  "periodo_dias": 7,
  "total_valor": 2500.00,
  "quantidade_parcelas": 10,
  "installments": [
    {
      "id": "uuid-parcela",
      "credit_purchase_id": "uuid-compra",
      "pagante_nome": "Ana Costa",
      "pagante_telefone": "(11) 98888-7777",
      "numero_parcela": 5,
      "valor_parcela": 200.00,
      "data_vencimento": "2025-02-05T00:00:00Z",
      "status": "pendente"
    },
    // ... mais parcelas
  ]
}
```

---

## 🎨 Sugestões de UI/UX

### Tela 1: Lista de Compras
```
┌─────────────────────────────────────────────────────┐
│  Compras no Crediário                     [+ Nova]  │
├─────────────────────────────────────────────────────┤
│  🔍 Filtros: [Status ▼] [Nome do Cliente]          │
├─────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────┐  │
│  │ João Silva - Geladeira Brastemp        🟢     │  │
│  │ R$ 3.000,00 • 10x • 30% pago (3/10)           │  │
│  │ Vencimento próximo: 01/03                     │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │ Maria Santos - Notebook Dell           ⚠️      │  │
│  │ R$ 6.000,00 • 12x • 25% pago (3/12)           │  │
│  │ ⚠️ 2 parcelas atrasadas                        │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Tela 2: Calendário de Parcelas (Dashboard Principal)
```
┌─────────────────────────────────────────────────────┐
│  Parcelas do Mês - Fevereiro 2025                  │
├─────────────────────────────────────────────────────┤
│  📊 Resumo:                                         │
│  • A receber: R$ 11.250,00 (45 parcelas)           │
│  • Pago: R$ 5.000,00 (20) • Pendente: R$ 3.750 (15)│
│  • Atrasado: R$ 2.500,00 (10) ⚠️                    │
├─────────────────────────────────────────────────────┤
│  📅 01/02 - R$ 1.250,00 (5 parcelas)               │
│  ├─ ✅ João Silva - Geladeira - Parc. 1/10 - R$ 250│
│  ├─ ⚠️ Maria Santos - Notebook - Parc. 3/12 - R$ 500│
│  └─ 🕐 Pedro Costa - TV - Parc. 2/6 - R$ 300       │
│                                                      │
│  📅 15/02 - R$ 2.000,00 (8 parcelas)               │
│  └─ ...                                              │
└─────────────────────────────────────────────────────┘
```

### Tela 3: Detalhes da Compra
```
┌─────────────────────────────────────────────────────┐
│  ← Voltar    Compra #abc123            [Cancelar]  │
├─────────────────────────────────────────────────────┤
│  👤 João Silva • (11) 98765-4321                   │
│  🛒 Geladeira Brastemp 450L                        │
│  💰 Total: R$ 3.000,00 • Entrada: R$ 500,00        │
│  📊 Progresso: [████████░░] 30% (3/10 pagas)       │
│  📅 Criado em 15/01/2025 por Maria Admin           │
├─────────────────────────────────────────────────────┤
│  Parcelas:                                          │
│  ┌─────────────────────────────────────────────┐   │
│  │ 1/10 • R$ 250 • Venc: 01/02 • ✅ Pago 01/02 │   │
│  │ Pago por: Carlos Vendedor                   │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │ 2/10 • R$ 250 • Venc: 01/03 • ⚠️ 16 dias    │   │
│  │ [💰 Registrar Pagamento]                    │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Modal de Registro de Pagamento
```
┌──────────────────────────────────────────┐
│  Registrar Pagamento - Parcela 2/10      │
├──────────────────────────────────────────┤
│  Cliente: João Silva                     │
│  Valor da parcela: R$ 250,00             │
│                                          │
│  Data do pagamento: [01/03/2025] 📅      │
│  Forma de pagamento: [PIX ▼]             │
│  Juros: [R$ 0,00]                        │
│  Multa: [R$ 0,00]                        │
│  ────────────────────────────────────    │
│  Total a pagar: R$ 250,00                │
│                                          │
│  Observação:                             │
│  [________________________]              │
│                                          │
│  [Cancelar]  [✅ Confirmar Pagamento]   │
└──────────────────────────────────────────┘
```

---

## ✅ Checklist de Implementação Frontend

### Páginas/Componentes Principais

- [ ] **Lista de Compras** (`/credito` ou `/crediario`)
  - Filtros por status e nome
  - Cards com resumo de cada compra
  - Botão para criar nova compra
  - Indicadores visuais de status

- [ ] **Formulário de Nova Compra**
  - Campos de cliente (nome, CPF, telefone)
  - Dados da compra (descrição, valor, entrada)
  - Configuração de parcelas (quantidade, intervalo, juros)
  - Validação de campos obrigatórios

- [ ] **Detalhes da Compra**
  - Informações completas do cliente e compra
  - Barra de progresso do pagamento
  - Lista de todas as parcelas com status
  - Botão para registrar pagamento em cada parcela pendente
  - Opção de cancelar compra

- [ ] **Dashboard de Parcelas**
  - Calendário ou lista agrupada por data
  - Resumo geral (totais, taxa de inadimplência)
  - Filtros por período e status
  - Indicadores visuais por status (cores/ícones)

- [ ] **Modal de Registro de Pagamento**
  - Data do pagamento (date picker)
  - Seleção de modalidade de pagamento
  - Campos de juros e multa
  - Campo de observação
  - Cálculo automático do total

- [ ] **Alertas e Notificações**
  - Badge com quantidade de parcelas atrasadas
  - Lista de parcelas vencendo em breve
  - Opção de enviar lembrete (futuro)

### Funcionalidades

- [ ] CRUD completo de compras
- [ ] Registro e estorno de pagamentos
- [ ] Filtros e busca
- [ ] Paginação nas listagens
- [ ] Dashboard com gráficos (opcional)
- [ ] Exportação de relatórios (futuro)
- [ ] Integração com sistema de lançamentos financeiros

### Permissões a Criar

No backend, você precisará criar estas features/permissões:

```typescript
const permissions = [
  "credit_purchases.create",     // Criar compras
  "credit_purchases.read",       // Visualizar compras
  "credit_purchases.update",     // Editar compras
  "credit_purchases.delete",     // Deletar compras
  "credit_purchases.cancel",     // Cancelar compras
  "credit_installments.pay",     // Registrar pagamentos
  "credit_installments.unpay",   // Desfazer pagamentos
];
```

---

## 🚀 Exemplo de Fluxo Completo

### 1. Criar Nova Compra
```typescript
const response = await fetch('/api/credit-purchases', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    pagante_nome: "João Silva",
    descricao_compra: "Geladeira Brastemp 450L",
    valor_total: 3000.00,
    numero_parcelas: 10,
    data_inicio_pagamento: "2025-02-01T00:00:00Z"
  })
});
const data = await response.json();
// data.credit_purchase.id -> uuid da compra
// data.installments -> array com 10 parcelas
```

### 2. Buscar Detalhes da Compra
```typescript
const response = await fetch(`/api/credit-purchases/${purchaseId}`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
const compra = await response.json();
// compra.installments -> todas as parcelas
```

### 3. Registrar Pagamento
```typescript
const response = await fetch(
  `/api/credit-purchases/${purchaseId}/installments/${installmentId}/pay`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      data_pagamento: new Date().toISOString(),
      modality_id: "uuid-pix",
      valor_juros: 0,
      valor_multa: 0,
      observacao: "Pago via PIX"
    })
  }
);
const result = await response.json();
// result.installment -> parcela atualizada (status: "pago")
// result.financial_entry -> lançamento criado automaticamente
```

### 4. Dashboard
```typescript
const startDate = "2025-02-01T00:00:00Z";
const endDate = "2025-02-28T23:59:59Z";

const response = await fetch(
  `/api/credit-purchases/dashboard/installments-by-date?start_date=${startDate}&end_date=${endDate}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const dashboard = await response.json();
// dashboard.summary -> totais gerais
// dashboard.installments_by_date -> parcelas agrupadas por data
```

---

## 📞 Suporte

Para dúvidas sobre a API, verifique:
- Logs de auditoria: `GET /api/admin/audit-logs` (super admin)
- Health check: `GET /health`
- Documentação principal: `GET /`

---

**Versão da API:** 2.0.0

**Data do Documento:** 2025-01-31

**Desenvolvido por:** Sistema de Dashboard Financeiro Multi-Tenant
