# este ficheiro define a dependencia fastapi que traduz o cabecalho http em numero inteiro
# o nome do cabecalho e x user id mas no codigo usamos alias para o hifen
# o frontend guarda o id escolhido no local storage e o axios repete em cada pedido
# assim o backend pode filtrar linhas sql por utilizador sem sessao de login completa
from fastapi import Header


def get_active_user_id(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
) -> int:
    # esta funcao devolve sempre um inteiro entre 1 e 99
    # parametro x user id vem do cliente ou fica none se o cabecalho nao existir
    # passo um se none ou string vazia devolvemos 1 para nao quebrar testes antigos
    if x_user_id is None or str(x_user_id).strip() == "":
        return 1
    # passo dois tentamos converter texto para inteiro
    try:
        uid = int(str(x_user_id).strip())
    except ValueError:
        # texto invalido cai aqui e usamos o mesmo default 1
        return 1
    # passo tres cortamos valores absurdos
    # zero ou negativo vira 1
    if uid < 1:
        return 1
    # numeros muito grandes viram 99 para evitar ids inventados enormes
    if uid > 99:
        return 99
    # caso normal devolvemos o proprio uid
    return uid
