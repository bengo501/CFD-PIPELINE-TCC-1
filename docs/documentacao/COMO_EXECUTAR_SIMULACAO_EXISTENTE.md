# como executar sua simulação cfd existente

## situação atual

você tem um caso openfoam **preparado mas não executado** em:

```
C:\Users\joxto\Downloads\CFD-PIPELINE-TCC-1\output\cfd\leito_interativo\
```

**status:**
- ✅ caso criado
- ✅ malha configurada  
- ✅ condições iniciais prontas
- ❌ simulação não executada (ainda não tem resultados)

**como sei?**
- só existe pasta `0/` (condições iniciais)
- não existem pastas `1/`, `2/`, etc (resultados)
- não existem logs de simulação

---

## como executar agora

### opção 1: via wsl (recomendado)

**passo 1: abrir wsl**
```powershell
wsl
```

**passo 2: navegar até o caso**
```bash
cd /mnt/c/Users/joxto/Downloads/CFD-PIPELINE-TCC-1/output/cfd/leito_interativo
```

**passo 3: carregar openfoam**
```bash
source /opt/openfoam11/etc/bashrc
```

**passo 4: executar simulação**
```bash
./Allrun
```

**aguardar:**
- pode levar 5-30 minutos
- logs aparecerão na tela
- verá progresso da simulação

**verificar conclusão:**
```bash
ls -d [0-9]* | sort -n
```

**saída esperada:**
```
0
1
2
3
...
100
```

se tiver várias pastas numeradas → ✅ simulação executou!

---

### opção 2: passo a passo (debug)

**para mais controle:**

```bash
cd /mnt/c/Users/joxto/Downloads/CFD-PIPELINE-TCC-1/output/cfd/leito_interativo

source /opt/openfoam11/etc/bashrc

# 1. gerar malha de fundo
blockMesh

# 2. refinar malha ao redor do leito
snappyHexMesh -overwrite

# 3. verificar qualidade
checkMesh

# 4. executar simulação
simpleFoam
```

---

### opção 3: via interface web (futuro)

**quando implementado:**

```
1. abrir http://localhost:5173
2. clicar em "simulação cfd"
3. selecionar caso existente
4. clicar em "executar"
5. monitorar na interface
```

**atualmente:**
- pode criar novos casos via web
- execução ainda precisa ser no wsl

---

## onde ficarão os resultados

### após executar

```
output/cfd/leito_interativo/
├── 0/                      # inicial (já existe)
│   ├── U
│   └── p
├── 1/                      # ← NOVO (após executar)
│   ├── U                   # velocidade em t=1
│   ├── p                   # pressão em t=1
│   └── phi
├── 2/                      # ← NOVO
├── 3/                      # ← NOVO
├── ...
├── 100/                    # ← NOVO (tempo final)
│   ├── U                   # ← ESTES SÃO OS RESULTADOS!
│   ├── p
│   └── phi
├── log.simpleFoam          # ← NOVO (log da simulação)
└── caso.foam
```

---

## como visualizar resultados

### após executar no wsl

**ainda no wsl:**

```bash
# criar arquivo para paraview (se não existe)
touch caso.foam

# abrir paraview
paraview caso.foam &
```

**ou no windows:**

```
1. abrir paraview para windows
2. file → open
3. navegar até: output\cfd\leito_interativo\
4. abrir: caso.foam
5. clicar "apply"
6. escolher variável: U (velocidade) ou p (pressão)
7. visualizar campo colorido
```

---

## verificar se simulação está executando

### durante execução

**em outro terminal wsl:**

```bash
cd /mnt/c/Users/joxto/Downloads/CFD-PIPELINE-TCC-1/output/cfd/leito_interativo

# ver log em tempo real
tail -f log.simpleFoam
```

**ou verificar pastas:**

```bash
watch -n 5 'ls -d [0-9]* 2>/dev/null | sort -n | tail -5'
```

isso mostra as últimas 5 pastas de tempo, atualizando a cada 5s

---

## tempo esperado

para o seu caso `leito_interativo`:

**estimativa:**
- malha: ~2-5 minutos
- simulação: ~5-15 minutos
- **total: ~7-20 minutos**

---

## troubleshooting

### "source: not found"

**solução:**
```bash
# verificar se openfoam está instalado
ls /opt/openfoam11

# se não existe:
# instalar via scripts/automation/install_openfoam.py
```

### "./Allrun: permission denied"

**solução:**
```bash
chmod +x Allrun
./Allrun
```

### "no such file or directory"

**verificar se está no diretório certo:**
```bash
pwd
# deve mostrar: /mnt/c/Users/joxto/Downloads/CFD-PIPELINE-TCC-1/output/cfd/leito_interativo

ls Allrun
# deve mostrar: Allrun
```

---

## comando rápido completo

**copiar e colar no wsl:**

```bash
cd /mnt/c/Users/joxto/Downloads/CFD-PIPELINE-TCC-1/output/cfd/leito_interativo && source /opt/openfoam11/etc/bashrc && ./Allrun
```

**isso irá:**
1. navegar até o caso
2. carregar openfoam
3. executar simulação completa
4. criar resultados em pastas numeradas
5. criar arquivo caso.foam

---

## resumo

### onde ficam os resultados

**antes de executar:**
```
output/cfd/leito_interativo/
└── 0/  (apenas condições iniciais)
```

**depois de executar:**
```
output/cfd/leito_interativo/
├── 0/  (condições iniciais)
├── 1/, 2/, 3/, ... N/  (← RESULTADOS AQUI!)
└── log.simpleFoam  (log da simulação)
```

### para visualizar

**precisa:**
1. executar simulação primeiro (via wsl)
2. abrir caso.foam no paraview
3. escolher campo (U ou p)
4. ver resultado colorido

### seu próximo passo

```bash
# 1. abrir wsl
wsl

# 2. executar simulação
cd /mnt/c/Users/joxto/Downloads/CFD-PIPELINE-TCC-1/output/cfd/leito_interativo
source /opt/openfoam11/etc/bashrc
./Allrun

# 3. aguardar (5-20 minutos)

# 4. visualizar
paraview caso.foam &
```

**pronto!** você verá os campos de velocidade e pressão do escoamento através do leito empacotado! 🌊

