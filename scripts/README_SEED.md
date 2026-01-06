# Scripts de Seed e Configuração

Este diretório contém scripts para popular o banco de dados e configurar o sistema.

## 📋 Scripts Disponíveis

### 1. `seed_complete_data.py` - Seed Completo de Dados

Popula o banco de dados com dados completos baseados nas tabelas fornecidas.

**O que cria:**
- ✅ **22 Modalidades de Pagamento** (pix, débito, crédito, antecipação, máquinas, aluguel)
  - Sicredi, Sicoob e Link Sicredi
  - Taxas configuradas conforme tabela

- ✅ **2 Limites Bancários**
  - Sicredi: R$ 80.000 (R$ 70.000 usado)
  - Sicoob: R$ 30.000 (R$ 0 usado)

- ✅ **Lançamentos Financeiros** (últimos 30 dias)
  - PIX, Débito, Crédito à vista
  - Crédito 2-6 e 7-12 parcelas
  - Antecipações

- ✅ **4 Crediários (Máquinas)** com parcelas
  - Total: 45 parcelas criadas
  - Algumas parcelas já pagas

- ✅ **Pagamentos de Crediário**
  - Lançamentos correspondentes às parcelas pagas

- ✅ **9 Contas** (Boletos, Pagamentos, Investimentos)
  - 3 Boletos (fornecedor, energia, internet)
  - 3 Pagamentos (salários, aluguel, contador)
  - 3 Investimentos (CDB, Tesouro, Fundos)

- ✅ **Configurações da Plataforma**
  - Antecipação habilitada

**Como usar:**
```bash
cd /Users/primum/financeiros/back_dashboard_financeiro
python scripts/seed_complete_data.py
```

**Pré-requisitos:**
- Banco de dados MongoDB rodando
- Empresa de teste criada (execute `seed_all.py` primeiro se necessário)

---

### 2. `remove_auth_restrictions.py` - Remover Autenticação

Remove todas as restrições de autenticação das APIs. A autenticação será gerenciada apenas no frontend.

**O que faz:**
- ❌ Remove decoradores `@require_auth`
- ❌ Remove decoradores `@require_feature`
- ❌ Remove decoradores `@require_role`
- ❌ Remove decoradores `@require_super_admin`
- 🔄 Substitui `g.company_id` por `COMPANY_ID` fixo
- 📝 Cria arquivo `startup_no_auth.py` para inicialização
- 🔧 Atualiza `main.py` para usar a configuração

**Como usar:**
```bash
cd /Users/primum/financeiros/back_dashboard_financeiro
python scripts/remove_auth_restrictions.py
```

**⚠️ ATENÇÃO:**
- Isso remove TODAS as proteções de autenticação
- Todas as rotas usarão a empresa "Empresa Teste Ltda"
- A autenticação deve ser implementada no frontend
- **Reinicie o servidor** após executar este script

**Após executar:**
```bash
# Reiniciar o servidor
python src/main.py
```

---

## 🚀 Fluxo Recomendado de Execução

### Primeira vez (Setup completo):

```bash
# 1. Criar empresa e usuário de teste
python scripts/seed_all.py

# 2. Popular com dados completos
python scripts/seed_complete_data.py

# 3. (Opcional) Remover autenticação das APIs
python scripts/remove_auth_restrictions.py

# 4. Reiniciar servidor
python src/main.py
```

### Apenas atualizar dados:

```bash
# Limpar e recriar dados
python scripts/seed_complete_data.py
# Responda 's' quando perguntado sobre limpar dados
```

---

## 📊 Dados de Teste Padrão

### Credenciais de Login:
- **Email:** teste@teste.com
- **Senha:** 123456
- **Empresa:** Empresa Teste Ltda
- **CNPJ:** 11.222.333/0001-44

### Modalidades Criadas (conforme tabela):

