"""
interface do wizard no terminal: layout limpo, tipo barra de endereco + tabela de opcoes.
usa rich se estiver instalado; caso contrario, modo texto simples compativel.
"""

from __future__ import annotations

import os
from typing import List, Sequence, Tuple

try:
    from rich import box
    from rich.align import Align
    from rich.console import Console
    from rich.markup import escape
    from rich.panel import Panel
    from rich.prompt import Confirm, IntPrompt, Prompt
    from rich.rule import Rule
    from rich.table import Table
    from rich.text import Text
    from rich.theme import Theme

    _HAS_RICH = True
except ImportError:
    escape = None  # type: ignore
    _HAS_RICH = False

MenuRow = Tuple[str, str, str]


_WIZARD_THEME = Theme(
    {
        "wizard.chrome": "bold white on rgb(95,25,35)",
        "wizard.path": "dim italic",
        "wizard.path_seg": "bold rgb(240,212,168)",
        "wizard.accent": "bold rgb(240,212,168)",
        "wizard.section": "bold rgb(240,212,168)",
        "wizard.muted": "dim",
        "wizard.hint": "italic dim",
        "wizard.warn": "yellow",
        "wizard.err": "bold red",
        "wizard.ok": "green",
        "wizard.label": "bold",
    }
)


class PlainWizardUi:
    """fallback sem rich — mantem o wizard utilizavel."""

    def __init__(self) -> None:
        self._rich = False

    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def header(self, title: str, subtitle: str = "") -> None:
        print("=" * 62)
        print(f"  {title}")
        print("=" * 62)
        if subtitle:
            print(f"  {subtitle}")
        print()

    def section(self, title: str) -> None:
        print(f"\n--- {title} ---")

    def breadcrumbs(self, *parts: str) -> None:
        if not parts:
            return
        print("  " + " > ".join(parts))
        print()

    def println(self, *args, **kwargs) -> None:
        print(*args, **kwargs)

    def muted(self, msg: str) -> None:
        print(f"  {msg}")

    def hint(self, msg: str) -> None:
        print(f"  {msg}")

    def warn(self, msg: str) -> None:
        print(f"  aviso: {msg}")

    def err(self, msg: str) -> None:
        print(f"  erro: {msg}")

    def ok(self, msg: str) -> None:
        print(f"  {msg}")

    def param_help(self, lines: Sequence[str]) -> None:
        for line in lines:
            print(f"  {line}")
        print()

    def pause(self, msg: str = "pressione enter para continuar...") -> None:
        input(f"\n{msg}")

    def ask_line(self, prompt: str) -> str:
        return input(prompt)

    def pick_from_list(self, caption: str, options: List[str], default_index: int = 0) -> str:
        print(f"\n{caption}")
        for i, option in enumerate(options):
            print(f"  {i + 1}. {option}")
        while True:
            try:
                raw = input(f"\nescolha (1-{len(options)}) [{default_index + 1}]: ").strip()
                if not raw:
                    return options[default_index]
                idx = int(raw) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                print(f"  aviso: escolha entre 1 e {len(options)}!")
            except ValueError:
                print("  aviso: digite um numero valido!")

    def confirm(self, message: str, default: bool = True) -> bool:
        default_str = "sim" if default else "nao"
        while True:
            value = input(f"{message} (s/n) [{default_str}]: ").strip()
            if not value:
                return default
            value = value.lower()
            if value in ("s", "sim", "y", "yes"):
                return True
            if value in ("n", "nao", "no"):
                return False
            print("  aviso: digite 's' para sim ou 'n' para nao!")

    def render_main_menu(self, rows: Sequence[MenuRow], footer_hint: str) -> None:
        print("modos disponiveis (digite o numero):")
        print()
        for key, titulo, desc in rows:
            print(f"  [{key}]  {titulo}")
            print(f"         {desc}")
            print()
        print(footer_hint)
        print()

    def render_help_section_menu(self, entries: Sequence[Tuple[str, str]], back_key: str = "0") -> None:
        print("secoes de ajuda:")
        for key, label in entries:
            print(f"  {key}. {label}")
        print(f"  {back_key}. voltar ao menu principal")
        print()


