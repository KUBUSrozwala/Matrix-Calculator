from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import QWebEngineView

class InverseWindow(QWidget):
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
                f"<div style='color: red'>⚠️ Please check and enter an integer value in each field correctly. All fields are required.</div>",
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
        is_dark = self.current_theme == "dark"
        colors = {
            'header': "#4192f0" if is_dark else "#d60326",
            'matrix': "#db2c52" if is_dark else "#400612",
            'calculation': "#0d9e66" if is_dark else "#bc4c00",
            'final': "#291be3" if is_dark else "#8250df"
        }

        format_num = lambda x: self.format_number(x)
        a_f, b_f, c_f, d_f = map(format_num, [a, b, c, d])
        det = a * d - b * c

        steps = []

        # Step 1: Matrix definition
        matrix_def = (
            fr"\color{{{colors['header']}}}\text{{Let }}A = "
            fr"\color{{{colors['matrix']}}}"
            fr"\begin{{bmatrix}} {a_f} & {b_f} \\ {c_f} & {d_f} \end{{bmatrix}}"
        )
        steps.append(fr"\[{matrix_def}\]")

        # Step 2: Determinant calculation
        det_steps = [
            fr"\color{{{colors['header']}}}|A| = ({a_f})({d_f}) - ({b_f})({c_f})",
            fr"\color{{{colors['calculation']}}}|A| = {format_num(a * d)} - {format_num(b * c)}",
            fr"\color{{{colors['calculation']}}}|A| = {format_num(det)}"
        ]
        steps.extend([fr"\[{s}\]" for s in det_steps])

        if det == 0:
            steps.append(fr"\[\color{{{colors['final']}}}\text{{Inverse does not exist (|A| = 0)}}\]")
        else:
            # Step 3: Cofactor calculations
            steps.append(fr"\[\color{{{colors['header']}}}\text{{Cofactor Calculations:}}\]")

            cofactor_steps = [
                fr"\color{{{colors['calculation']}}}A_{{11}} = (+1){d_f} = {format_num(d)}",
                fr"\color{{{colors['calculation']}}}A_{{12}} = (-1){c_f} = {format_num(-c)}",
                fr"\color{{{colors['calculation']}}}A_{{21}} = (-1){b_f} = {format_num(-b)}",
                fr"\color{{{colors['calculation']}}}A_{{22}} = (+1){a_f} = {format_num(a)}"
            ]
            steps.extend([fr"\[{s}\]" for s in cofactor_steps])

            # Step 4: Cofactor Matrix
            cofactor_matrix = (
                fr"\color{{{colors['header']}}}\text{{Cofactor Matrix:}}"
                fr"\color{{{colors['matrix']}}}"
                fr"\begin{{bmatrix}} {format_num(d)} & {format_num(-c)} \\ {format_num(-b)} & {format_num(a)} \end{{bmatrix}}"
            )
            steps.append(fr"\[{cofactor_matrix}\]")

            # Step 5: Adjoint Matrix
            adjoint_step = (
                fr"\color{{{colors['header']}}}\text{{Adjoint Matrix (Transpose):}}"
                fr"\color{{{colors['matrix']}}}"
                fr"\begin{{bmatrix}} {format_num(d)} & {format_num(-b)} \\ {format_num(-c)} & {format_num(a)} \end{{bmatrix}}"
            )
            steps.append(fr"\[{adjoint_step}\]")

            # Step 6: Inverse Calculation
            inverse_step = (
                fr"\color{{{colors['final']}}}A^{{-1}} = \frac{{1}}{{{format_num(det)}}}"
                fr"\color{{{colors['matrix']}}}"
                fr"\begin{{bmatrix}} {format_num(d)} & {format_num(-b)} \\ {format_num(-c)} & {format_num(a)} \end{{bmatrix}}"
            )
            steps.append(fr"\[{inverse_step}\]")

        return f'''
        <div style="text-align: center; padding: 20px;">
            {"<hr>".join(steps)}
        </div>
        '''

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