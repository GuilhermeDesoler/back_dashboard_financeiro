# API Endpoints - Payment Modalities

Base URL: `http://localhost:5000/api`

## Autenticação
Todos os endpoints requerem autenticação via JWT Token no header:
```
Authorization: Bearer {token}
```

---

## Payment Modalities

### 1. Criar Modalidade de Pagamento
**Endpoint:** `POST /payment-modalities`

**Permissão necessária:** `payment_modalities.create`

**Request Body:**
```json
{
  "name": "string (obrigatório)",
  "color": "string (obrigatório, ex: #FF5733)",
  "is_active": "boolean (opcional, default: true)",
  "is_credit_plan": "boolean (opcional, default: false)",
  "allows_anticipation": "boolean (opcional, default: false)",
  "allows_credit_payment": "boolean (opcional, default: false)"
}
```

**Exemplo de Request:**
```json
{
  "name": "PIX",
  "color": "#00C853",
  "is_active": true,
  "is_credit_plan": false,
  "allows_anticipation": true,
  "allows_credit_payment": false
}
```

**Response Success (201):**
```json
{
  "id": "uuid",
  "name": "PIX",
  "color": "#00C853",
  "is_active": true,
  "is_credit_plan": false,
  "allows_anticipation": true,
  "allows_credit_payment": false,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Response Error (400):**
```json
{
  "error": "Nome da modalidade é obrigatório"
}
```
ou
```json
{
  "error": "Modalidade 'PIX' já existe"
}
```

---

### 2. Listar Modalidades de Pagamento
**Endpoint:** `GET /payment-modalities`

**Permissão necessária:** `payment_modalities.read`

**Query Parameters:**
- `only_active` (opcional): `true` | `false` (default: `true`)
  - `true`: retorna apenas modalidades ativas
  - `false`: retorna todas as modalidades

**Exemplo de Request:**
```
GET /payment-modalities?only_active=false
```

**Response Success (200):**
```json
[
  {
    "id": "uuid-1",
    "name": "PIX",
    "color": "#00C853",
    "is_active": true,
    "is_credit_plan": false,
    "allows_anticipation": true,
    "allows_credit_payment": false,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  },
  {
    "id": "uuid-2",
    "name": "Crediário",
    "color": "#FF5733",
    "is_active": true,
    "is_credit_plan": true,
    "allows_anticipation": false,
    "allows_credit_payment": true,
    "created_at": "2024-01-15T11:00:00",
    "updated_at": "2024-01-15T11:00:00"
  },
  {
    "id": "uuid-3",
    "name": "Dinheiro",
    "color": "#4CAF50",
    "is_active": false,
    "is_credit_plan": false,
    "allows_anticipation": false,
    "allows_credit_payment": false,
    "created_at": "2024-01-15T12:00:00",
    "updated_at": "2024-01-15T14:00:00"
  }
]
```

---

### 3. Atualizar Modalidade de Pagamento
**Endpoint:** `PUT /payment-modalities/{modality_id}`

**Permissão necessária:** `payment_modalities.update`

**URL Parameters:**
- `modality_id`: ID da modalidade

**Request Body (todos os campos são opcionais):**
```json
{
  "name": "string (opcional)",
  "color": "string (opcional)",
  "is_active": "boolean (opcional)",
  "is_credit_plan": "boolean (opcional)",
  "allows_anticipation": "boolean (opcional)",
  "allows_credit_payment": "boolean (opcional)"
}
```

**Exemplo de Request:**
```json
{
  "color": "#FF9800",
  "allows_anticipation": true
}
```

**Response Success (200):**
```json
{
  "id": "uuid",
  "name": "PIX",
  "color": "#FF9800",
  "is_active": true,
  "is_credit_plan": false,
  "allows_anticipation": true,
  "allows_credit_payment": false,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T15:30:00"
}
```

**Response Error (404):**
```json
{
  "error": "Modalidade não encontrada"
}
```

**Response Error (400):**
```json
{
  "error": "Modalidade 'Nome Duplicado' já existe"
}
```

---

### 4. Deletar Modalidade de Pagamento
**Endpoint:** `DELETE /payment-modalities/{modality_id}`

**Permissão necessária:** `payment_modalities.delete`

**URL Parameters:**
- `modality_id`: ID da modalidade

**Response Success (200):**
```json
{
  "message": "Modalidade deletada com sucesso"
}
```

**Response Error (404):**
```json
{
  "error": "Modalidade não encontrada"
}
```

---

### 5. Toggle Status da Modalidade
**Endpoint:** `PATCH /payment-modalities/{modality_id}/toggle`

**Permissão necessária:** `payment_modalities.toggle`

**URL Parameters:**
- `modality_id`: ID da modalidade

**Request Body:**
```json
{
  "activate": "boolean (opcional, default: true)"
}
```

**Exemplo de Request (Ativar):**
```json
{
  "activate": true
}
```

**Exemplo de Request (Desativar):**
```json
{
  "activate": false
}
```

**Response Success (200):**
```json
{
  "id": "uuid",
  "name": "PIX",
  "color": "#00C853",
  "is_active": true,
  "is_credit_plan": false,
  "allows_anticipation": true,
  "allows_credit_payment": false,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T16:00:00"
}
```

**Response Error (404):**
```json
{
  "error": "Modalidade não encontrada"
}
```

---

## Platform Settings

### 1. Obter Configurações da Plataforma
**Endpoint:** `GET /platform-settings`

**Permissão necessária:** `platform_settings.read`

**Response Success (200):**
```json
{
  "id": "platform_settings",
  "is_anticipation_enabled": false,
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:00:00"
}
```

---

### 2. Toggle Antecipação da Plataforma
**Endpoint:** `PATCH /platform-settings/toggle-anticipation`

**Permissão necessária:** `platform_settings.toggle_anticipation`

**Response Success (200):**
```json
{
  "id": "platform_settings",
  "is_anticipation_enabled": true,
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T16:30:00"
}
```

---

## Descrição dos Campos de Payment Modality

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | string | ID único da modalidade (UUID) |
| `name` | string | Nome da modalidade (ex: "PIX", "Dinheiro", "Crediário") |
| `color` | string | Cor em hexadecimal (ex: "#FF5733") |
| `is_active` | boolean | Define se a modalidade está ativa no sistema |
| `is_credit_plan` | boolean | Define se é uma modalidade de crediário |
| `allows_anticipation` | boolean | Define se permite antecipação de valores |
| `allows_credit_payment` | boolean | Define se permite pagamento de crediário |
| `created_at` | string | Data/hora de criação (ISO 8601) |
| `updated_at` | string | Data/hora da última atualização (ISO 8601) |

---

## Notas Importantes

1. **Validação de Nome:** O sistema impede a criação de modalidades com nomes duplicados (case-insensitive). Por exemplo, "PIX" e "pix" são considerados duplicados.

2. **Multi-Tenant:** Todas as modalidades são isoladas por empresa. Cada empresa possui suas próprias modalidades de pagamento.

3. **Autenticação:** Todos os endpoints requerem um token JWT válido no header `Authorization`.

4. **Permissões RBAC:** Cada endpoint verifica se o usuário possui a feature/permissão necessária.

5. **Valores Padrão:**
   - `is_active`: `true`
   - `is_credit_plan`: `false`
   - `allows_anticipation`: `false`
   - `allows_credit_payment`: `false`
