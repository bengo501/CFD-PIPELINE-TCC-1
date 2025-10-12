# início rápido: wizard web

## como usar o wizard web completo

### 1. iniciar o sistema

**terminal 1 - backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**terminal 2 - frontend:**
```bash
cd frontend
npm run dev
```

### 2. acessar o wizard

abra no navegador: http://localhost:5173

clique na aba: **wizard interativo**

---

## 4 modos disponíveis

### opção 1: questionário interativo
**melhor para:** iniciantes, primeira vez

1. clique em "questionário interativo"
2. preencha os formulários passo a passo
3. veja preview 3d na confirmação
4. clique em "gerar arquivo .bed"

**tempo:** ~5 minutos

---

### opção 2: editor de template
**melhor para:** quem conhece a sintaxe .bed

1. clique em "editor de template"
2. edite o código diretamente
3. clique em "usar este template"
4. arquivo compilado automaticamente

**tempo:** ~2 minutos

---

### opção 3: modo blender
**melhor para:** geração de modelo 3d apenas

1. clique em "modo blender"
2. preencha parâmetros básicos
3. escolha formatos de exportação
4. modelo gerado em `output/models/`

**tempo:** ~3 minutos + tempo de geração

---

### opção 4: blender interativo
**melhor para:** iteração rápida

1. clique em "blender interativo"
2. preencha parâmetros
3. modelo gerado e blender abre automaticamente
4. edite diretamente no blender

**tempo:** ~3 minutos + abertura automática

---

## botões úteis

### ajuda
**quando usar:** dúvida sobre parâmetros

clique no botão "ajuda" para ver:
- descrição de cada parâmetro
- limites (min/max)
- exemplos práticos
- organizados por seção

---

### documentação
**quando usar:** primeira vez, referência completa

clique no botão "documentação" para ver:
- sobre o wizard
- explicação dos modos
- parâmetros principais
- dicas de uso
- formatos de exportação
- links úteis

---

## formatos de exportação

ao criar modelo blender, escolha formatos:

- **blend** → para editar no blender depois
- **glb** → para visualizar na web (usado pelo viewer)
- **obj** → para importar em outros programas
- **fbx** → para unity/unreal
- **stl** → para impressão 3d

**dica:** marque `blend,glb,obj` para máxima compatibilidade

---

## exemplo rápido

### criar primeiro leito (modo interativo)

1. acesse http://localhost:5173
2. clique em "wizard interativo"
3. clique em "questionário interativo"
4. use valores padrão (pressione enter em todos campos)
5. veja preview 3d
6. clique em "gerar arquivo .bed"
7. pronto! arquivo criado

**tempo total:** ~2 minutos

---

## valores recomendados

### para teste rápido
- diâmetro: 0.05m (5cm)
- altura: 0.1m (10cm)
- partículas: 50
- tempo: 5s

**geração:** ~1 minuto

### para modelo final
- diâmetro: 0.05m (5cm)
- altura: 0.1m (10cm)
- partículas: 500
- tempo: 10s

**geração:** ~5 minutos

### para simulação cfd
- incluir parâmetros cfd
- regime: laminar (para começar)
- velocidade: 0.1 m/s
- iterações: 1000

**simulação:** ~10 minutos

---

## onde encontrar os arquivos

### arquivos .bed
`output/`
- `meu_leito.bed` - arquivo de configuração
- `meu_leito.bed.json` - parâmetros compilados

### modelos 3d
`output/models/`
- `meu_leito.blend` - blender nativo
- `meu_leito.glb` - visualizador web
- `meu_leito.obj` - universal
- etc.

### simulações cfd
`output/openfoam/`
- caso openfoam completo
- resultados da simulação

---

## dicas

### começe simples
- use valores padrão primeiro
- teste com poucas partículas (50)
- aumente gradualmente

### use ajuda
- digite `?` em campos numéricos
- clique em "ajuda" para referência
- leia "documentação" uma vez

### escolha formato certo
- **web:** glb
- **edição:** blend
- **outros programas:** obj
- **impressão 3d:** stl

### iteração rápida
- use "blender interativo"
- ajuste e reabra rapidamente
- visualize imediatamente

---

## atalhos

### no wizard
- **enter:** usar valor padrão
- **tab:** próximo campo
- **?:** mostrar ajuda (campos numéricos)

### no blender (modo interativo)
- **scroll mouse:** zoom
- **botão meio + arrastar:** rotacionar
- **numpad 7:** vista superior
- **z:** mudar visualização
- **shift + a:** adicionar objeto

---

## solução de problemas

### backend não inicia
```bash
# verificar se porta 8000 está livre
netstat -ano | findstr :8000

# instalar dependências
cd backend
pip install -r requirements.txt
```

### frontend não inicia
```bash
# instalar dependências
cd frontend
npm install

# limpar cache
npm run dev -- --force
```

### blender não encontrado
- instalar blender 3.x+
- adicionar ao path do sistema
- ou especificar caminho em `executar_leito_headless.py`

### compilação falha
- verificar sintaxe do .bed
- ver mensagem de erro detalhada
- consultar template de exemplo

---

## workflow completo

### 1. criar leito
- usar wizard web
- escolher modo adequado
- configurar parâmetros

### 2. gerar modelo 3d
- selecionar formatos
- aguardar geração
- verificar em `output/models/`

### 3. visualizar
- abrir na aba "resultados"
- viewer 3d integrado
- ou abrir .blend no blender

### 4. simular (opcional)
- configurar parâmetros cfd
- executar simulação openfoam
- visualizar resultados no paraview

---

## próximos passos

após criar seu primeiro leito:

1. experimente diferentes geometrias
2. teste vários tipos de partículas
3. ajuste parâmetros de física
4. compare resultados
5. execute simulação cfd
6. analise resultados

---

## recursos adicionais

### documentação
- `RESUMO_WIZARD_COMPLETO.md` - guia completo
- `GUIA_FORMATOS_EXPORTACAO.md` - formatos detalhados
- `README.md` - documentação geral

### exemplos
- `dsl/examples/` - arquivos .bed de exemplo
- `output/` - arquivos gerados

### api
- http://localhost:8000/docs - documentação interativa
- swagger ui com todos endpoints

---

## suporte

**problemas?**
1. consulte documentação
2. verifique logs do backend
3. veja console do navegador
4. revise sintaxe do .bed

**dúvidas?**
1. clique em "ajuda" no wizard
2. leia "documentação"
3. consulte guias na raiz do projeto

---

**pronto para começar! crie seu primeiro leito empacotado agora!** 🚀

