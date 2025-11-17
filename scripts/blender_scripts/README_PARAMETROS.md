# SCRIPT LEITO_EXTRACAO.PY - DOCUMENTAÇÃO

## ATUALIZAÇÃO: SUPORTE A PARÂMETROS JSON

O script foi atualizado para aceitar parâmetros do arquivo JSON gerado pelo compilador ANTLR.

### **NOVAS FUNCIONALIDADES:**

#### **1. Leitura de Arquivo JSON**

- Lê parâmetros do arquivo `params.json`
- Extrai valores de geometria e partículas
- Usa valores padrão se JSON não for fornecido

#### **2. Argumentos da Linha de Comando**

- `--params` - Caminho do arquivo JSON
- `--output` - Caminho do arquivo .blend de saída
- Compatível com execução headless do Blender

#### **3. Salvamento Automático**

- Salva arquivo `.blend` automaticamente
- Cria diretórios necessários
- Confirma salvamento no console

###  **PARÂMETROS SUPORTADOS:**

#### **Do JSON (bed):**

- `height` - Altura do leito (m)
- `diameter` - Diâmetro do leito (m)
- `wall_thickness` - Espessura da parede (m)

#### **Do JSON (particles):**

- `count` - Número de partículas
- `diameter` - Diâmetro das partículas (m)

### **COMO USAR:**

#### **1. Execução Manual com Parâmetros:**

```bash
blender --background \
  --python leito_extracao.py \
  -- \
  --params caminho/para/arquivo.json \
  --output caminho/para/saida.blend
```

#### **2. Execução via Bed Wizard:**

```bash
cd dsl
python bed_wizard.py
# Escolher opção 3 (modo blender)
```

#### **3. Execução Sem Parâmetros (Padrão):**

```bash
blender --python leito_extracao.py
```

### **ESTRUTURA DO JSON:**

```json
{
  "bed": {
    "diameter": 0.05,
    "height": 0.1,
    "wall_thickness": 0.002
  },
  "particles": {
    "count": 100,
    "diameter": 0.005,
    "kind": "sphere"
  }
}
```

### **VALORES PADRÃO:**

Se algum parâmetro não for fornecido, serão usados:

| Parâmetro         | Valor Padrão |
| ------------------ | ------------- |
| altura             | 0.1 m         |
| diametro           | 0.05 m        |
| espessura_parede   | 0.002 m       |
| num_particulas     | 100           |
| diametro_particula | 0.005 m       |

### **EXEMPLO DE SAÍDA:**

```
parametros carregados de: leito_blender.bed.json
parametros do json:
  altura: 0.1m
  diametro: 0.05m
  espessura parede: 0.002m
  particulas: 100
  diametro particula: 0.005m

cena limpa
cilindro oco criado: altura=0.1, diametro_externo=0.05, espessura_parede=0.002
tampa criada: diametro=0.05, espessura=0.003, altura=0
tampa criada: diametro=0.05, espessura=0.003, altura=0.1
particulas criadas: 100 esferas de 0.005 metros
simulacao fisica configurada
fisica aplicada: leito_extracao (passivo)
fisica aplicada: tampa_inferior (passivo)
fisica aplicada: tampa_superior (passivo)
fisica aplicada: particula_1 (ativo)
...

arquivo salvo: C:\...\output\models\leito_blender.blend
modelo 3d gerado com sucesso!
```

### **NOTAS IMPORTANTES:**

1. **Blender Headless:**

   - O script funciona em modo headless (`--background`)
   - Não exibe interface gráfica
   - Ideal para automação
2. **Caminhos:**

   - Use caminhos absolutos ou relativos corretos
   - Windows: use barras invertidas `\` ou duplas `\\`
   - Linux/Mac: use barras normais `/`
3. **Física:**

   - O script configura rigid body physics
   - Leito e tampas: objetos passivos
   - Partículas: objetos ativos (caem com gravidade)
4. **Tempo de Execução:**

   - 100 partículas: ~30-60 segundos
   - 500 partículas: ~2-3 minutos
   - 1000 partículas: ~5-10 minutos

### **TROUBLESHOOTING:**

#### **Problema: Arquivo não salvo**

```
Solução: Verifique se o diretório de saída existe
         Ou adicione permissões de escrita
```

#### **Problema: JSON não encontrado**

```
Solução: Use caminho absoluto para o arquivo JSON
         Ou execute do diretório correto
```

#### **Problema: Erro ao processar argumentos**

```
Solução: Certifique-se de usar '--' antes dos argumentos
         blender --python script.py -- --params arquivo.json
```

### **REFERÊNCIAS:**

- [Blender Python API](https://docs.blender.org/api/current/)
- [Rigid Body Physics](https://docs.blender.org/manual/en/latest/physics/rigid_body/index.html)
- [Bed Wizard](../../dsl/bed_wizard.py)
- [Compilador ANTLR](../../dsl/compiler/bed_compiler_antlr_standalone.py)
