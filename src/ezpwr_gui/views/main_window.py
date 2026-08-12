from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QTabWidget,
    QTreeWidgetItem,
    QWidget,
)

from .about import AboutPage
from .loader import CoreLibLoaderThread
from .models import ModelsPage
from .pages.pii import PIIPage
from .pages.pin import PINPage
from .pages.pis import PISPage
from .pages.psi import PSIPage
from .pages.psn import PSNPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Ezpwr GUI")
        self.resize(900, 600)

        self.page_map = {}
        self.ezpwr_version: str | None = None  # 核心库版本，加载完成后填充

        self._init_ui()
        self._build_tree_and_pages()

        # 启动后台异步加载核心库
        self._start_async_loading()

    def _init_ui(self) -> None:

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)

        # ===== 顶部横向 Tab 栏：计算 / 关于 =====
        self.tab_main = QTabWidget()
        self.tab_main.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_main.setDocumentMode(True)
        root_layout.addWidget(self.tab_main)

        # ---- Tab 1：模型 ----
        self.page_models = ModelsPage()
        self.tab_main.addTab(self.page_models, "模型")

        # ---- Tab 2：关于 ----
        self.page_about = AboutPage()
        self.tab_main.addTab(self.page_about, "关于")

        # 底部状态栏
        self.statusBar().showMessage("程序已就绪")

    def _build_tree_and_pages(self) -> None:

        self.tree = self.page_models.tree
        self.stacked = self.page_models.stacked

        cat_mean = QTreeWidgetItem(self.tree, ["定量模型"])
        cat_mean.setExpanded(True)
        cat_prop = QTreeWidgetItem(self.tree, ["定性模型"])
        cat_prop.setExpanded(True)
        cat_corr = QTreeWidgetItem(self.tree, ["相关系数"])
        cat_corr.setExpanded(True)

        # 设置不可选中
        for cat in (cat_mean, cat_prop, cat_corr):
            cat.setFlags(cat.flags() & ~Qt.ItemFlag.ItemIsSelectable)

        # 设置粗体
        bold_font = QFont()
        bold_font.setBold(True)
        for cat in (cat_mean, cat_prop, cat_corr):
            cat.setFont(0, bold_font)

        # 创建页面
        pages = (
            PSIPage(),
            PSNPage(),
            PIIPage(),
            PINPage(),
            PISPage(),
        )

        for page in pages:
            self.stacked.addWidget(page)
            item = QTreeWidgetItem(cat_prop, [page.LABEL])
            self.page_map[item] = page

        self.tree.itemClicked.connect(self._on_tree_item_clicked)

    def _start_async_loading(self) -> None:
        self.stacked.setEnabled(False)
        self.statusBar().showMessage("正在加载核心算法库，请稍后...")

        self.loader_thread = CoreLibLoaderThread(self)
        self.loader_thread.loaded_signal.connect(self._on_core_lib_loaded)
        self.loader_thread.failed_signal.connect(self._on_core_lib_failed)
        self.loader_thread.start()

    def _on_core_lib_loaded(self, ezpwr_module: object) -> None:
        """加载成功，把 ezpwr 模块对象传给所有页面"""

        # 记录核心库版本，并同步到关于页面
        self.ezpwr_version = getattr(ezpwr_module, "__version__", None) or "未知"
        self.page_about.set_ezpwr_version(self.ezpwr_version)

        failed_pages: list[str] = []
        for i in range(self.stacked.count()):
            page = self.stacked.widget(i)
            if not hasattr(page, "init_ezpwr"):
                continue
            try:
                page.init_ezpwr(ezpwr_module)
            except Exception as e:  # noqa: BLE001
                # 单个页面初始化失败不应拖垮整个加载流程，记录后继续
                label = getattr(page, "LABEL", type(page).__name__)
                failed_pages.append(f"{label}({e})")

        self.stacked.setEnabled(True)

        if failed_pages:
            self.statusBar().showMessage(f"部分页面初始化失败：{'; '.join(failed_pages)}")
        else:
            self.statusBar().showMessage("程序已就绪")

    def _on_core_lib_failed(self, error_msg: str) -> None:
        """加载失败，显示错误信息"""

        self.statusBar().showMessage(f"算法库加载异常：{error_msg}")

    def _on_tree_item_clicked(self, item: QTreeWidgetItem, _) -> None:
        """点击模型，显示参数面板"""

        if item.childCount() > 0:
            item.setExpanded(not item.isExpanded())

        page = self.page_map.get(item)
        if page is not None:
            self.stacked.setCurrentWidget(page)
