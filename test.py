from app.widgets.fontcard import FontPreviewWidget
from qtpop import FontManager

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    fm = FontManager()
    fm.load_font("resources/fonts/RobotoCondensed-VariableFont_wght.ttf")
    # fm.load_font("path/to/font2.ttf")

    w = FontPreviewWidget(fm)
    w.resize(700, 500)
    w.show()

    sys.exit(app.exec())
