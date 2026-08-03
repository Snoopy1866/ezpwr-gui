# ==================== Nuitka Project Options ====================
# [通用基础配置]
# nuitka-project: --standalone
# nuitka-project: --show-progress
# nuitka-project: --show-memory
# nuitka-project: --assume-yes-for-downloads
# nuitka-project: --output-dir=dist
# nuitka-project: --product-name="Ezpwr GUI"
# nuitka-project: --python-flag=no_docstrings

# [性能优化与依赖处理]
# nuitka-project: --low-memory
# nuitka-project: --enable-plugin=pyside6
# nuitka-project: --include-package=ezpwr

# [Windows 专属选项]
# nuitka-project-if: {OS} == "Windows":
#     nuitka-project: --lto=no
#     nuitka-project: --jobs=1
#     nuitka-project: --clang
#     nuitka-project: --windows-console-mode=disable
#     nuitka-project: --output-filename="ezpwr-gui.exe"
#     nuitka-project: --product-name="Ezpwr GUI"

# [macOS 专属选项]
# nuitka-project-if: {OS} == "Darwin":
#     nuitka-project: --macos-create-app-bundle
#     nuitka-project: --macos-app-console-mode=disable
#     nuitka-project: --macos-app-name="Ezpwr GUI"
#     nuitka-project: --output-filename="ezpwr-gui"

# [Linux 专属选项]
# nuitka-project-if: {OS} == "Linux":
#     nuitka-project: --output-filename="ezpwr-gui"
# ================================================================


import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from ezpwr_gui.views.main_window import MainWindow


def main():
    # 必须在创建 QApplication 之前设置高 DPI 缩放策略。
    # 默认 Round 策略在 Windows 125%/150% 等分数缩放时会取整缩放因子，
    # 界面先按低分辨率渲染再被 Windows 位图拉伸，导致字体发虚。
    # PassThrough 让 Qt 使用精确分数缩放因子渲染，文字保持清晰。
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)

    # 显式使用系统 UI 字体（Windows 11 为微软雅黑 UI），避免字体回退导致的渲染模糊
    app.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