class RichWizardUi:
    """terminal com paineis, tabelas e prompts alinhados ao estilo web (chrome + conteudo)."""

    def __init__(self) -> None:
        self._rich = True
        # soft_wrap evita quebrar layout em caminhos longos
        self.console = Console(theme=_WIZARD_THEME, highlight=False, soft_wrap=True)

    def clear(self) -> None:
        self.console.clear()

    def header(self, title: str, subtitle: str = "") -> None:
        chrome = Text()
        chrome.append(" bedflow atlas ", style="wizard.chrome")
        chrome.append(" ", style="")
        chrome.append("wizard://", style="wizard.path")
        seg = title.strip().lower().replace(" ", "-")[:48]
        chrome.append(seg if seg else "inicio", style="wizard.path_seg")
        bar = Panel(
            Align.left(chrome),
            box=box.HEAVY,
            border_style="rgb(95,25,35)",
            padding=(0, 1),
        )
        self.console.print(bar)
        if subtitle:
            self.console.print(Text(subtitle, style="wizard.muted"), end="\n\n")
        else:
            self.console.print()

    def section(self, title: str) -> None:
        self.console.print()
        self.console.print(Rule(Text(title.lower(), style="wizard.section"), style="rgb(95,25,35)"))

    def breadcrumbs(self, *parts: str) -> None:
        if not parts:
            return
        t = Text()
        t.append("wizard://", style="wizard.path")
        for i, p in enumerate(parts):
            if i:
                t.append(" / ", style="wizard.muted")
            t.append(p.lower(), style="wizard.path_seg")
        self.console.print(Align.left(t))
        self.console.print()

    def println(self, *args, **kwargs) -> None:
        self.console.print(*args, **kwargs)

    def muted(self, msg: str) -> None:
        self.console.print(Text(msg, style="wizard.muted"))

    def hint(self, msg: str) -> None:
        self.console.print(Text(msg, style="wizard.hint"))

    def warn(self, msg: str) -> None:
        self.console.print(Text(f"aviso: {msg}", style="wizard.warn"))

    def err(self, msg: str) -> None:
        self.console.print(Text(f"erro: {msg}", style="wizard.err"))

    def ok(self, msg: str) -> None:
        self.console.print(Text(msg, style="wizard.ok"))

    def param_help(self, lines: Sequence[str]) -> None:
        body = "\n".join(lines)
        self.console.print(
            Panel(
                body,
                title="ajuda",
                title_align="left",
                border_style="dim",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )

    def pause(self, msg: str = "pressione enter para continuar...") -> None:
        self.console.input(f"\n[wizard.muted]{msg}[/] ")

    def ask_line(self, prompt: str) -> str:
        return Prompt.ask(escape(prompt), default="", show_default=False, console=self.console)

    def pick_from_list(self, caption: str, options: List[str], default_index: int = 0) -> str:
        self.console.print()
        self.console.print(Text(caption, style="wizard.label"))
        table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="wizard.section", border_style="dim")
        table.add_column("#", justify="right", style="wizard.muted", width=4)
        table.add_column("opcao", style="")
        for i, opt in enumerate(options):
            table.add_row(str(i + 1), opt)
        self.console.print(table)
        self.console.print()
        while True:
            try:
                n = IntPrompt.ask(
                    f"[wizard.label]numero[/] [wizard.muted](1-{len(options)}, enter={default_index + 1})[/]",
                    default=default_index + 1,
                    console=self.console,
                )
                idx = int(n) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                self.warn(f"escolha entre 1 e {len(options)}!")
            except (ValueError, TypeError):
                self.warn("digite um numero valido!")

    def confirm(self, message: str, default: bool = True) -> bool:
        return Confirm.ask(message, default=default, console=self.console)

    def render_main_menu(self, rows: Sequence[MenuRow], footer_hint: str) -> None:
        self.console.print(Text("inicio — escolha um modo", style="wizard.label"))
        self.console.print()
        table = Table(box=box.ROUNDED, show_header=True, border_style="rgb(95,25,35)", header_style="wizard.section")
        table.add_column("", justify="center", style="wizard.accent", width=5)
        table.add_column("modo", style="bold")
        table.add_column("descricao", style="wizard.muted")
        for key, titulo, desc in rows:
            table.add_row(key, titulo, desc)
        self.console.print(table)
        self.console.print()
        self.console.print(Text(footer_hint, style="wizard.hint"))
        self.console.print()

    def render_help_section_menu(self, entries: Sequence[Tuple[str, str]], back_key: str = "0") -> None:
        table = Table(box=box.SIMPLE, show_header=False, border_style="dim")
        table.add_column("atalho", style="wizard.accent", width=6)
        table.add_column("secao", style="")
        for key, label in entries:
            table.add_row(key, label)
        table.add_row(back_key, "voltar ao menu principal")
        self.console.print(table)
        self.console.print()


def make_terminal_ui():
    if _HAS_RICH:
        return RichWizardUi()
    return PlainWizardUi()


def rich_available() -> bool:
    return _HAS_RICH
