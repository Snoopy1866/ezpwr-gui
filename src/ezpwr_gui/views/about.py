"""关于页面（Tab 栏的"关于"页）"""

from importlib import metadata

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

APP_NAME = "Ezpwr GUI"
APP_DESCRIPTION = "基于 ezpwr 核心算法库的检验效能与样本量计算图形界面。"

# 开源库信息：(显示名称, 安装包名, 简介, 项目主页)
OPEN_SOURCE_LIBS = [
    ("ezpwr", "ezpwr", "检验效能与样本量计算核心算法库", "https://github.com/Snoopy1866/ezpwr"),
    ("SciPy", "scipy", "科学计算基础库", "https://scipy.org"),
    ("PySide6", "PySide6", "Qt for Python，跨平台 GUI 框架", "https://wiki.qt.io/Qt_for_Python"),
]


def _get_dist_version(dist_name: str) -> str:
    """读取已安装发行版版本号，读取失败时回退"""

    try:
        return metadata.version(dist_name)
    except metadata.PackageNotFoundError:
        return "未知"


def _get_app_version() -> str:
    """获取应用版本号，优先使用安装元数据，失败时回退"""

    try:
        return metadata.version("ezpwr-gui")
    except metadata.PackageNotFoundError:
        return "0.1.0"


class AboutPage(QWidget):
    """关于页面"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.ezpwr_version: str | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(32, 24, 32, 24)

        # 应用名称
        lbl_name = QLabel(APP_NAME)
        lbl_name.setStyleSheet("font-size: 24px; font-weight: bold;")
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_name)

        # 版本信息（核心库版本由主窗口加载完成后更新）
        self.lbl_version = QLabel()
        self.lbl_version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_version.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        layout.addWidget(self.lbl_version)

        # 功能描述
        lbl_desc = QLabel(APP_DESCRIPTION)
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_desc)

        layout.addSpacing(12)

        # 开源库信息标题
        lbl_libs_title = QLabel("开源库信息")
        lbl_libs_title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(lbl_libs_title)

        # 开源库列表（每项一行：名称 版本 - 简介，名称与主页为超链接）
        for name, dist_name, desc, url in OPEN_SOURCE_LIBS:
            version = _get_dist_version(dist_name)
            item = QLabel(
                f'<a href="{url}" style="text-decoration:none; color:#1a73e8;">{name}</a> '
                f'<span style="color:#666;">{version}</span> - {desc}'
            )
            item.setOpenExternalLinks(True)
            item.setTextFormat(Qt.TextFormat.RichText)
            item.setWordWrap(True)
            layout.addWidget(item)

        layout.addStretch(1)

        self._update_version_label()

    def _update_version_label(self) -> None:
        """刷新版本信息标签"""

        text = f"应用版本：{_get_app_version()}"
        if self.ezpwr_version:
            text += f"    核心算法库（ezpwr）：{self.ezpwr_version}"
        else:
            text += "    核心算法库（ezpwr）：正在加载…"

        self.lbl_version.setText(text)

    def set_ezpwr_version(self, version: str) -> None:
        """核心算法库加载完成后由主窗口调用，更新版本显示"""

        self.ezpwr_version = version
        self._update_version_label()
