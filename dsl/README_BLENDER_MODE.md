# 🎨 MODO BLENDER - BED WIZARD

## 📋 DESCRIÇÃO

O **Modo Blender** do Bed Wizard é uma interface simplificada para gerar apenas modelos 3D de leitos empacotados, sem configurar parâmetros CFD.

## 🎯 OBJETIVO

Este modo foi criado para usuários que desejam:
- Gerar rapidamente modelos 3D
- Visualizar geometrias de leitos
- Exportar para formatos compatíveis (BLEND, STL)
- Trabalhar apenas com a parte de modelagem (sem simulação CFD)

## 🚀 COMO USAR

### **1. Executar o Bed Wizard**

```bash
cd dsl
python bed_wizard.py
```

### **2. Selecionar Modo Blender**

No menu principal, escolha a opção **3. modo blender**:

```
escolha o modo de criacao:
1. questionario interativo - responda perguntas passo a passo
2. editor de template - edite um arquivo padrao
3. modo blender - apenas geracao de modelo 3d (sem cfd)
4. sair

escolha (1-4): 3
```

### **3. Configurar Parâmetros**

O wizard irá solicitar os seguintes parâmetros:

#### **Geometria do Leito**
- diametro do leito (m)
- altura do leito (m)
- espessura da parede (m)
- folga superior (m)
- material da parede
- rugosidade (m) - opcional

#### **Tampas**
- tipo da tampa superior (flat, hemispherical, none)
- tipo da tampa inferior (flat, hemispherical, none)
- espessura tampa superior (m)
- espessura tampa inferior (m)
- folga do selo (m) - opcional

#### **Partículas**
- tipo de particula (sphere, cube, cylinder)
- diametro das particulas (m)
- numero de particulas
- porosidade alvo - opcional
- densidade do material (kg/m3)
- massa das particulas (g) - opcional
- coeficiente de restituicao - opcional
- coeficiente de atrito - opcional
- atrito de rolamento - opcional
- amortecimento linear - opcional
- amortecimento angular - opcional
- seed para reproducibilidade - opcional

#### **Empacotamento**
- metodo de empacotamento (rigid_body)
- gravidade (m/s2)
- sub-passos de simulacao - opcional
- iteracoes - opcional
- amortecimento - opcional
- velocidade de repouso (m/s) - opcional
- tempo maximo (s) - opcional
- margem de colisao (m) - opcional

### **4. Confirmar e Gerar**

Após configurar todos os parâmetros:
1. O wizard mostrará um resumo
2. Confirmará se deseja continuar
3. Salvará o arquivo `.bed`
4. Compilará para `.json`
5. Executará o Blender automaticamente
6. Salvará o modelo em `output/models/`

## 📂 ESTRUTURA DE ARQUIVOS

```
CFD-PIPELINE-TCC-1/
├── dsl/
│   ├── bed_wizard.py           # script principal
│   ├── leito_blender.bed       # arquivo .bed gerado
│   └── leito_blender.bed.json  # arquivo json compilado
├── output/
│   └── models/
│       └── leito_blender.blend # modelo 3d gerado
└── scripts/
    └── blender_scripts/
        └── leito_extracao.py   # script de geracao 3d
```

## ⚙️ CONFIGURAÇÕES

### **Parâmetros CFD**
No modo Blender, os parâmetros CFD **NÃO são configurados**. Este modo é apenas para geração de geometria 3D.

### **Formatos de Exportação**
Por padrão, o modo Blender exporta em:
- **BLEND** - formato nativo do Blender
- **STL** - formato para impressão 3D e CAD

### **Diretório de Saída**
Todos os modelos são salvos em:
```
CFD-PIPELINE-TCC-1/output/models/
```

## 🔧 REQUISITOS

- **Python 3.8+**
- **Blender 3.0+** instalado no sistema
- **ANTLR** configurado (para compilação)
- **Java** (para executar ANTLR)

## 📝 EXEMPLO DE USO

### **Caso de Uso: Gerar Leito Simples**

1. Execute: `python bed_wizard.py`
2. Escolha opção: `3`
3. Configure:
   - Diâmetro: `0.05 m`
   - Altura: `0.1 m`
   - Partículas: `100 esferas de 0.005 m`
4. Confirme: `s`
5. Aguarde a geração (1-5 minutos)
6. Modelo salvo em: `output/models/leito_blender.blend`

## 🎯 DIFERENÇAS DOS OUTROS MODOS

| Característica | Modo Interativo | Modo Template | Modo Blender |
|----------------|-----------------|---------------|--------------|
| **CFD** | ✅ Configurável | ✅ Configurável | ❌ Desabilitado |
| **Interface** | Questionário | Editor | Questionário |
| **Execução Blender** | ❌ Manual | ❌ Manual | ✅ Automática |
| **Formato Saída** | Personalizável | Personalizável | BLEND + STL |
| **Complexidade** | Média | Alta | Baixa |

## 🚨 TROUBLESHOOTING

### **Blender não encontrado**
```
erro: blender nao encontrado
instale o blender ou adicione ao path do sistema
```

**Solução:**
- Instale o Blender: https://www.blender.org/download/
- Ou adicione ao PATH do sistema

### **Timeout na execução**
```
erro: timeout na execucao do blender (limite: 5 minutos)
```

**Solução:**
- Reduza o número de partículas
- Simplifique a geometria
- Aumente o timeout no código (linha 745)

### **Arquivo JSON não encontrado**
```
erro: arquivo json nao encontrado
```

**Solução:**
- Verifique se o compilador ANTLR está instalado
- Execute manualmente: `python compiler/bed_compiler_antlr_standalone.py arquivo.bed`

## 📊 PERFORMANCE

| Parâmetro | Tempo Aproximado |
|-----------|------------------|
| 50 partículas | 30-60 segundos |
| 100 partículas | 1-2 minutos |
| 500 partículas | 3-5 minutos |
| 1000 partículas | 5-10 minutos |

## 🎓 PRÓXIMOS PASSOS

Após gerar o modelo 3D:
1. Abra no Blender: `File > Open > output/models/seu_modelo.blend`
2. Visualize a geometria
3. Exporte para outros formatos (STL, OBJ, FBX)
4. Use em simulações CFD externas
5. Imprima em 3D (formato STL)

## 📚 REFERÊNCIAS

- [Documentação do Blender](https://docs.blender.org/)
- [Proposta TCC](../refs/PropostaTCC_transcricao.txt)
- [Gramática DSL](grammar/Bed.g4)
- [Compilador ANTLR](compiler/bed_compiler_antlr_standalone.py)

---

*Última atualização: Janeiro 2025*  
*Versão: 1.0.0*
