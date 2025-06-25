from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import QWebEngineView


class DeterminantWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.operation_name = "Determinant"
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
            lambda pos: self.apply_theme_with_scroll(pos, html, bg_color, text_color))

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
        if hasattr(self, 'last_values'):
            steps = self.generate_steps(*self.last_values)
            self.web_view.setHtml(self.get_mathjax_template(steps))

    def generate_steps(self, a, b, c, d):
        format_num = self.format_number
        a_f = format_num(a)
        b_f = format_num(b)
        c_f = format_num(c)
        d_f = format_num(d)
        det = a * d - b * c
        det_f = format_num(det)
        product_ad = a * d
        product_ad_f = format_num(product_ad)
        product_bc = b * c
        product_bc_f = format_num(product_bc)

        step1 = r"\text{Let A = }\begin{vmatrix} a & b \\ c & d \end{vmatrix}"
        step2 = fr"\text{{i.e A = }}\begin{{vmatrix}} {a_f} & {b_f} \\ {c_f} & {d_f} \end{{vmatrix}}"
        step3 = r"|A| = ( a \times d - b \times c )"
        step4 = fr"|A| = ( {a_f} \times {d_f} - {b_f} \times {c_f} )"
        step5 = fr"|A| = ( {product_ad_f} - {product_bc_f} )"
        step6 = fr"|A| = {det_f}"

        steps_html = [
            fr"\[ \color{{#d17711}} {step1} \]",
            fr"\[ \color{{#3041db}} {step2} \]",
            fr"\[ \color{{#41db1f}} {step3} \]",
            fr"\[ \color{{#8217cf}} {step4} \]",
            fr"\[ \color{{#06d4bf}} {step5} \]",
            fr"<p style='font-size: 13px; color: #cf0c20;'>\[ {step6} \]</p>"
        ]

        content = f'''
        <div style="text-align: center; padding: 20px;">
            <font color='blue'>
                {"<hr><hr>".join(steps_html)}
            </font>
        </div>
        '''
        return content

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
                    .step-header {{
                        color: {("#58a6ff" if bg_color == "#0d1117" else "#0366d6")};
                        font-size: 18px;
                        margin-top: 15px;
                    }}
                    .calculation-step {{
                        color: {("#ff9b72" if bg_color == "#0d1117" else "#bc4c00")};
                    }}
                    .final-result {{
                        color: {("#d2a8ff" if bg_color == "#0d1117" else "#8250df")};
                        font-size: 20px;
                    }}
                    hr {{
                        border-color: {("#30363d" if bg_color == "#0d1117" else "#d0d7de")};
                    }}
                </style>
            </head>
            <body>
                {content}
            </body>
            </html>
            """
