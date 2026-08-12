from abc import abstractmethod
from collections.abc import Callable

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..widgets.param_widgets import EPWidget


class BaseTargetGroupBox(QGroupBox):
    """GroupBox - 求解目标"""

    class TargetCombox(QComboBox):
        """ComboBox - 求解目标"""

        def __init__(self, parent=None, *, widgets_cls: list[type[EPWidget]]) -> None:
            super().__init__(parent)
            items = (widget_cls.LABEL for widget_cls in widgets_cls)
            self.addItems(items)

    def __init__(self, parent=None, *, widgets_cls: list[type[EPWidget]]) -> None:
        super().__init__(parent, title="求解目标")

        self.widgets_cls = widgets_cls

        layout = QHBoxLayout(self)

        self.cbx_target = self.TargetCombox(parent, widgets_cls=self.widgets_cls)
        layout.addWidget(self.cbx_target)


class BaseParamGroupBox(QGroupBox):
    """GroupBox - 参数面板"""

    def __init__(self, parent=None, *, widgets_cls: list[type[EPWidget]]) -> None:
        super().__init__(parent, title="参数设置")

        layout = QFormLayout(self)

        self.widgets: dict[str, EPWidget] = {}  # 存放控件实例以供外部访问

        for widget_cls in widgets_cls:
            widget_instance = widget_cls()
            layout.addRow(widget_cls.LABEL, widget_instance)

            self.widgets[widget_cls.KEY.upper()] = widget_instance

    @abstractmethod
    def _init_value(self) -> None:
        """初始化参数值"""

    def get_params(self) -> dict[str, str]:
        """获取参数值，返回一个字典，key 为参数名，value 为参数值，可通过解包传入计算函数"""

        params_dict: dict[str, str] = {}
        for widget in self.widgets.values():
            params_dict |= widget.get_params()

        return params_dict

    def get_widget(self, key: str) -> EPWidget:
        """获取 key 对应的输入控件"""

        return self.widgets.get(key.upper())


