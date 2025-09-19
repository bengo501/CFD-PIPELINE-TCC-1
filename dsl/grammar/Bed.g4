grammar Bed;

// regra principal - um arquivo .bed
bedFile: section+ EOF;

// secoes principais do arquivo .bed
section: bedSection 
       | lidsSection 
       | particlesSection 
       | packingSection 
       | exportSection 
       | cfdSection;

// secao bed - define geometria do leito cilindrico
bedSection: 'bed' '{' bedProperty+ '}';
bedProperty: 'diameter' '=' NUMBER UNIT ';'         # bedDiameter
           | 'height' '=' NUMBER UNIT ';'           # bedHeight  
           | 'wall_thickness' '=' NUMBER UNIT ';'   # bedWallThickness
           | 'clearance' '=' NUMBER UNIT ';'        # bedClearance
           | 'material' '=' STRING ';'              # bedMaterial
           | 'roughness' '=' NUMBER UNIT ';'        # bedRoughness;

// secao lids - define tampas superior e inferior
lidsSection: 'lids' '{' lidsProperty+ '}';
lidsProperty: 'top_type' '=' lidType ';'            # lidsTopType
            | 'bottom_type' '=' lidType ';'         # lidsBottomType
            | 'top_thickness' '=' NUMBER UNIT ';'   # lidsTopThickness
            | 'bottom_thickness' '=' NUMBER UNIT ';' # lidsBottomThickness
            | 'seal_clearance' '=' NUMBER UNIT ';'  # lidsSealClearance;

lidType: 'flat' | 'hemispherical' | 'none';

// secao particles - define particulas e suas propriedades
particlesSection: 'particles' '{' particlesProperty+ '}';
particlesProperty: 'kind' '=' particleKind ';'          # particlesKind
                 | 'diameter' '=' NUMBER UNIT ';'       # particlesDiameter
                 | 'count' '=' INTEGER ';'              # particlesCount
                 | 'target_porosity' '=' NUMBER ';'     # particlesTargetPorosity
                 | 'density' '=' NUMBER UNIT ';'        # particlesDensity
                 | 'mass' '=' NUMBER UNIT ';'           # particlesMass
                 | 'restitution' '=' NUMBER ';'         # particlesRestitution
                 | 'friction' '=' NUMBER ';'            # particlesFriction
                 | 'rolling_friction' '=' NUMBER ';'    # particlesRollingFriction
                 | 'linear_damping' '=' NUMBER ';'      # particlesLinearDamping
                 | 'angular_damping' '=' NUMBER ';'     # particlesAngularDamping
                 | 'seed' '=' INTEGER ';'               # particlesSeed;

particleKind: 'sphere' | 'cube' | 'cylinder';

// secao packing - controle do empacotamento fisico
packingSection: 'packing' '{' packingProperty+ '}';
packingProperty: 'method' '=' packingMethod ';'        # packingMethod
               | 'gravity' '=' NUMBER UNIT ';'         # packingGravity
               | 'substeps' '=' INTEGER ';'            # packingSubsteps
               | 'iterations' '=' INTEGER ';'          # packingIterations
               | 'damping' '=' NUMBER ';'              # packingDamping
               | 'rest_velocity' '=' NUMBER UNIT ';'   # packingRestVelocity
               | 'max_time' '=' NUMBER UNIT ';'        # packingMaxTime
               | 'collision_margin' '=' NUMBER UNIT ';' # packingCollisionMargin;

packingMethod: 'rigid_body';

// secao export - configuracao de exportacao
exportSection: 'export' '{' exportProperty+ '}';
exportProperty: 'formats' '=' '[' formatList ']' ';'   # exportFormats
              | 'units' '=' STRING ';'                 # exportUnits
              | 'scale' '=' NUMBER ';'                 # exportScale
              | 'wall_mode' '=' wallMode ';'           # exportWallMode
              | 'fluid_mode' '=' fluidMode ';'         # exportFluidMode
              | 'manifold_check' '=' BOOLEAN ';'       # exportManifoldCheck
              | 'merge_distance' '=' NUMBER UNIT ';'   # exportMergeDistance;

formatList: STRING (',' STRING)*;
wallMode: 'surface' | 'solid';
fluidMode: 'none' | 'cavity';

// secao cfd - parametros opcionais para CFD
cfdSection: 'cfd' '{' cfdProperty+ '}';
cfdProperty: 'regime' '=' cfdRegime ';'                # cfdRegime
           | 'inlet_velocity' '=' NUMBER UNIT ';'      # cfdInletVelocity
           | 'fluid_density' '=' NUMBER UNIT ';'       # cfdFluidDensity
           | 'fluid_viscosity' '=' NUMBER UNIT ';'     # cfdFluidViscosity
           | 'max_iterations' '=' INTEGER ';'          # cfdMaxIterations
           | 'convergence_criteria' '=' NUMBER ';'     # cfdConvergenceCriteria
           | 'write_fields' '=' BOOLEAN ';'            # cfdWriteFields;

cfdRegime: 'laminar' | 'turbulent_rans';

// tokens lexicos
NUMBER: [0-9]+ ('.' [0-9]+)?;
INTEGER: [0-9]+;
UNIT: 'm' | 'cm' | 'mm' | 'kg' | 'g' | 's' | 'Pa' | 'N' | 'm/s' | 'kg/m3' | 'Pa.s';
STRING: '"' (~["\r\n])* '"';
BOOLEAN: 'true' | 'false';

// ignorar espacos e comentarios
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;
BLOCK_COMMENT: '/*' .*? '*/' -> skip;
