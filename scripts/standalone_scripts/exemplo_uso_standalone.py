#!/usr/bin/env python3

# exemplo de uso do script standalone para gerar leitos de extração

# importa o script standalone
from leito_standalone import LeitoStandalone

def exemplo_basico():
    # exemplo básico com parâmetros padrão
    print("===== Exemplo Básico =====")
    
    gerador = LeitoStandalone()
    
    # Gerar leito com parâmetros padrão
    gerador.gerar_leito(
        output_file="leito_basico.blend"
    )

def exemplo_personalizado():
    # exemplo com parâmetros personalizados
    print("======Exemplo Personalizado=====")
    
    gerador = LeitoStandalone()
    
    # Gerar leito personalizado
    gerador.gerar_leito(
        altura=0.15,              # 15 cm de altura
        diametro=0.03,            # 3 cm de diâmetro
        espessura_parede=0.003,   # 3 mm de espessura
        num_particulas=50,        # 50 partículas
        tamanho_particula=0.002,  # 2 mm de tamanho
        massa_particula=0.2,      # 200g de massa
        tipo_particula="cilindros", # Cilindros em vez de esferas
        cor_leito="vermelho",     # Leito vermelho
        cor_particulas="amarelo", # Partículas amarelas
        output_file="leito_personalizado.blend"
    )

def exemplo_multiplos():
    # exemplo gerando múltiplos leitos
        print("======Exemplo Múltiplos Leitos=====")
    
    gerador = LeitoStandalone()
    
    # Configurações diferentes
    configs = [
        {
            "nome": "leito_pequeno",
            "altura": 0.05,
            "diametro": 0.015,
            "num_particulas": 20,
            "tipo_particula": "cubos"
        },
        {
            "nome": "leito_grande",
            "altura": 0.2,
            "diametro": 0.05,
            "num_particulas": 100,
            "tipo_particula": "esferas"
        },
        {
            "nome": "leito_medio",
            "altura": 0.1,
            "diametro": 0.025,
            "num_particulas": 30,
            "tipo_particula": "cilindros"
        }
    ]
    
    for config in configs:
        print(f"Gerando {config['nome']}")
        gerador.gerar_leito(
            altura=config["altura"],
            diametro=config["diametro"],
            num_particulas=config["num_particulas"],
            tipo_particula=config["tipo_particula"],
            output_file=f"{config['nome']}.blend"
        )

def exemplo_estudo_parametros():
    # exemplo para estudo de parâmetros
    print("======Exemplo Estudo de Parametros=====")
    
    gerador = LeitoStandalone()
    
    # variar numero de particulas
    for num_parts in [10, 30, 50, 100]:
        print(f"Gerando leito com {num_parts} particulas")
        gerador.gerar_leito(
            num_particulas=num_parts,
            output_file=f"leito_{num_parts}particulas.blend"
        )


    for tamanho in [0.0005, 0.001, 0.002, 0.005]:
            print(f"Gerando leito com particulas de {tamanho*1000:.1f}mm")
        gerador.gerar_leito(
            tamanho_particula=tamanho,
            output_file=f"leito_particula_{tamanho*1000:.1f}mm.blend"
        )

if __name__ == "__main__":
    print("iniciando exemplos de uso do gerador standalone")
    print()
    
    try:
        # executar exemplos
        exemplo_basico()
        print()
        exemplo_personalizado()
        print()
        exemplo_multiplos()
        print()
        exemplo_estudo_parametros()
        print()
        
        print("todos os exemplos executados com sucesso")
        print("verifique os arquivos .blend gerados na pasta atual")
        
    except Exception as e:
        print(f"erro durante a execucao: {e}")
        print("certifique-se de que o Blender está instalado e acessivel")
