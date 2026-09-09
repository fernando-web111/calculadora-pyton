#!/usr/bin/env python3
"""
Calculadora Científica com Interface Gráfica
==============================================
Calculadora científica completa construída com Tkinter (biblioteca padrão
do Python, não requer instalação extra).

Para executar:
    python3 calculadora_cientifica_gui.py
"""

import math
import tkinter as tk
from tkinter import font as tkfont


# ---------------------------------------------------------------------------
# Lógica de cálculo (independente da interface, facilita testes)
# ---------------------------------------------------------------------------

class MotorCalculadora:
    """Responsável por interpretar e avaliar as expressões digitadas."""

    def __init__(self):
        self.memoria = 0.0
        self.modo_graus = True

    def _preparar_expressao(self, expressao: str) -> str:
        """Converte símbolos amigáveis da tela em código Python válido."""
        substituicoes = {
            "×": "*",
            "÷": "/",
            "^": "**",
            "π": "pi",
            "√(": "sqrt(",
            "−": "-",
        }
        for antigo, novo in substituicoes.items():
            expressao = expressao.replace(antigo, novo)

        # Trata "x!" -> fatorial(x) para números ou fechamento de parênteses
        expressao = self._converter_fatorial(expressao)
        return expressao

    @staticmethod
    def _converter_fatorial(expressao: str) -> str:
        resultado = []
        i = 0
        while i < len(expressao):
            char = expressao[i]
            if char == "!":
                # Recua para capturar o operando (número ou grupo entre parênteses)
                if resultado and resultado[-1] == ")":
                    profundidade = 0
                    j = len(resultado) - 1
                    while j >= 0:
                        if resultado[j] == ")":
                            profundidade += 1
                        elif resultado[j] == "(":
                            profundidade -= 1
                            if profundidade == 0:
                                break
                        j -= 1
                    operando = "".join(resultado[j:])
                    del resultado[j:]
                    resultado.append(f"fatorial({operando})")
                else:
                    j = len(resultado) - 1
                    while j >= 0 and (resultado[j].isdigit() or resultado[j] == "."):
                        j -= 1
                    operando = "".join(resultado[j + 1:])
                    del resultado[j + 1:]
                    resultado.append(f"fatorial({operando})")
            else:
                resultado.append(char)
            i += 1
        return "".join(resultado)

    def _funcoes_permitidas(self) -> dict:
        def sin(x):
            return math.sin(math.radians(x)) if self.modo_graus else math.sin(x)

        def cos(x):
            return math.cos(math.radians(x)) if self.modo_graus else math.cos(x)

        def tan(x):
            return math.tan(math.radians(x)) if self.modo_graus else math.tan(x)

        def asin(x):
            r = math.asin(x)
            return math.degrees(r) if self.modo_graus else r

        def acos(x):
            r = math.acos(x)
            return math.degrees(r) if self.modo_graus else r

        def atan(x):
            r = math.atan(x)
            return math.degrees(r) if self.modo_graus else r

        def fatorial(x):
            return math.factorial(int(x))

        return {
            "sin": sin, "cos": cos, "tan": tan,
            "asin": asin, "acos": acos, "atan": atan,
            "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
            "log": math.log10, "ln": math.log,
            "sqrt": math.sqrt, "exp": math.exp,
            "fatorial": fatorial,
            "pi": math.pi, "e": math.e,
            "abs": abs, "pow": pow,
        }

    def avaliar(self, expressao: str):
        expressao_python = self._preparar_expressao(expressao)
        ambiente = self._funcoes_permitidas()
        # Bloqueia acesso a builtins para manter a avaliação segura
        return eval(expressao_python, {"__builtins__": {}}, ambiente)


# ---------------------------------------------------------------------------
# Interface gráfica
# ---------------------------------------------------------------------------