class BaseResultGroupBox(QGroupBox):
    """GroupBox - 计算结果"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent, title="计算结果")

        layout = QVBoxLayout(self)

        # 结果标签：允许鼠标/键盘选中文本，方便直接复制
        self.lbl_result = QLabel()
        self.lbl_result.setWordWrap(True)
        self.lbl_result.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        layout.addWidget(self.lbl_result)

        # 一键复制按钮
        self.btn_copy = QPushButton("复制结果")
        self.btn_copy.clicked.connect(self._copy_result)
        self.btn_copy.setVisible(False)
        layout.addWidget(self.btn_copy, alignment=Qt.AlignmentFlag.AlignRight)

    def _copy_result(self) -> None:
        """将当前计算结果复制到剪贴板"""

        text = self.lbl_result.text()
        if not text:
            return

        QApplication.clipboard().setText(text)

        # 按钮短暂反馈，提示复制成功
        self.btn_copy.setText("已复制 ✓")
        QTimer.singleShot(1500, lambda: self.btn_copy.setText("复制结果"))


class CalcWorker(QThread):
    """后台计算线程

    求解器在主线程同步执行时，遇到病态参数（如效应量为零）可能长时间不返回，
    冻结整个 UI。将计算放入后台线程，界面始终保持响应。
    结果通过信号回传主线程（信号跨线程自动排队）。
    """

    finished_signal = Signal(object, object)  # (result, error)

    def __init__(self, solver: Callable[..., float], params: dict[str, float], parent=None) -> None:
        super().__init__(parent)

        self._solver = solver
        self._params = params

    def run(self) -> None:
        try:
            result = self._solver(**self._params)
            self.finished_signal.emit(result, None)
        except Exception as e:  # noqa: BLE001
            self.finished_signal.emit(None, e)


class BasePage(QWidget):
    """模型参数设置页面的基类"""

    LABEL = ""
    DEFAULT_TARGET = "样本量"  # 默认展示的求解目标

    def __init__(
        self,
        parent=None,
        *,
        gbx_target: BaseTargetGroupBox,
        gbx_params: tuple[BaseParamGroupBox, ...],
        gbx_result: BaseResultGroupBox,
    ) -> None:
        super().__init__(parent)

        self.gbx_target = gbx_target
        self.gbx_params = gbx_params
        self.gbx_result = gbx_result

        self._init_ui()

        self._connect_signals()

        self.ezpwr = None

    def init_ezpwr(self, ezpwr_module: object) -> None:
        """主窗口加载完成后自动回调此方法"""

        self.ezpwr = ezpwr_module
        self.ezpwr_module = None  # 页面对应的 ezpwr 模块
        self.solver_map: dict[int, Callable[..., float]] = {}  # 求解器查询字典

    def _init_ui(self) -> None:
        """初始化 UI"""

        layout = QVBoxLayout(self)

        self._add_target(layout)

        self._add_params(layout)

        self._add_calc_button(layout)

        self._add_result(layout)

        layout.addStretch(1)

    def _add_target(self, parent: QLayout) -> None:
        """在 `layout` 中添加求解目标 `gbx_target`"""

        parent.addWidget(self.gbx_target)

    def _add_calc_button(self, parent: QLayout) -> None:
        """在参数面板下方添加计算按钮（独立一行）

        按钮右对齐：左侧 4/5 为空白，按钮占用水平方向 1/5 宽度。
        独立一行可避免垂直高度受 GroupBox（含标题区）牵制而"冒顶"或"过扁"。
        """

        layout = QHBoxLayout()

        self.btn_calc = QPushButton("计算")
        self.btn_calc.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout.addWidget(self.btn_calc, alignment=Qt.AlignmentFlag.AlignRight)

        parent.addLayout(layout)

    def _add_params(self, parent: QLayout) -> None:
        """在 layout 中添加参数面板"""

        self.stacked_params = QStackedWidget()
        self.stacked_params.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        for gbx_param in self.gbx_params:
            self.stacked_params.addWidget(gbx_param)

        default_index = self.gbx_target.cbx_target.findText(self.DEFAULT_TARGET)
        if default_index < 0:
            default_index = 0  # 找不到时回退到第一个目标

        # 此时信号尚未连接（_connect_signals 在 _init_ui 之后调用），
        # setCurrentIndex 不会触发 _on_target_changed，因此需手动同步两处。
        self.gbx_target.cbx_target.setCurrentIndex(default_index)
        self.stacked_params.setCurrentIndex(default_index)

        parent.addWidget(self.stacked_params)

    def _add_result(self, parent: QLayout) -> None:
        """在 layout 中添加结果显示"""

        parent.addWidget(self.gbx_result)

    def _connect_signals(self) -> None:
        """连接信号"""

        # 事件：下拉框选择内容发生变化
        self.gbx_target.cbx_target.currentIndexChanged.connect(self._on_target_changed)

        # 事件：点击计算按钮
        self.btn_calc.clicked.connect(self._calc_target)

    def _calc_target(self) -> None:
        """计算结果（后台线程执行，不阻塞主界面 UI）"""

        if not self.ezpwr:
            self.gbx_result.lbl_result.setText("核心算法库尚未就绪！")
            return

        # 计算进行中禁止重复点击
        if getattr(self, "_calc_worker", None) is not None and self._calc_worker.isRunning():
            return

        target_index = self.gbx_target.cbx_target.currentIndex()

        solver = self.solver_map.get(target_index)
        if solver is None:
            self.gbx_result.lbl_result.setText("未找到对应的求解器")
            return

        params = self.stacked_params.currentWidget().get_params()

        # 计算进行中：禁用按钮并提示
        self.btn_calc.setEnabled(False)
        self.btn_calc.setText("计算中…")
        self.gbx_result.lbl_result.setText("正在计算，请稍候…")
        self.gbx_result.btn_copy.setVisible(False)

        # 计算放入后台线程，UI 保持响应。
        # 注意：不给线程设置 parent——若以页面为 parent，页面销毁时 Qt 会
        # 析构仍在运行的线程对象，触发 "QThread: Destroyed while thread is still running"。
        # 线程生命周期由页面自身管理（见 _shutdown_calc_worker）。
        self._calc_worker = CalcWorker(solver, params)
        self._calc_worker.finished_signal.connect(self._on_calc_finished)
        self._calc_worker.start()

    def _on_calc_finished(self, result, error) -> None:
        """后台计算完成回调（主线程执行）"""

        self.btn_calc.setEnabled(True)
        self.btn_calc.setText("计算")

        target_text = self.gbx_target.cbx_target.currentText()

        if error is not None:
            # 区分"无解"（SolutionNotFoundError）与一般错误
            try:
                ezpwr_exc = self.ezpwr.exceptions.SolutionNotFoundError
            except Exception:  # noqa: BLE001
                ezpwr_exc = None

            if ezpwr_exc is not None and isinstance(error, ezpwr_exc):
                self.gbx_result.lbl_result.setText("无解")
            else:
                self.gbx_result.lbl_result.setText(f"{error}")
            self.gbx_result.btn_copy.setVisible(False)
            return

        self.gbx_result.lbl_result.setText(f"{target_text}：{result}")
        self.gbx_result.btn_copy.setVisible(True)

        # 线程此时已结束（信号在线程 run() 返回后发出），可安全析构
        if self._calc_worker is not None:
            self._calc_worker.wait()  # 确保线程完全退出
            self._calc_worker.deleteLater()
            self._calc_worker = None

    def _shutdown_calc_worker(self) -> None:
        """页面销毁前安全停止后台计算线程

        避免 "QThread: Destroyed while thread is still running" 警告：
        - 线程已结束：直接析构；
        - 线程仍在运行：等待其结束；若超时（求解器卡死），不销毁运行中的
          线程对象，改为线程结束时自动 deleteLater 清理。
        """

        worker = getattr(self, "_calc_worker", None)
        if worker is None:
            return

        if worker.isRunning():
            worker.requestInterruption()  # 提示线程尽快退出（求解器内部需配合检查）
            if not worker.wait(3000):  # 超时：线程仍卡在求解器中
                # 不销毁运行中的线程（否则触发警告），线程结束时自动清理
                worker.finished.connect(worker.deleteLater)
                return

        worker.deleteLater()
        self._calc_worker = None

    def closeEvent(self, event) -> None:
        """窗口/页面关闭时安全停止后台计算线程"""

        self._shutdown_calc_worker()
        super().closeEvent(event)

    def _on_target_changed(self, index: int) -> None:
        """切换参数面板"""

        self.stacked_params.setCurrentIndex(index)

        self.gbx_result.lbl_result.clear()
        self.gbx_result.btn_copy.setVisible(False)
