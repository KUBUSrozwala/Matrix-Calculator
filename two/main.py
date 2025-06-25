# main.py
import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# relative imports:
from .addition       import AdditionWindow
from .subtraction    import SubtractionWindow
from .multiplication import MultiplicationWindow
from .inverse        import InverseWindow
from .determinent    import DeterminantWindow
from .inv_row        import InvRowWindow


# import addition
# import subtraction
# import inverse
# import inv_row
# import multiplication
# import determinent

class AnimatedSidebar(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.buttons = []
        self.active_button = None
        self.setup_ui()
        self.collapsed = False
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def setup_ui(self):
        self.setMinimumWidth(250)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(15)

        # Header with dynamic color
        self.header = QLabel("MatriQ")
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setStyleSheet("""A:\Isa\python\Gui\Matrix C
            QLabel {
                font-family: 'Lucida Console';
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
            }
        """)
        layout.addWidget(self.header)

        # Menu Items
        self.menu_items = [
            ("➕ Addition", AdditionWindow),
            ("➖ Subtraction", SubtractionWindow),
            ("✖️ Multiplication", MultiplicationWindow),
            ("🔃 Inverse", InverseWindow),
            ("📏 Determinant", DeterminantWindow)
        ]

        # Create buttons with theme-aware styling
        for text, _ in self.menu_items:
            btn = QPushButton(text)
            btn.original_text = text
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    font-family: 'Lucida Console';
                    font-size: 16px;
                    padding: 12px 20px;
                    border: none;
                    text-align: left;
                }
            """)
            btn.clicked.connect(self.create_click_handler(btn))
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addStretch()

        # Theme Toggle Button
        self.theme_btn = QPushButton("🌙 Dark Mode")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background: rgba(200, 200, 200, 0.1);
                font-family: 'Lucida Console';
                padding: 12px;
                border-radius: 8px;
            }
        """)
        self.theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_btn)

        # Collapse Button
        self.collapse_btn = QPushButton("☰")
        self.collapse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.collapse_btn.setStyleSheet("""
            QPushButton {
                background: rgba(200, 200, 200, 0.1);
                font-family: 'Lucida Console';
                font-size: 20px;
                padding: 10px;
                border-radius: 8px;
            }
        """)
        self.collapse_btn.clicked.connect(self.toggle_sidebar)
        layout.addWidget(self.collapse_btn)

        # Initial theme setup
        self.update_colors(self.main_window.current_theme == "dark")

    def set_active_button(self, button):
        # Clear previous active style from all buttons
        for btn in self.buttons:
            btn.setStyleSheet(btn.styleSheet().replace(
                "border-left: 3px solid #ff7b72;",
                "border-left: 3px solid transparent;"
            ))
            btn.setStyleSheet(btn.styleSheet().replace(
                "background: rgba(200,200,200,0.1);",
                ""
            ))

        # Apply active style to selected button
        active_style = f"""
            border-left: 3px solid #ff7b72;
            background: rgba{("200,200,200", "0,0,0")[self.main_window.current_theme == "dark"]}0.1;
        """
        button.setStyleSheet(button.styleSheet() + active_style)
        self.active_button = button

    def create_click_handler(self, button):
        def handler():
            main_window = self.parent().parent()  # Get MainWindow instance
            main_window.load_content(button.text().split()[-1])
            self.set_active_button(button)

        return handler

    def toggle_sidebar(self):
        self.collapsed = not self.collapsed
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(60 if self.collapsed else 250)
        self.animation.start()

        # Update button texts using stored original_text
        for btn in self.buttons:
            if self.collapsed:
                btn.setText(btn.original_text.split()[0])
            else:
                btn.setText(btn.original_text)

        # Update theme button and header
        if self.collapsed:
            icon = "🌙" if self.main_window.current_theme == "dark" else "☀️"
            self.theme_btn.setText(icon)
            self.header.setText("MQ")
        else:
            mode = "Dark" if self.main_window.current_theme == "dark" else "Light"
            self.theme_btn.setText(f"🌙 {mode} Mode")
            self.header.setText("MatriQ")

    def toggle_theme(self):
        new_theme = "light" if self.main_window.current_theme == "dark" else "dark"
        self.main_window.set_theme(new_theme)
        is_dark = new_theme == "dark"

        # Update sidebar colors
        self.update_colors(is_dark)

        # Update theme button
        if self.collapsed:
            self.theme_btn.setText("☀️" if not is_dark else "🌙")
        else:
            self.theme_btn.setText(f"☀️ Light Mode" if not is_dark else f"🌙 Dark Mode")

    def create_click_handler(self, button):
        def handler():
            # Use self.main_window instead of parent hierarchy
            self.main_window.load_content(button.text().split()[-1])
            self.set_active_button(button)

        return handler

    def update_colors(self, is_dark):
        # Header color
        header_color = "#ff7b72" if is_dark else "#cf222e"
        self.header.setStyleSheet(f"""
            QLabel {{
                color: {header_color};
                font-size: 24px;
                font-weight: bold;
                padding: 15px;
            }}
        """)

        # Button styling
        text_color = "#c9d1d9" if is_dark else "#1f1f1f"
        button_style = f"""
            QPushButton {{
                color: {text_color};
                border-left: 3px solid transparent;
            }}
            QPushButton:hover {{
                background: rgba{("200,200,200", "0,0,0")[not is_dark]}0.1;
                border-left: 3px solid {header_color};
            }}
        """
        for btn in self.buttons:
            btn.setStyleSheet(btn.styleSheet() + button_style)


class TwoMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MatriQ - Matrix Calculator")
        self.setGeometry(100, 100, 1200, 800)
        self.content_widgets = {}
        self.current_theme = "dark"
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)


        # Create sidebar first
        self.sidebar_container = QWidget()
        self.sidebar_layout = QHBoxLayout(self.sidebar_container)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar = AnimatedSidebar(main_window=self, parent=self.sidebar_container)
        self.sidebar_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.sidebar_container)

        # Create content area AFTER sidebar
        self.content_area = QStackedWidget()
        main_layout.addWidget(self.content_area)

        # Set initial content and highlight based on first button
        if self.sidebar.buttons:
            # Get the operation name from the button's full text
            first_operation = self.sidebar.buttons[0].original_text.split()[-1]
            self.load_content(first_operation)
            # Find and activate the correct button
            for btn in self.sidebar.buttons:
                if btn.original_text.split()[-1] == first_operation:
                    self.sidebar.set_active_button(btn)
                    break

        self.set_theme("dark")


    # Moved outside of setup_ui and fixed indentation
    def set_theme(self, theme):
        self.current_theme = theme
        style = f"""
            QWidget {{
                background: {'#0d1117' if theme == 'dark' else '#ffffff'};
                color: {'#c9d1d9' if theme == 'dark' else '#1f1f1f'};
            }}
        """
        self.setStyleSheet(style)

        # Update content widgets
        for widget in self.content_widgets.values():
            if hasattr(widget, 'update_theme'):
                widget.update_theme(theme)
            if isinstance(widget, (AdditionWindow, SubtractionWindow,
                                   MultiplicationWindow, InverseWindow,
                                   InverseWindow, DeterminantWindow)) and hasattr(widget, 'web_view'):
                widget.web_view.setHtml(widget.get_mathjax_template(
                    widget.last_html if hasattr(widget, 'last_html') else "",
                    "#0d1117" if theme == "dark" else "#ffffff",
                    "#c9d1d9" if theme == "dark" else "#1f1f1f"
                ))

    def load_content(self, operation):
        if operation == "Inverse":
            dialog = QDialog(self)
            dialog.setWindowTitle("Select Inverse Method")
            dialog.setFixedSize(400, 300)

            # Get theme colors from main window
            is_dark = self.current_theme == "dark"
            bg_color = "#0d1117" if is_dark else "#ffffff"
            text_color = "#c9d1d9" if is_dark else "#1f1f1f"
            accent_color = "#ff7b72" if is_dark else "#cf222e"

            # Main layout
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)

            # Header
            header = QLabel("Choose Inverse Method")
            header.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    font-size: 18px;
                    font-weight: bold;
                    padding-bottom: 10px;
                    border-bottom: 2px solid {accent_color};
                }}
            """)
            layout.addWidget(header)

            # Method buttons
            methods = [
                ("🎯", "Adjoint Method", "Calculate using matrix adjoint and determinant"),
                ("🔄", "Row Transformation", "Calculate through elementary row operations")
            ]

            for icon, title, desc in methods:
                btn = QPushButton()
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setFixedHeight(70)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        border: 2px solid {accent_color};
                        border-radius: 8px;
                        padding: 15px;
                        text-align: left;
                        color: {text_color};
                    }}
                    QPushButton:hover {{
                        background: rgba{tuple(QColor(accent_color).getRgb()[:3])}20;
                    }}
                """)

                btn_layout = QHBoxLayout(btn)
                btn_layout.setContentsMargins(10, 5, 10, 5)
                btn_layout.setSpacing(15)

                # Icon
                icon_label = QLabel(icon)
                icon_label.setStyleSheet(f"font-size: 24px; color: {accent_color};")
                btn_layout.addWidget(icon_label)

                # Text
                text_widget = QWidget()
                text_layout = QVBoxLayout(text_widget)
                text_layout.setContentsMargins(0, 0, 0, 0)

                title_label = QLabel(title)
                title_label.setStyleSheet(f"""
                    QLabel {{
                        color: {text_color};
                        font-size: 14px;
                        font-weight: bold;
                    }}
                """)

                desc_label = QLabel(desc)
                desc_label.setStyleSheet(f"""
                    QLabel {{
                        color: {text_color};
                        font-size: 12px;
                        opacity: 0.8;
                    }}
                """)

                text_layout.addWidget(title_label)
                text_layout.addWidget(desc_label)
                btn_layout.addWidget(text_widget)
                btn_layout.addStretch()

                layout.addWidget(btn)

            # Button handlers
            def on_adjoint():
                dialog.accept()
                if "Inverse" not in self.content_widgets:
                    self.content_widgets["Inverse"] = InverseWindow()
                    self.content_area.addWidget(self.content_widgets["Inverse"])
                self.content_area.setCurrentWidget(self.content_widgets["Inverse"])

            def on_row():
                dialog.accept()
                if "InvRow" not in self.content_widgets:
                    self.content_widgets["InvRow"] = InvRowWindow()
                    self.content_area.addWidget(self.content_widgets["InvRow"])
                self.content_area.setCurrentWidget(self.content_widgets["InvRow"])

            # Connect buttons
            layout.itemAt(1).widget().clicked.connect(on_adjoint)  # First method button
            layout.itemAt(2).widget().clicked.connect(on_row)  # Second method button

            # Show dialog
            dialog.exec()
            return

        # Existing code for other operations
        if operation not in self.content_widgets:
            for text, cls in self.sidebar.menu_items:
                if text.split()[-1] == operation and cls:
                    self.content_widgets[operation] = cls()
                    self.content_area.addWidget(self.content_widgets[operation])
                    break

        if operation in self.content_widgets:
            self.content_area.setCurrentWidget(self.content_widgets[operation])

        # Update button states
        for btn in self.sidebar.buttons:
            if btn.original_text.split()[-1] == operation:
                self.sidebar.set_active_button(btn)
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TwoMainWindow()
    window.show()
    sys.exit(app.exec())