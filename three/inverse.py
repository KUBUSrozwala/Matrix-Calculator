from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import QWebEngineView


class InverseWindow3x3(QWidget):
    def __init__(self):
        super().__init__()
        self.operation_name = "Inverse 3x3"
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
            a, b, c, d, e, f, g, h, i = values
            steps = self.generate_steps(a, b, c, d, e, f, g, h, i)
            self.last_html = steps
            is_dark = self.current_theme == "dark"
            bg_color = "#0d1117" if is_dark else "#ffffff"
            text_color = "#c9d1d9" if is_dark else "#1f1f1f"
            self.web_view.setHtml(self.get_mathjax_template(steps, bg_color, text_color))
            self.last_values = values
        except ValueError as err:
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

    def generate_steps(self, a, b, c, d, e, f, g, h, i):
        is_dark = self.current_theme == "dark"
        colors = {
            'header': "#4192f0" if is_dark else "#d60326",
            'matrix': "#db2c52" if is_dark else "#400612",
            'calculation': "#0d9e66" if is_dark else "#bc4c00",
            'final': "#291be3" if is_dark else "#8250df",
            'error': "#ff0000"
        }

        format_num = lambda x: self.format_number(x)
        elements = [a, b, c, d, e, f, g, h, i]
        formatted = list(map(format_num, elements))
        a_f, b_f, c_f, d_f, e_f, f_f, g_f, h_f, i_f = formatted

        steps = []

        # Step 1: Matrix definition
        matrix_def = (
            fr"\color{{{colors['header']}}}\text{{Let }}A = "
            fr"\color{{{colors['matrix']}}}"
            fr"\begin{{bmatrix}} {a_f} & {b_f} & {c_f} \\ "
            fr"{d_f} & {e_f} & {f_f} \\ {g_f} & {h_f} & {i_f} \end{{bmatrix}}"
        )
        steps.append(fr"\[{matrix_def}\]")

        # Step 2: Determinant calculation
        det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
        det_steps = [
            fr"\color{{{colors['header']}}}|A| = {a_f}({e_f}×{i_f} - {f_f}×{h_f}) "
            fr"- {b_f}({d_f}×{i_f} - {f_f}×{g_f}) + {c_f}({d_f}×{h_f} - {e_f}×{g_f})",

            fr"\color{{{colors['calculation']}}}|A| = {a_f}({format_num(e * i - f * h)}) "
            fr"- {b_f}({format_num(d * i - f * g)}) + {c_f}({format_num(d * h - e * g)})",

            fr"\color{{{colors['calculation']}}}|A| = {format_num(a * (e * i - f * h))} "
            fr"- {format_num(b * (d * i - f * g))} + {format_num(c * (d * h - e * g))}",

            fr"\color{{{colors['calculation']}}}|A| = {format_num(det)}"
        ]
        steps.extend([fr"\[{s}\]" for s in det_steps])

        if det == 0:
            steps.append(fr"\[\color{{{colors['error']}}}\text{{Inverse does not exist (|A| = 0)}}\]")
        else:
            # Step 3: Matrix of Minors with element labels
            steps.append(
                fr"\[\color{{{colors['header']}}}\text{{Since }} |A| \neq 0, A^{{-1}} \text{{ exists.}}\]")
            steps.append(fr"\[\color{{{colors['header']}}}\text{{Matrix of Minors:}}\]")
            minors = [
                (0, 0, e * i - f * h), (0, 1, d * i - f * g), (0, 2, d * h - e * g),
                (1, 0, b * i - c * h), (1, 1, a * i - c * g), (1, 2, a * h - b * g),
                (2, 0, b * f - c * e), (2, 1, a * f - c * d), (2, 2, a * e - b * d)
            ]

            minor_steps = []
            for row, col, val in minors:
                minor_steps.append(
                    fr"\color{{{colors['calculation']}}}M_{{{row + 1}{col + 1}}} = {format_num(val)}"
                )
            steps.extend([fr"\[{s}\]" for s in minor_steps])

            # Display full minors matrix
            minors_matrix = (
                fr"\color{{{colors['matrix']}}}"
                fr"\text{{Minor of A =}}\ \begin{{bmatrix}} "
                fr"{format_num(minors[0][2])} & {format_num(minors[1][2])} & {format_num(minors[2][2])} \\ "
                fr"{format_num(minors[3][2])} & {format_num(minors[4][2])} & {format_num(minors[5][2])} \\ "
                fr"{format_num(minors[6][2])} & {format_num(minors[7][2])} & {format_num(minors[8][2])}"
                fr"\end{{bmatrix}}"
            )
            steps.append(fr"\[{minors_matrix}\]")

            # Step 4: Cofactor matrix with signs (corrected)
            steps.append(fr"\[\color{{{colors['header']}}}\text{{Apply Cofactor Signs:}}\]")
            signs = [1, -1, 1, -1, 1, -1, 1, -1, 1]
            cofactors = [
                (f"A_{{{row + 1}{col + 1}}}", sign * val, sign)
                for (row, col, val), sign in zip(minors, signs)
            ]

            cofactor_steps = []
            for (label, val, sign), (row, col, _) in zip(cofactors, minors):
                cofactor_steps.append(
                    fr"\color{{{colors['calculation']}}}{label} = ({'+' if sign == 1 else '-'}1){format_num(val / sign)} = {format_num(val)}"
                )
            steps.extend([fr"\[{s}\]" for s in cofactor_steps])

            # Display full cofactor matrix
            cofactor_matrix = (
                fr"\color{{{colors['matrix']}}}"
                fr"\text{{Cofactor of A =}}\ \begin{{bmatrix}} "
                fr"{format_num(cofactors[0][1])} & {format_num(cofactors[1][1])} & {format_num(cofactors[2][1])} \\ "
                fr"{format_num(cofactors[3][1])} & {format_num(cofactors[4][1])} & {format_num(cofactors[5][1])} \\ "
                fr"{format_num(cofactors[6][1])} & {format_num(cofactors[7][1])} & {format_num(cofactors[8][1])}"
                fr"\end{{bmatrix}}"
            )
            steps.append(fr"\[{cofactor_matrix}\]")

            # Step 5: Adjoint Matrix (Transpose)
            steps.append(fr"\[\color{{{colors['header']}}}\text{{Adjoint Matrix (Transpose of Cofactor):}}\]")
            adjoint = [
                cofactors[0][1], cofactors[3][1], cofactors[6][1],
                cofactors[1][1], cofactors[4][1], cofactors[7][1],
                cofactors[2][1], cofactors[5][1], cofactors[8][1]
            ]

            adjoint_matrix = (
                fr"\color{{{colors['matrix']}}}\text{{Adj(A) =}}\ "
                fr"\begin{{bmatrix}} "
                fr"{format_num(adjoint[0])} & {format_num(adjoint[1])} & {format_num(adjoint[2])} \\ "
                fr"{format_num(adjoint[3])} & {format_num(adjoint[4])} & {format_num(adjoint[5])} \\ "
                fr"{format_num(adjoint[6])} & {format_num(adjoint[7])} & {format_num(adjoint[8])}"
                fr"\end{{bmatrix}}"
            )
            steps.append(fr"\[{adjoint_matrix}\]")

            # Step 6: Inverse Calculation
            inv_det = 1 / det
            steps.append(fr"\[\color{{{colors['header']}}}\text{{Inverse Formula:}}\]")
            steps.append(
                fr"\[\color{{{colors['calculation']}}}A^{{-1}} = \frac{{1}}{{|A|}} \times \text{{Adj}}(A) = "
                fr"\frac{{1}}{{{format_num(det)}}} \times "
                fr"\begin{{bmatrix}} "
                fr"{format_num(adjoint[0])} & {format_num(adjoint[1])} & {format_num(adjoint[2])} \\ "
                fr"{format_num(adjoint[3])} & {format_num(adjoint[4])} & {format_num(adjoint[5])} \\ "
                fr"{format_num(adjoint[6])} & {format_num(adjoint[7])} & {format_num(adjoint[8])}"
                fr"\end{{bmatrix}}\]"
            )

            # Step 7: Numerical inverse
            steps.append(fr"\[\color{{{colors['header']}}}\text{{Scalar Multiplication:}}\]")
            steps.append(
                fr"\[\color{{{colors['calculation']}}}A^{{-1}} = "
                fr"{format_num(inv_det)} \times "
                fr"\begin{{bmatrix}} "
                fr"{format_num(adjoint[0])} & {format_num(adjoint[1])} & {format_num(adjoint[2])} \\ "
                fr"{format_num(adjoint[3])} & {format_num(adjoint[4])} & {format_num(adjoint[5])} \\ "
                fr"{format_num(adjoint[6])} & {format_num(adjoint[7])} & {format_num(adjoint[8])}"
                fr"\end{{bmatrix}}\]"
            )

            # Step 8: Final inverse matrix
            final_inv = [format_num(x * inv_det) for x in adjoint]
            final_matrix = (
                fr"\color{{{colors['final']}}}A^{{-1}} = "
                fr"\begin{{bmatrix}} "
                fr"{final_inv[0]} & {final_inv[1]} & {final_inv[2]} \\ "
                fr"{final_inv[3]} & {final_inv[4]} & {final_inv[5]} \\ "
                fr"{final_inv[6]} & {final_inv[7]} & {final_inv[8]}"
                fr"\end{{bmatrix}}"
            )
            steps.append(fr"\[{final_matrix}\]")

        return f'''
        <div style="text-align: center; padding: 20px;">
            {"<hr>".join(steps)}
        </div>
        '''

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