class CalculadoraCientificaApp:
    COR_FUNDO = "#1e1e1e"
    COR_VISOR = "#111111"
    COR_TEXTO_VISOR = "#ffffff"
    COR_TEXTO_HISTORICO = "#888888"
    COR_NUMERO = "#333333"
    COR_NUMERO_HOVER = "#454545"
    COR_OPERADOR = "#ff9500"
    COR_CIENTIFICA = "#3a3a3a"
    COR_ESPECIAL = "#a5a5a5"
    COR_TEXTO_CLARO = "#ffffff"
    COR_TEXTO_ESCURO = "#000000"

    def __init__(self, raiz: tk.Tk):
        self.raiz = raiz
        self.motor = MotorCalculadora()
        self.expressao_atual = ""
        self.ultimo_resultado_exibido = False

        self.raiz.title("Calculadora Científica")
        self.raiz.configure(bg=self.COR_FUNDO)
        self.raiz.resizable(False, False)

        self._construir_visor()
        self._construir_teclado()

        self.raiz.bind("<Key>", self._tecla_pressionada)

    # -- Construção da interface -------------------------------------------------

    def _construir_visor(self):
        fonte_historico = tkfont.Font(family="Segoe UI", size=12)
        fonte_visor = tkfont.Font(family="Segoe UI", size=32, weight="bold")

        quadro_visor = tk.Frame(self.raiz, bg=self.COR_VISOR)
        quadro_visor.pack(fill="both", expand=True)

        self.rotulo_modo = tk.Label(
            quadro_visor, text="DEG", anchor="w",
            bg=self.COR_VISOR, fg=self.COR_TEXTO_HISTORICO,
            font=fonte_historico, padx=15,
        )
        self.rotulo_modo.pack(fill="x", pady=(10, 0))

        self.rotulo_historico = tk.Label(
            quadro_visor, text="", anchor="e",
            bg=self.COR_VISOR, fg=self.COR_TEXTO_HISTORICO,
            font=fonte_historico, padx=15,
        )
        self.rotulo_historico.pack(fill="x")

        self.rotulo_visor = tk.Label(
            quadro_visor, text="0", anchor="e",
            bg=self.COR_VISOR, fg=self.COR_TEXTO_VISOR,
            font=fonte_visor, padx=15,
        )
        self.rotulo_visor.pack(fill="x", pady=(0, 15))

    def _construir_teclado(self):
        quadro_botoes = tk.Frame(self.raiz, bg=self.COR_FUNDO)
        quadro_botoes.pack()

        linhas_botoes = [
            [("Rad/Deg", self._alternar_modo, self.COR_CIENTIFICA),
             ("(", lambda: self._inserir("("), self.COR_CIENTIFICA),
             (")", lambda: self._inserir(")"), self.COR_CIENTIFICA),
             ("MC", self._memoria_limpar, self.COR_CIENTIFICA),
             ("MR", self._memoria_recuperar, self.COR_CIENTIFICA)],

            [("x²", lambda: self._inserir("^2"), self.COR_CIENTIFICA),
             ("x^y", lambda: self._inserir("^"), self.COR_CIENTIFICA),
             ("√(", lambda: self._inserir("√("), self.COR_CIENTIFICA),
             ("x!", lambda: self._inserir("!"), self.COR_CIENTIFICA),
             ("M+", self._memoria_somar, self.COR_CIENTIFICA)],

            [("sin", lambda: self._inserir("sin("), self.COR_CIENTIFICA),
             ("cos", lambda: self._inserir("cos("), self.COR_CIENTIFICA),
             ("tan", lambda: self._inserir("tan("), self.COR_CIENTIFICA),
             ("π", lambda: self._inserir("π"), self.COR_CIENTIFICA),
             ("M-", self._memoria_subtrair, self.COR_CIENTIFICA)],

            [("asin", lambda: self._inserir("asin("), self.COR_CIENTIFICA),
             ("acos", lambda: self._inserir("acos("), self.COR_CIENTIFICA),
             ("atan", lambda: self._inserir("atan("), self.COR_CIENTIFICA),
             ("e", lambda: self._inserir("e"), self.COR_CIENTIFICA),
             ("ln", lambda: self._inserir("ln("), self.COR_CIENTIFICA)],

            [("log", lambda: self._inserir("log("), self.COR_CIENTIFICA),
             ("C", self._limpar_tudo, self.COR_ESPECIAL),
             ("⌫", self._apagar, self.COR_ESPECIAL),
             ("%", lambda: self._inserir("/100"), self.COR_ESPECIAL),
             ("÷", lambda: self._inserir("÷"), self.COR_OPERADOR)],

            [("7", lambda: self._inserir("7"), self.COR_NUMERO),
             ("8", lambda: self._inserir("8"), self.COR_NUMERO),
             ("9", lambda: self._inserir("9"), self.COR_NUMERO),
             ("×", lambda: self._inserir("×"), self.COR_OPERADOR),
             ("exp", lambda: self._inserir("exp("), self.COR_CIENTIFICA)],

            [("4", lambda: self._inserir("4"), self.COR_NUMERO),
             ("5", lambda: self._inserir("5"), self.COR_NUMERO),
             ("6", lambda: self._inserir("6"), self.COR_NUMERO),
             ("−", lambda: self._inserir("−"), self.COR_OPERADOR),
             ("sinh", lambda: self._inserir("sinh("), self.COR_CIENTIFICA)],

            [("1", lambda: self._inserir("1"), self.COR_NUMERO),
             ("2", lambda: self._inserir("2"), self.COR_NUMERO),
             ("3", lambda: self._inserir("3"), self.COR_NUMERO),
             ("+", lambda: self._inserir("+"), self.COR_OPERADOR),
             ("cosh", lambda: self._inserir("cosh("), self.COR_CIENTIFICA)],

            [("0", lambda: self._inserir("0"), self.COR_NUMERO),
             (".", lambda: self._inserir("."), self.COR_NUMERO),
             ("±", self._inverter_sinal, self.COR_NUMERO),
             ("=", self._calcular, self.COR_OPERADOR),
             ("tanh", lambda: self._inserir("tanh("), self.COR_CIENTIFICA)],
        ]

        fonte_botao = tkfont.Font(family="Segoe UI", size=14)

        for linha in linhas_botoes:
            quadro_linha = tk.Frame(quadro_botoes, bg=self.COR_FUNDO)
            quadro_linha.pack()
            for texto, comando, cor_fundo in linha:
                cor_texto = self.COR_TEXTO_CLARO
                botao = tk.Button(
                    quadro_linha, text=texto, command=comando,
                    width=6, height=2, bg=cor_fundo, fg=cor_texto,
                    activebackground=self.COR_NUMERO_HOVER,
                    activeforeground=cor_texto,
                    font=fonte_botao, bd=0, relief="flat",
                    highlightthickness=0,
                )
                botao.pack(side="left", padx=3, pady=3)

    # -- Ações do teclado ----------------------------------------------------

    def _atualizar_visor(self):
        texto = self.expressao_atual if self.expressao_atual else "0"
        self.rotulo_visor.config(text=texto)

    def _inserir(self, texto: str):
        if self.ultimo_resultado_exibido and texto not in ("+", "−", "×", "÷", "^"):
            self.expressao_atual = ""
        self.ultimo_resultado_exibido = False
        self.expressao_atual += texto
        self._atualizar_visor()

    def _limpar_tudo(self):
        self.expressao_atual = ""
        self.rotulo_historico.config(text="")
        self._atualizar_visor()

    def _apagar(self):
        self.expressao_atual = self.expressao_atual[:-1]
        self._atualizar_visor()

    def _inverter_sinal(self):
        if self.expressao_atual.startswith("-"):
            self.expressao_atual = self.expressao_atual[1:]
        else:
            self.expressao_atual = "-" + self.expressao_atual
        self._atualizar_visor()

    def _alternar_modo(self):
        self.motor.modo_graus = not self.motor.modo_graus
        self.rotulo_modo.config(text="DEG" if self.motor.modo_graus else "RAD")

    def _memoria_somar(self):
        try:
            self.motor.memoria += self.motor.avaliar(self.expressao_atual or "0")
        except Exception:
            pass

    def _memoria_subtrair(self):
        try:
            self.motor.memoria -= self.motor.avaliar(self.expressao_atual or "0")
        except Exception:
            pass

    def _memoria_recuperar(self):
        self._inserir(self._formatar(self.motor.memoria))

    def _memoria_limpar(self):
        self.motor.memoria = 0.0

    @staticmethod
    def _formatar(valor) -> str:
        if isinstance(valor, float) and valor.is_integer():
            return str(int(valor))
        if isinstance(valor, float):
            return f"{valor:.10g}"
        return str(valor)

    def _calcular(self):
        if not self.expressao_atual:
            return
        try:
            resultado = self.motor.avaliar(self.expressao_atual)
            self.rotulo_historico.config(text=self.expressao_atual + " =")
            self.expressao_atual = self._formatar(resultado)
            self.ultimo_resultado_exibido = True
        except ZeroDivisionError:
            self.expressao_atual = "Erro: divisão por zero"
            self.ultimo_resultado_exibido = True
        except Exception:
            self.expressao_atual = "Erro"
            self.ultimo_resultado_exibido = True
        self._atualizar_visor()

    def _tecla_pressionada(self, evento):
        tecla = evento.char
        mapa_teclado = {
            "*": "×", "/": "÷", "-": "−",
        }
        mapa_numpad = {
            "KP_0": "0", "KP_1": "1", "KP_2": "2", "KP_3": "3", "KP_4": "4",
            "KP_5": "5", "KP_6": "6", "KP_7": "7", "KP_8": "8", "KP_9": "9",
            "KP_Add": "+", "KP_Subtract": "−", "KP_Multiply": "×",
            "KP_Divide": "÷", "KP_Decimal": ".",
        }
        keysym = evento.keysym

        if keysym in mapa_numpad:
            self._inserir(mapa_numpad[keysym])
        elif tecla.isdigit() or tecla in ".()+":
            self._inserir(tecla)
        elif tecla in mapa_teclado:
            self._inserir(mapa_teclado[tecla])
        elif tecla in ("\r", "=") or keysym == "KP_Enter":
            self._calcular()
        elif keysym == "BackSpace":
            self._apagar()
        elif keysym == "Escape":
            self._limpar_tudo()


# ---------------------------------------------------------------------------
# Ponto de entrada
# ---------------------------------------------------------------------------

def main():
    raiz = tk.Tk()
    CalculadoraCientificaApp(raiz)
    raiz.mainloop()


if __name__ == "__main__":
    main()