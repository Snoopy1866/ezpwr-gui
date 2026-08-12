from PySide6.QtWidgets import QHBoxLayout, QStackedWidget, QTreeWidget, QWidget


class ModelsPage(QWidget):
    """模型页面"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)

        # 左侧 - 模型列表
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setFixedWidth(220)
        layout.addWidget(self.tree)

        # 右侧 - 模型参数
        self.stacked = QStackedWidget()
        layout.addWidget(self.stacked)
