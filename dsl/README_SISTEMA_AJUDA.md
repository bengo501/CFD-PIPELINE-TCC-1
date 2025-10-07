# sistema de ajuda do bed wizard

## resumo das melhorias

o `bed_wizard.py` agora possui um **sistema completo de ajuda** com:

1. **menu de ajuda interativo** - opcao 4 no menu principal
2. **ajuda contextual** - digite `?` ao preencher qualquer parametro
3. **validacao automatica** - valores minimos e maximos para cada parametro
4. **informacoes detalhadas** - descricao, range permitido e exemplos

---

## como usar

### 1. menu de ajuda geral

ao executar `python bed_wizard.py`, escolha a opcao **4 - menu de ajuda**:

```
escolha o modo de criacao:
1. questionario interativo - responda perguntas passo a passo
2. editor de template - edite um arquivo padrao
3. modo blender - apenas geracao de modelo 3d (sem cfd)
4. menu de ajuda - informacoes sobre parametros
5. sair

escolha (1-5): 4
```

depois escolha uma secao para ver todos os parametros:

```
1. geometria do leito
2. tampas
3. particulas
4. empacotamento
5. exportacao
6. simulacao cfd
0. voltar ao menu principal
```

**exemplo de saida:**

```
[diameter]
  descricao: diametro interno do leito cilindrico
  range: 0.01m a 2.0m
  exemplo: leito de 5cm = 0.05m

[height]
  descricao: altura total do leito cilindrico
  range: 0.01m a 5.0m
  exemplo: leito de 10cm = 0.1m
```

---

### 2. ajuda contextual (digite ?)

durante o preenchimento dos parametros, digite `?` para ver ajuda:

```
--- geometria do leito ---

  [ajuda] diametro interno do leito cilindrico
  [range] minimo: 0.01m, maximo: 2.0m
  [exemplo] leito de 5cm = 0.05m

diametro do leito [0.05 m] (? para ajuda): ?

  [ajuda] diametro interno do leito cilindrico
  [range] minimo: 0.01m, maximo: 2.0m
  [exemplo] leito de 5cm = 0.05m

diametro do leito [0.05 m] (? para ajuda):
```

---

### 3. validacao automatica

o wizard valida automaticamente se o valor esta dentro do range:

**valor muito baixo:**
```
diametro do leito [0.05 m] (? para ajuda): 0.001
  aviso: valor muito baixo! minimo: 0.01m
```

**valor muito alto:**
```
diametro do leito [0.05 m] (? para ajuda): 5.0
  aviso: valor muito alto! maximo: 2.0m
```

**valor correto:**
```
diametro do leito [0.05 m] (? para ajuda): 0.08
(continua para proximo parametro)
```

---

## parametros com validacao

### secao bed (geometria do leito)

| parametro | min | max | unidade | descricao |
|-----------|-----|-----|---------|-----------|
| diameter | 0.01 | 2.0 | m | diametro interno do leito cilindrico |
| height | 0.01 | 5.0 | m | altura total do leito cilindrico |
| wall_thickness | 0.0001 | 0.1 | m | espessura da parede do cilindro |
| clearance | 0.0 | 1.0 | m | espaco livre acima das particulas |
| roughness | 0.0 | 0.01 | m | rugosidade da superficie interna |

### secao lids (tampas)

| parametro | min | max | unidade | descricao |
|-----------|-----|-----|---------|-----------|
| top_thickness | 0.0001 | 0.1 | m | espessura da tampa superior |
| bottom_thickness | 0.0001 | 0.1 | m | espessura da tampa inferior |
| seal_clearance | 0.0 | 0.01 | m | folga entre tampa e parede |

### secao particles (particulas)

| parametro | min | max | unidade | descricao |
|-----------|-----|-----|---------|-----------|
| diameter | 0.0001 | 0.5 | m | diametro das particulas esfericas |
| count | 1 | 10000 | - | quantidade total de particulas |
| target_porosity | 0.1 | 0.9 | - | porosidade desejada (0-1) |
| density | 100.0 | 20000.0 | kg/m3 | densidade do material das particulas |
| mass | 0.0 | 1000.0 | g | massa individual de cada particula |
| restitution | 0.0 | 1.0 | - | coeficiente de restituicao (quique) |
| friction | 0.0 | 1.0 | - | coeficiente de atrito entre particulas |
| rolling_friction | 0.0 | 1.0 | - | resistencia ao rolamento |
| linear_damping | 0.0 | 1.0 | - | amortecimento do movimento linear |
| angular_damping | 0.0 | 1.0 | - | amortecimento da rotacao |
| seed | 0 | 99999 | - | semente para geracao aleatoria |

### secao packing (empacotamento)

| parametro | min | max | unidade | descricao |
|-----------|-----|-----|---------|-----------|
| gravity | -50.0 | 50.0 | m/s2 | aceleracao da gravidade |
| substeps | 1 | 100 | - | subdivisoes de cada frame |
| iterations | 1 | 100 | - | iteracoes do solver por substep |
| damping | 0.0 | 1.0 | - | amortecimento global da simulacao |
| rest_velocity | 0.0001 | 1.0 | m/s | velocidade considerada repouso |
| max_time | 0.1 | 60.0 | s | tempo maximo de simulacao |
| collision_margin | 0.00001 | 0.01 | m | margem de deteccao de colisao |

