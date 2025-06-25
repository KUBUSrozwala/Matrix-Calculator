import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import QWebEngineView

class InvRowWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.operation_name = "Inverse"
        self.all_inputs = []
        self.current_theme = "dark"
        self.setup_ui()
        self.update_styles()

    def update_theme(self, theme):
        self.current_theme = theme
        self.update_styles()
        if hasattr(self, 'last_values'):
            self.update_display()

    def update_styles(self, text_color=None):
        is_dark = self.current_theme == "dark"
        bg_color = "#0d1117" if is_dark else "#ffffff"
        border_color = "#30363d" if is_dark else "#d0d7de"
        focus_color = "#58a6ff"

        input_style = f"""
            QLineEdit {{
                background: {bg_color};
                color: {("#c9d1d9" if is_dark else "#1f1f1f")};
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 12px;
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border-color: {focus_color};
            }}
        """
        for inp in self.all_inputs:
            inp.setStyleSheet(input_style)

        if hasattr(self, 'last_html'):
            self.web_view.setHtml(self.get_mathjax_template(self.last_html, bg_color, text_color))

    def update_web_view_content(self, html):
        is_dark = self.current_theme == "dark"
        bg_color = "#0d1117" if is_dark else "#ffffff"
        text_color = "#c9d1d9" if is_dark else "#1f1f1f"

        self.web_view.page().runJavaScript(
            "window.scrollY",
            lambda pos: self.apply_theme_with_scroll(pos, html, bg_color, text_color)
        )

    def apply_theme_with_scroll(self, scroll_pos, html, bg_color, text_color):
        styled_html = self.get_mathjax_template(html, bg_color, text_color)
        self.web_view.setHtml(styled_html)
        self.web_view.page().runJavaScript(f"window.scrollTo(0, {scroll_pos});")

    def format_number(self, num):
        if isinstance(num, float) and num.is_integer():
            return str(int(num))
        return f"{num:.2f}"

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Input Matrix
        input_layout = QHBoxLayout()
        self.matrix, inputs = self.create_matrix_input()
        self.all_inputs = inputs
        input_layout.addWidget(self.matrix)
        layout.addLayout(input_layout)

        # Calculate Button
        btn = QPushButton("Calculate")
        btn.setStyleSheet("""
            QPushButton {
                background: #238636;
                color: white;
                padding: 12px;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover { background: #2ea043; }
        """)
        btn.clicked.connect(self.calculate)
        layout.addWidget(btn)

        # Steps Display
        self.web_view = QWebEngineView()
        self.web_view.setHtml(self.get_mathjax_template())
        layout.addWidget(self.web_view, 1)

    def create_matrix_input(self):
        matrix = QWidget()
        grid = QGridLayout(matrix)
        grid.setSpacing(10)
        inputs = []
        for row in range(2):
            for col in range(2):
                inp = QLineEdit()
                inp.setPlaceholderText("0")
                inputs.append(inp)
                grid.addWidget(inp, row, col)
        return matrix, inputs

    def calculate(self):
        try:
            values = [float(inp.text()) for inp in self.all_inputs]
            a, b, c, d = values
            steps = self.generate_steps(a, b, c, d)
            self.last_html = steps
            is_dark = self.current_theme == "dark"
            bg_color = "#0d1117" if is_dark else "#ffffff"
            text_color = "#c9d1d9" if is_dark else "#1f1f1f"
            self.web_view.setHtml(self.get_mathjax_template(steps, bg_color, text_color))
            self.last_values = values
        except ValueError as e:
            error_html = self.get_mathjax_template(
                f"<div style='color: red'>Error: {e}</div>",
                "#0d1117" if self.current_theme == "dark" else "#ffffff",
                "#c9d1d9" if self.current_theme == "dark" else "#1f1f1f"
            )
            self.web_view.setHtml(error_html)

    def update_display(self):
        """Refresh display with current theme"""
        if hasattr(self, 'last_values'):
            steps = self.generate_steps(*self.last_values)
            self.web_view.setHtml(self.get_mathjax_template(steps))

    def generate_steps(self, a, b, c, d):
        from fractions import Fraction

        # turn floats/ints into nice fraction strings
        def fmt(x):
            f = Fraction(x).limit_denominator()
            if f.denominator == 1:
                return str(f.numerator)
            # keep denominator positive
            if f.denominator < 0:
                f = Fraction(-f.numerator, -f.denominator)
            return f"\\frac{{{f.numerator}}}{{{f.denominator}}}"

        colors = {
            'header': "#4192f0",
            'matrix': "#db2c52",
            'operation': "#0d9e66",
            'final': "#291be3"
        }

        # helper to render a 2×2 matrix in LaTeX
        def mat(m):
            return (
                "\\begin{bmatrix}"
                f"{fmt(m[0][0])} & {fmt(m[0][1])}\\\\ "
                f"{fmt(m[1][0])} & {fmt(m[1][1])}"
                "\\end{bmatrix}"
            )

        steps = []
        L = [[a, b], [c, d]]
        R = [[1, 0], [0, 1]]

        # — Initial Equation —
        steps.append(f"""
        <div class="step">
          <span style="color:{colors['header']}">Initial Equation:</span><br/>
          $$\\color{{{colors['matrix']}}}{mat(L)}\\color{{black}}\\cdot A^{{-1}}
             =\\color{{{colors['matrix']}}}{mat(R)}$$
        </div>
        """)

        def row_op(desc, newL, newR):
            steps.append(f"""
            <div class="step">
              <span style="color:{colors['operation']}">Row Operation:</span>&nbsp;
              ${desc}$<br/>
              $$\\color{{{colors['matrix']}}}{mat(newL)}\\color{{black}}\\cdot A^{{-1}}
                 =\\color{{{colors['matrix']}}}{mat(newR)}$$
            </div>
            """)

        # Step 1: Normalize R1
        if L[0][0] != 1:
            d = L[0][0]
            newL = [[x / d for x in L[0]], L[1].copy()]
            newR = [[x / d for x in R[0]], R[1].copy()]
            row_op(f"R_1 \\to \\tfrac{{1}}{{{fmt(d)}}}R_1", newL, newR)
            L, R = newL, newR

        # Step 2: Eliminate below
        if L[1][0] != 0:
            m = L[1][0]
            newL = [
                L[0].copy(),
                [L[1][i] - m * L[0][i] for i in (0, 1)]
            ]
            newR = [
                R[0].copy(),
                [R[1][i] - m * R[0][i] for i in (0, 1)]
            ]
            row_op(f"R_2 \\to R_2 - ({fmt(m)})R_1", newL, newR)
            L, R = newL, newR

        # Step 3: Normalize R2
        if L[1][1] not in (0, 1):
            d = L[1][1]
            newL = [L[0].copy(), [x / d for x in L[1]]]
            newR = [R[0].copy(), [x / d for x in R[1]]]
            row_op(f"R_2 \\to \\tfrac{{1}}{{{fmt(d)}}}R_2", newL, newR)
            L, R = newL, newR

        # Step 4: Eliminate above
        if L[0][1] != 0:
            m = L[0][1]
            newL = [
                [L[0][i] - m * L[1][i] for i in (0, 1)],
                L[1].copy()
            ]
            newR = [
                [R[0][i] - m * R[1][i] for i in (0, 1)],
                R[1].copy()
            ]
            row_op(f"R_1 \\to R_1 - ({fmt(m)})R_2", newL, newR)
            L, R = newL, newR

        # — Final Result —
        steps.append(f"""
        <div class="step" style="color:{colors['final']}">
          $${mat([[1, 0], [0, 1]])}\\cdot A^{{-1}}={mat(R)}$$
          $$\\therefore A^{{-1}}={mat(R)}$$
        </div>
        """)

        return "".join(steps)

    def get_mathjax_template(self, content="", bg_color="#0d1117", text_color="white"):
        return f"""
        <html>
        <head>
            <script>
                MathJax = {{
                    loader: {{load: ['[tex]/color']}},
                    tex: {{
                        packages: {{'[+]': ['color']}},
                        inlineMath: [['$', '$'], ['\\(', '\\)']],
                        displayAlign: 'center',
                    }},
                    startup: {{
                        typeset: false
                    }}
                }};
            </script>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                body {{
                    background-color: {bg_color};
                    color: {text_color};
                    font-family: 'Lucida Console', monospace;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                }}
                hr {{
                    border: 0.5px solid {text_color}33;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            {content}
            <script>
                MathJax.typesetPromise();
            </script>
        </body>
        </html>
        """

    def get_mathjax_template(self, content="", bg_color="#0d1117", text_color="white"):
        return f"""
        <html>
        <head>
            <script>
                MathJax = {{
                    loader: {{load: ['[tex]/color']}},
                    tex: {{
                        packages: {{'[+]': ['color']}},
                        inlineMath: [['$', '$'], ['\\(', '\\)']],
                        tags: 'ams'
                    }},
                    startup: {{
                        typeset: false
                    }}
                }};
            </script>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                body {{
                    background-color: {bg_color};
                    color: {text_color};
                    font-family: 'Lucida Console', monospace;
                    line-height: 1.6;
                    padding: 20px;
                }}
                hr {{
                    border: 0.5px solid {text_color}33;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            {content}
            <script>
                MathJax.typesetPromise();
            </script>
        </body>
        </html>
        """

    def get_mathjax_template(self, content="", bg_color="#0d1117", text_color="white"):
        return f"""
        <html>
        <head>
            <script>
                MathJax = {{
                    tex: {{
                        packages: {{'[+]': ['xcolor']}},
                        inlineMath: [['$', '$'], ['\\(', '\\)']]
                    }}
                }};
            </script>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                body {{
                    background-color: {bg_color};
                    color: {text_color};
                    font-family: 'Lucida Console', monospace;
                    line-height: 1.6;
                    padding: 20px;
                }}
                hr {{
                    border: 0.5px solid {text_color}33;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """

