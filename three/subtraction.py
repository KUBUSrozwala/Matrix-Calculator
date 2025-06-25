from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import QWebEngineView


class SubtractionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.operation_name = "Subtraction"
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

    def get_mathjax_template(self, content="", bg_color="#0d1117", text_color="white"):
        return f"""
        <html>
        <head>
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

    def format_number(self, num):
        if isinstance(num, float) and num.is_integer():
            return int(num)
        return round(num, 2)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Input Grid
        input_layout = QHBoxLayout()
        self.matrix_a, inputs_a = self.create_matrix_input()
        self.matrix_b, inputs_b = self.create_matrix_input()

        self.all_inputs = inputs_a + inputs_b

        input_layout.addWidget(self.matrix_a)
        input_layout.addWidget(QLabel("➖"))
        input_layout.addWidget(self.matrix_b)
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
        for row in range(3):
            for col in range(3):
                inp = QLineEdit()
                inp.setPlaceholderText("0")
                inputs.append(inp)
                grid.addWidget(inp, row, col)
        return matrix, inputs

    def calculate(self):
        try:
            values = [float(inp.text()) for inp in self.all_inputs]
            # First matrix (a-i), second matrix (j-r)
            a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r = values
            steps = self.generate_steps(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r)

            self.last_html = steps
            is_dark = self.current_theme == "dark"
            bg_color = "#0d1117" if is_dark else "#ffffff"
            text_color = "#c9d1d9" if is_dark else "#1f1f1f"

            self.web_view.setHtml(self.get_mathjax_template(steps, bg_color, text_color))

        except ValueError as e:
            error_html = self.get_mathjax_template(
                f"<div style='color: red'>⚠️ Please check and enter an integer value in each field correctly. All fields are required.</div>",
                "#0d1117" if self.current_theme == "dark" else "#ffffff",
                "#c9d1d9" if self.current_theme == "dark" else "#1f1f1f"
            )
            self.web_view.setHtml(error_html)

    def update_display(self):
        if hasattr(self, 'last_values'):
            steps = self.generate_steps(*self.last_values)
            self.web_view.setHtml(self.get_mathjax_template(steps))

    def generate_steps(self, a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r):
        is_dark = self.current_theme == "dark"
        colors = {
            'header': "#4192f0" if is_dark else "#d60326",
            'matrix': "#db2c52" if is_dark else "#400612",
            'calculation': "#0d9e66" if is_dark else "#bc4c00",
            'final': "#291be3" if is_dark else "#8250df",
            'extra': "#7a4815" if is_dark else "#8250df"
        }

        format_num = lambda x: str(int(x)) if x.is_integer() else f"{x:.2f}"
        a_f, b_f, c_f = format_num(a), format_num(b), format_num(c)
        d_f, e_f, f_f = format_num(d), format_num(e), format_num(f)
        g_f, h_f, i_f = format_num(g), format_num(h), format_num(i)
        j_f, k_f, l_f = format_num(j), format_num(k), format_num(l)
        m_f, n_f, o_f = format_num(m), format_num(n), format_num(o)
        p_f, q_f, r_f = format_num(p), format_num(q), format_num(r)

        # Step 1: Matrix definitions
        step1 = (
            fr"\large\color{{{colors['header']}}}\text{{Matrix A = }}"
            fr"\color{{{colors['matrix']}}}"
            fr"\begin{{vmatrix}} {a_f} & {b_f} & {c_f} \\ {d_f} & {e_f} & {f_f} \\ {g_f} & {h_f} & {i_f} \end{{vmatrix}}"
        )

        step2 = (
            fr"\large\color{{{colors['header']}}}\text{{Matrix B = }}"
            fr"\color{{{colors['matrix']}}}"
            fr"\begin{{vmatrix}} {j_f} & {k_f} & {l_f} \\ {m_f} & {n_f} & {o_f} \\ {p_f} & {q_f} & {r_f} \end{{vmatrix}}"
        )

        # Step 2: Matrix Subtraction
        step3 = (
            fr"\large\color{{{colors['header']}}}\text{{A - B = }}"
            fr"\color{{{colors['matrix']}}}"
            fr"\left( \begin{{vmatrix}} {a_f} & {b_f} & {c_f} \\ {d_f} & {e_f} & {f_f} \\ {g_f} & {h_f} & {i_f} \end{{vmatrix}} "
            fr"+ \begin{{vmatrix}} {j_f} & {k_f} & {l_f} \\ {m_f} & {n_f} & {o_f} \\ {p_f} & {q_f} & {r_f} \end{{vmatrix}} \right)"
        )

        # Step 3: Calculation
        step4 = (
            fr"\large\color{{{colors['calculation']}}}\text{{A - B = }}"
            fr"\begin{{vmatrix}}"
            fr"{a_f}-{j_f} & {b_f}-{k_f} & {c_f}-{l_f} \\ "
            fr"{d_f}-{m_f} & {e_f}-{n_f} & {f_f}-{o_f} \\ "
            fr"{g_f}-{p_f} & {h_f}-{q_f} & {i_f}-{r_f}"
            fr"\end{{vmatrix}}"
        )

        # Final result
        final = lambda x: str(int(x)) if (x).is_integer() else f"{x:.2f}"
        step5 = (
            fr"\large\color{{{colors['final']}}}\text{{A - B = }}"
            fr"\begin{{vmatrix}}"
            fr"{final(a - j)} & {final(b - k)} & {final(c - l)} \\ "
            fr"{final(d - m)} & {final(e - n)} & {final(f - o)} \\ "
            fr"{final(g - p)} & {final(h - q)} & {final(i - r)}"
            fr"\end{{vmatrix}}"
        )

        return f"""
            <div class="steps">
                <div class="step">
                    <div class="step-number">Step 1: Define Matrices</div>
                    \[{step1}\]
                    \[{step2}\]
                </div>

                <div class="step">
                    <div class="step-number">Step 2: Add Matrices</div>
                    \[{step3}\]
                </div>

                <div class="step">
                    <div class="step-number">Step 3: Perform Subtraction</div>
                    \[{step4}\]
                </div>

                <div class="final-result">
                    \[{step5}\]
                </div>
            </div>
        """