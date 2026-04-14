# tutoriais openfoam (versionados)

casos minimos para validar instalacao e estudar fluxos classicos. pensados para **openfoam.org** (ex.: openfoam11) em **linux** ou **wsl2**.

| pasta | solver | objetivo |
|-------|--------|----------|
| [cavity-icoFoam](cavity-icoFoam/) | `icoFoam` | cavidade com tampa arrastada — benchmark classico (literatura: ghia et al. 1982; tutoriais openfoam) |
| [channel-simpleFoam](channel-simpleFoam/) | `simpleFoam` | canal 2d estacionario — esquemas simple/piso em malha estruturada |
| [sphere-snappyHexMesh](sphere-snappyHexMesh/) | malha | `blockMesh` + `snappyHexMesh` com `searchableSphere` (sem stl externo) |

## requisitos

- openfoam carregado (`source /opt/openfoam11/etc/bashrc` ou equivalente)
- executar sempre **dentro** da pasta do caso

## uso rapido

### cavity (icofoam)

```bash
cd tutorial/cavity-icoFoam
./Allrun
# ou: blockMesh && icoFoam
```

pos-processamento: `paraFoam` ou `postProcess -func 'sampleDict' ...` conforme a tua versao.

### canal (simplefoam)

```bash
cd tutorial/channel-simpleFoam
./Allrun
```

### snappy (esfera)

```bash
cd tutorial/sphere-snappyHexMesh
./Allmesh
# malha em constant/polyMesh; inspecionar com checkMesh
```

## notas

- **cavity**: `nu`, tamanho do dominio e velocidade da tampa definem o reynolds; ajuste `nu` em `constant/physicalProperties` para estudar diferentes re.
- **simplefoam**: caso estacionario; `endTime` e `deltaT` sao passos pseudotempo simples.
- **snappy**: `locationInMesh` deve ficar **fora** da esfera mas **dentro** do dominio de fundo; se falhar, ajuste o ponto em `snappyHexMeshDict`.

## relacao com o resto do projeto

estes casos sao **independentes** do pipeline leito/blender. o gerador em `scripts/openfoam_scripts/setup_openfoam_case.py` produz casos **com stl** do leito e `snappyHexMesh` proprio; aqui o exemplo snappy usa **geometria implicita** (`searchableSphere`) para ser pequeno e autocontido no git.