| Nome | Banco | Taxa Sicredi | Taxa Sicoob | Taxa Link |
|------|-------|--------------|-------------|-----------|
| pix | sicredi/Sicoob/link | 0% | 0% | 0% |
| débito | sicredi/Sicoob/link | 0,9% | 0,9% | 0,9% |
| crédito à vista | sicredi/Sicoob/link | 1,1% | 1,1% | 1,3% |
| crédito 2 a 6 | sicredi/Sicoob/link | 1,4% | 1,4% | 1,6% |
| crédito 7 a 12 | sicredi/Sicoob/link | 1,6% | 1,6% | 1,8% |
| antecipação | sicredi/Sicoob/link | 1,7% | 1,59% | 1,79% |
| máquinas | sicredi/Sicoob | 2,0% | 1,0% | - |
| aluguel | sicredi/Sicoob | R$ 0,00 | R$ 56,90 | - |

### Limites Bancários (conforme tabela):

| Banco | Disponível | Em Uso | Modalidade |
|-------|------------|---------|------------|
| Sicredi | R$ 80.000,00 | R$ 70.000,00 | rotativo |
| Sicoob | R$ 30.000,00 | R$ 0,00 | cheque especial |
| **TOTAL** | **R$ 115.000,00** | **R$ 66.000,00** | |
| **Provisão Juros** | | **R$ 2.302,21** | |

---

## 🔍 Verificando os Dados

### Via MongoDB Shell:
```javascript
// Conectar ao MongoDB
mongosh

// Verificar empresa
use shared_db
db.companies.find({name: "Empresa Teste Ltda"}).pretty()

// Verificar modalidades (substitua COMPANY_ID)
use company_empresa_teste_ltda_db
db.payment_modalities.countDocuments()
db.payment_modalities.find().pretty()

// Verificar lançamentos
db.financial_entries.countDocuments()

// Verificar crediários (installments)
db.installments.countDocuments()
db.installments.find({is_paid: false}).count()  // Pendentes
db.installments.find({is_paid: true}).count()   // Pagas
```

### Via API (com curl):
```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "teste@teste.com", "password": "123456"}'

# Listar modalidades (com token)
curl -X GET http://localhost:5000/api/payment-modalities \
  -H "Authorization: Bearer SEU_TOKEN_AQUI"

# Ou sem autenticação (após executar remove_auth_restrictions.py)
curl -X GET http://localhost:5000/api/payment-modalities
```

---

## 🛠️ Troubleshooting

### Erro: "Empresa de teste não encontrada"
**Solução:** Execute primeiro o `seed_all.py`:
```bash
python scripts/seed_all.py
```

### Erro: "Connection refused" ao MongoDB
**Solução:** Verifique se o MongoDB está rodando:
```bash
# macOS (Homebrew)
brew services start mongodb-community

# Linux (systemd)
sudo systemctl start mongod

# Verificar status
mongosh --eval "db.version()"
```

### Erro: "Module not found"
**Solução:** Certifique-se de estar no diretório correto e que as dependências estão instaladas:
```bash
cd /Users/primum/financeiros/back_dashboard_financeiro
pip install -r requirements.txt
```

### APIs retornam 401 após remover autenticação
**Solução:** Reinicie o servidor Flask:
```bash
# Parar o servidor (Ctrl+C)
# Iniciar novamente
python src/main.py
```

---

## 📝 Notas Importantes

1. **Backup:** Sempre faça backup do banco antes de executar scripts de seed em produção
2. **Ambiente:** Estes scripts são para desenvolvimento/teste. Não use em produção sem adaptações
3. **Company ID:** Todos os dados são criados para a empresa "Empresa Teste Ltda"
4. **Autenticação:** O script `remove_auth_restrictions.py` é APENAS para desenvolvimento local

---

## 🤝 Contribuindo

Para adicionar novos dados ao seed:

1. Edite `seed_complete_data.py`
2. Adicione funções `seed_*()` conforme necessário
3. Chame a função em `main()`
4. Atualize este README com as mudanças

---

## 📚 Referências

- [Documentação MongoDB](https://docs.mongodb.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
