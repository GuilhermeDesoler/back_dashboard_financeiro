# 🔧 Correção de Modalidades Duplicadas

**Data:** 30/12/2025
**Problema:** Múltiplas modalidades com mesmo nome aparecendo na empresa
**Status:** ✅ RESOLVIDO

---

## 🐛 Problema Identificado

### Causa Raiz

O sistema estava permitindo a criação de modalidades duplicadas devido a **3 problemas**:

1. **Validação case-sensitive no código**
   - `find_by_name()` buscava exatamente "PIX", não encontrava "pix" ou "Pix"
   - Permitia criar "PIX", "Pix", "pix" como se fossem diferentes

2. **Índice único case-sensitive no banco**
   - MongoDB por padrão cria índices case-sensitive
   - Índice único em "name" não impedia "PIX" vs "pix"

3. **Falta de normalização de entrada**
   - Não removia espaços extras ("PIX " vs "PIX")
   - Permitia variações como " Pix " vs "Pix"

### Impacto

- ❌ Usuário via múltiplas modalidades com mesmo nome
- ❌ Confusão ao selecionar modalidade
- ❌ Dados inconsistentes no banco

---

## ✅ Soluções Implementadas

### 1. Validação Case-Insensitive no Código

**Arquivo:** [src/infra/repositories/mongo_payment_modality_repository.py:57](src/infra/repositories/mongo_payment_modality_repository.py#L57)

```python
def find_by_name(self, name: str) -> Optional[PaymentModality]:
    # Busca case-insensitive para evitar duplicatas como "PIX" vs "Pix"
    doc = self._collection.find_one({"name": {"$regex": f"^{name.strip()}$", "$options": "i"}})
    if doc:
        return self._doc_to_entity(doc)
    return None
```

**Mudanças:**
- ✅ Busca com regex case-insensitive (`$options: "i"`)
- ✅ Remove espaços extras com `.strip()`
- ✅ Busca exata com `^...$` (evita match parcial)

### 2. Índice Único Case-Insensitive no Banco

**Arquivo:** [src/infra/database/tenant_database_manager.py:97](src/infra/database/tenant_database_manager.py#L97)

```python
# Índices para payment_modalities
# Índice único case-insensitive para evitar duplicatas como "PIX" vs "Pix"
tenant_db["payment_modalities"].create_index(
    "name",
    unique=True,
    collation={"locale": "pt", "strength": 2}  # Case-insensitive
)
```

**Mudanças:**
- ✅ Adicionado parâmetro `collation` com `strength: 2` (case-insensitive)
- ✅ `locale: "pt"` para regras de comparação em português
- ✅ MongoDB agora bloqueia duplicatas no nível do banco

### 3. Script de Migração para Empresas Existentes

**Arquivo:** [scripts/fix_duplicate_modalities.py](scripts/fix_duplicate_modalities.py)

O script automaticamente:
1. ✅ Lista todas as empresas
2. ✅ Identifica modalidades duplicadas (case-insensitive)
3. ✅ Mantém a modalidade mais recente
4. ✅ Remove duplicatas antigas
5. ✅ Remove índice antigo (case-sensitive)
6. ✅ Cria novo índice (case-insensitive)

---

## 📊 Resultado da Execução

```
🔧 Iniciando correção de modalidades duplicadas...

📊 Encontradas 4 empresas

🏢 Processando: Empresa Teste Ltda
   ⚠️  Duplicata encontrada: 'PIX' (5 ocorrências)
      ✅ Mantendo: ID 2e431af4-2b13-43e8-9879-81746e3ec129
      🗑️  Removendo: 4 duplicatas

   [... outras modalidades duplicadas ...]

============================================================
🎉 CORREÇÃO CONCLUÍDA!
============================================================

📊 Resumo:
  • Empresas processadas: 4
  • Modalidades duplicadas removidas: 24
```

---

## 🧪 Validação

### Testes Automatizados

Todos os **31 testes** continuam passando após as correções:

```bash
pytest tests/test_api.py -v
# ============================== 31 passed in 6.79s ==============================
```

### Testes Manuais

**Antes da correção:**
```
Empresa X tinha:
- PIX (5x)
- Dinheiro (5x)
- Cartão de Crédito (5x)
Total: 30 modalidades (6 únicas × 5 duplicatas)
```

**Após a correção:**
```
Empresa X tem:
- PIX (1x)
- Dinheiro (1x)
- Cartão de Crédito (1x)
Total: 6 modalidades únicas ✅
```

### Prevenção de Novas Duplicatas

**Tentativa de criar "pix" quando "PIX" já existe:**

```bash
POST /payment-modalities
{
  "name": "pix",
  "color": "#00FF00"
}

Response: 400 Bad Request
{
  "error": "Modalidade 'pix' já existe"
}
```

✅ **Sistema agora bloqueia corretamente!**

---

## 🚀 Como Usar o Script de Correção

### 1. Para Empresas Existentes (com duplicatas)

```bash
cd back_dashboard_financeiro
source .venv/bin/activate
python scripts/fix_duplicate_modalities.py
```

O script é **idempotente** - pode rodar múltiplas vezes sem problemas.

### 2. Para Novas Empresas

✅ **Não precisa fazer nada!**

Novas empresas criadas já terão o índice correto automaticamente via `TenantDatabaseManager.create_tenant_db()`.

---

## 📋 Checklist de Verificação

Para verificar se a correção foi aplicada corretamente:

- [x] Validação case-insensitive no código implementada
- [x] Índice case-insensitive configurado para novas empresas
- [x] Script de migração executado em empresas existentes
- [x] Duplicatas removidas do banco
- [x] Testes automatizados passando (31/31)
- [x] Teste manual confirmando prevenção de duplicatas

---

## 🔍 Verificação de Índices no MongoDB

Para verificar se os índices estão corretos:

```javascript
// Conectar ao MongoDB
use cmp_XXXXXXXX_db

// Listar índices da collection
db.payment_modalities.getIndexes()

// Resultado esperado:
[
  {
    "v": 2,
    "key": { "_id": 1 },
    "name": "_id_"
  },
  {
    "v": 2,
    "key": { "name": 1 },
    "name": "name_1",
    "unique": true,
    "collation": {
      "locale": "pt",
      "strength": 2
    }
  },
  {
    "v": 2,
    "key": { "is_active": 1 },
    "name": "is_active_1"
  }
]
```

✅ O índice `name_1` deve ter `collation.strength: 2`

---

## 📞 Suporte

Se ainda estiver vendo duplicatas:

1. **Verifique se o script foi executado:**
   ```bash
   python scripts/fix_duplicate_modalities.py
   ```

2. **Verifique os índices no MongoDB** (comando acima)

3. **Reporte o problema** com:
   - Nome da empresa afetada
   - IDs das modalidades duplicadas
   - Screenshot do problema

---

## 🎯 Benefícios da Correção

| Antes | Depois |
|-------|--------|
| ❌ Múltiplas "PIX", "pix", "Pix" | ✅ Apenas 1 modalidade |
| ❌ Usuário confuso ao selecionar | ✅ Lista limpa e clara |
| ❌ Dados inconsistentes | ✅ Dados normalizados |
| ❌ Possível erro em relatórios | ✅ Relatórios confiáveis |

---

## 📝 Notas Técnicas

### Por que `strength: 2`?

MongoDB Collation Strength levels:
- **1**: Base character comparison (ignore accents)
- **2**: Case-insensitive + accent-insensitive
- **3**: Case-sensitive + accent-sensitive

Usamos `strength: 2` para:
- ✅ "PIX" = "pix" (case-insensitive)
- ✅ "Cartão" = "cartao" (accent-insensitive)

### Por que Regex no `find_by_name`?

A validação precisa ser **consistente** com o índice. Mesmo que o índice bloqueie no nível do banco, a validação no código deve:
1. Dar mensagem de erro clara ao usuário
2. Evitar tentativa de insert (melhor UX)
3. Funcionar mesmo se índice for removido acidentalmente

---

**✅ Problema resolvido! Sistema agora 100% protegido contra duplicatas.**
