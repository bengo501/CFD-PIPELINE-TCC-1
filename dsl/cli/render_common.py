# mensagens rich partilhadas pelos comandos typer
# este modulo nao gera geometria so formata texto no terminal
from __future__ import annotations

# annotations adia avaliacao de tipos para o interpretador aceitar referencias adiante
from typing import Optional

# console e o objeto que sabe imprimir com cores e quebras de linha
from rich.console import Console
# panel desenha uma caixa com titulo em volta de um texto
from rich.panel import Panel
# text permite dar estilo a uma string sem perder o conteudo literal
from rich.text import Text

# variavel de modulo guarda uma unica consola para nao criar varias instancias
# none significa ainda nao criada
_console: Optional[Console] = None


def get_shared_console() -> Console:
    # devolve sempre a mesma consola rich para o processo inteiro
    # global diz que vamos ler e escrever a variavel de modulo _console
    global _console
    # primeira chamada cria a consola
    if _console is None:
        # highlight false evita colorir numeros e caminhos como codigo
        # soft wrap true deixa linhas longas quebrarem sem cortar palavras
        _console = Console(highlight=False, soft_wrap=True)
    # chamadas seguintes reutilizam o mesmo objeto
    return _console


def render_success(title: str, body: str) -> None:
    # mostra um painel verde para feedback positivo
    # title e o titulo curto do painel
    # body e o texto principal pode ser multilinha
    c = get_shared_console()
    # border style green colore a moldura
    # title align left alinha o titulo a esquerda
    c.print(Panel(body, title=title, border_style="green", title_align="left"))


def render_error(title: str, body: str) -> None:
    # igual ao sucesso mas moldura vermelha para erros
    c = get_shared_console()
    c.print(Panel(body, title=title, border_style="red", title_align="left"))


def render_info(title: str, body: str) -> None:
    # painel discreto para informacao neutra
    c = get_shared_console()
    # dim reduz contraste visual
    c.print(Panel(body, title=title, border_style="dim", title_align="left"))


def print_equivalent_command(cmd: str) -> None:
    # depois de um fluxo interativo mostramos o comando cli que repetiria o mesmo
    # cmd e a linha completa ja montada com espacos entre argumentos
    c = get_shared_console()
    # Text aplica estilo cyan so ao conteudo interno
    # Panel envolve para destacar do resto do log
    c.print(
        Panel(
            Text(cmd, style="cyan"),
            title="comando equivalente",
            border_style="rgb(95,25,35)",
        )
    )