### secao export (exportacao)

| parametro | min | max | unidade | descricao |
|-----------|-----|-----|---------|-----------|
| scale | 0.001 | 1000.0 | - | fator de escala na exportacao |
| merge_distance | 0.0 | 0.1 | m | distancia para mesclar vertices |

### secao cfd (simulacao)

| parametro | min | max | unidade | descricao |
|-----------|-----|-----|---------|-----------|
| inlet_velocity | 0.001 | 100.0 | m/s | velocidade do fluido na entrada |
| fluid_density | 0.1 | 2000.0 | kg/m3 | densidade do fluido |
| fluid_viscosity | 1e-6 | 1.0 | Pa.s | viscosidade dinamica do fluido |
| max_iterations | 10 | 100000 | - | numero maximo de iteracoes |
| convergence_criteria | 1e-10 | 1e-2 | - | criterio de convergencia (residuo) |

---

## exemplos de valores comuns

### materiais de particulas

- **vidro**: densidade = 2500 kg/m3
- **aco**: densidade = 7850 kg/m3
- **plastico**: densidade = 950 kg/m3
- **aluminio**: densidade = 2700 kg/m3
- **areia**: densidade = 1600 kg/m3

### materiais de parede

- **steel** (aco): resistente e condutor
- **glass** (vidro): transparente, bom para visualizacao
- **plastic** (plastico): leve e isolante
- **aluminum** (aluminio): leve e condutor

### fluidos para cfd

- **ar**: densidade = 1.225 kg/m3, viscosidade = 1.8e-5 Pa.s
- **agua**: densidade = 1000 kg/m3, viscosidade = 1e-3 Pa.s
- **oleo**: densidade = 900 kg/m3, viscosidade = 0.1 Pa.s

### configuracoes de empacotamento

- **rapido** (100 particulas): 10 substeps, 10 iterations, 5s
- **medio** (500 particulas): 20 substeps, 15 iterations, 10s
- **preciso** (1000+ particulas): 50 substeps, 20 iterations, 30s

### gravidade em diferentes ambientes

- **terra**: -9.81 m/s2
- **lua**: -1.62 m/s2
- **marte**: -3.71 m/s2
- **sem gravidade**: 0.0 m/s2

---

## dicas de uso

### 1. comece com valores padrao

pressione **enter** ou **espaco** para aceitar valores padrao. isso e util para:
- testar o sistema rapidamente
- ter um ponto de partida confiavel
- entender os ranges tipicos

### 2. use a ajuda contextual

digite **?** sempre que tiver duvida sobre um parametro. a ajuda mostra:
- o que o parametro significa
- valores minimos e maximos permitidos
- exemplos praticos de uso

### 3. valide seus valores

o sistema valida automaticamente se os valores estao dentro dos limites, mas considere:
- **particulas muito pequenas** podem deixar a simulacao lenta
- **muitas particulas** aumentam o tempo de processamento
- **valores extremos** podem causar instabilidade na fisica

### 4. consulte o menu de ajuda

antes de criar seu leito, visite o **menu de ajuda** (opcao 4) para:
- explorar todos os parametros disponiveis
- entender as relacoes entre parametros
- ver exemplos de valores para diferentes casos de uso

---

## alteracoes no codigo

### 1. novo dicionario `param_help`

adicionado no `__init__` da classe `BedWizard`:
```python
self.param_help = {
    'bed.diameter': {
        'desc': 'diametro interno do leito cilindrico',
        'min': 0.01, 'max': 2.0, 'unit': 'm',
        'exemplo': 'leito de 5cm = 0.05m'
    },
    # ... mais 40+ parametros
}
```

### 2. novo metodo `show_param_help()`

```python
def show_param_help(self, param_key: str):
    """mostrar ajuda detalhada sobre um parametro"""
    if param_key in self.param_help:
        info = self.param_help[param_key]
        print(f"\n  [ajuda] {info['desc']}")
        # mostra range e exemplo
```

### 3. `get_number_input()` atualizado

- novo parametro: `param_key` para identificar o parametro
- mostra ajuda automaticamente ao entrar no campo
- permite digitar `?` para ver ajuda novamente
- valida min/max automaticamente

### 4. novo metodo `show_help_menu()`

menu interativo completo para explorar todos os parametros por secao

### 5. menu principal atualizado

- nova opcao 4: menu de ajuda
- opcao sair mudou de 4 para 5

---

## beneficios

1. **facilita o aprendizado** - usuarios novos podem explorar parametros antes de criar
2. **previne erros** - validacao automatica evita valores invalidos
3. **melhora a experiencia** - ajuda contextual sempre disponivel
4. **documenta inline** - descricoes e exemplos no proprio wizard
5. **aumenta a produtividade** - menos tentativa e erro, mais acertos

---

*ultima atualizacao: outubro 2024*  
*versao do wizard: 2.0.0*
