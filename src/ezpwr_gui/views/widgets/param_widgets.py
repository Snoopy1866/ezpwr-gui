# 参数输入小部件


from abc import abstractmethod

from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QIntValidator, QValidator
from PySide6.QtWidgets import QCheckBox, QComboBox, QMessageBox


class EPWidget:
    """纯 Python Mixin，仅供类型标注使用"""

    KEY = "param"
    PARAM_KEY = "param"
    LABEL = "参数"


# region 数值类型


class EPNumericComboBox(QComboBox, EPWidget):
    """数值型参数部件的抽象基类，子类应当实现 `get_params` 方法"""

    def __init__(
        self,
        parent=None,
        *,
        items: tuple[tuple[str, float], ...] | tuple[float, ...],
        min_val: float,
        max_val: float,
        default_value: float,
        interger_only: bool,
    ) -> None:
        super().__init__(parent)

        self.items = items
        self.min_val = min_val
        self.max_val = max_val
        self.default_value = default_value
        self.interger_only = interger_only

        self.setEditable(True)
        self.insertPolicy = QComboBox.InsertPolicy.NoInsert

        if all(isinstance(item, tuple) for item in items):
            for text, val in items:
                self.addItem(text)
                self.setItemData(self.count() - 1, val)
        else:
            for val in items:
                self.addItem(str(val))
                self.setItemData(self.count() - 1, val)

        self.setCurrentText(f"{self.default_value}")

        if interger_only:
            self.validator = QIntValidator(self, bottom=self.min_val, top=self.max_val)
        else:
            self.validator = QDoubleValidator(self, bottom=self.min_val, top=self.max_val)
        self.setValidator(self.validator)

        self.line_edit = self.lineEdit()
        self.line_edit.setAttribute(Qt.WidgetAttribute.WA_InputMethodEnabled, False)
        self.currentTextChanged.connect(self._validate_text)

    def _validate_text(self, text) -> None:

        if not text.strip():
            self.setStyleSheet("")
            return

        try:
            value = int(text) if self.interger_only else float(text)
        except ValueError:
            self.setStyleSheet("QComboBox { color: red; }")
            return

        if self.min_val < value < self.max_val:
            self.setStyleSheet("")
        else:
            self.setStyleSheet("QComboBox { color: red; }")

    def _on_editing_finished(self) -> None:

        text = self.line_edit.text().strip()

        if not text:
            return

        try:
            value = int(text) if self.interger_only else float(text)
        except ValueError:
            value = None

        if value is None or not (self.min_val < value < self.max_val):
            QMessageBox.warning(
                self,
                "数值超出范围",
                f"请输入有效范围内的数值！\n允许的范围是：{self.min_val} ~ {self.max_val}",
                QMessageBox.StandardButton.Ok,
            )

            self.line_edit.setFocus()
            self.line_edit.selectAll()

    @abstractmethod
    def get_params(self) -> dict[str, float]: ...


class EPIntComboBox(EPNumericComboBox):
    """数值型参数 - 整数"""

    def __init__(
        self,
        parent=None,
        *,
        items: tuple[tuple[str, int], ...],
        min_val: int,
        max_val: int,
        default_value: int,
    ) -> None:
        super().__init__(
            parent,
            items=items,
            min_val=min_val,
            max_val=max_val,
            default_value=default_value,
            interger_only=True,
        )

    def get_params(self) -> dict[str, int]:

        return {self.PARAM_KEY: int(self.line_edit.text())}


class EPDoubleComboBox(EPNumericComboBox, EPWidget):
    """数值型参数 - 浮点数"""

    def __init__(
        self,
        parent=None,
        *,
        items: tuple[tuple[str, float], ...],
        min_val: float,
        max_val: float,
        default_value: float,
    ) -> None:
        super().__init__(
            parent,
            items=items,
            min_val=min_val,
            max_val=max_val,
            default_value=default_value,
            interger_only=False,
        )

    def get_params(self) -> dict[str, float]:

        return {self.PARAM_KEY: float(self.line_edit.text())}


class EPMeanComboBox(EPDoubleComboBox):
    """数值型参数 - 均值"""

    KEY = "mean"
    PARAM_KEY = "mean"
    LABEL = "均值"

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            items=[
                0,
                1,
                2,
                3,
                4,
                5,
                10,
                20,
                30,
                40,
                50,
                100,
                200,
                300,
                400,
                500,
                1_000,
                2_000,
                5_000,
                10_000,
                100_000,
                1_000_000,
            ],
            min_val=-1_000_000_000,
            max_val=1_000_000_000,
            default_value=2,
        )


class EPSTDComboBox(EPDoubleComboBox):
    """数值型参数 - 标准差"""

    KEY = "std"
    PARAM_KEY = "std"
    LABEL = "标准差"

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            items=[
                0,
                1,
                2,
                3,
                4,
                5,
                10,
                20,
                30,
                40,
                50,
                100,
                200,
                300,
                400,
                500,
                1_000,
                2_000,
                5_000,
                10_000,
                100_000,
                1_000_000,
            ],
            min_val=-1_000_000_000,
            max_val=1_000_000_000,
            default_value=1,
        )


class EPProportionComboBox(EPDoubleComboBox):
    """数值型参数 - 率/比例"""

    KEY = "proportion"
    PARAM_KEY = "proportion"
    LABEL = "率/比例"

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            items=[
                0.01,
                0.02,
                0.03,
                0.04,
                0.05,
                0.10,
                0.20,
                0.30,
                0.40,
                0.50,
                0.60,
                0.70,
                0.80,
                0.90,
                0.95,
                0.96,
                0.97,
                0.98,
                0.99,
            ],
            min_val=0.0,
            max_val=1.0,
            default_value=0.95,
        )


class EPMarginComboBox(EPDoubleComboBox):
    """数值型参数 - 界值"""

    KEY = "margin"
    PARAM_KEY = "margin"
    LABEL = "界值"

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            items=[
                -0.30,
                -0.25,
                -0.20,
                -0.15,
                -0.10,
                -0.05,
                0,
                0.05,
                0.10,
                0.15,
                0.20,
                0.25,
                0.30,
            ],
            min_val=-1,
            max_val=1,
            default_value=0,
        )


class EPAlphaComboBox(EPDoubleComboBox):
    """数值型参数 - 显著性水平"""

    KEY = "alpha"
    PARAM_KEY = "alpha"
    LABEL = "显著性水平"

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            items=[
                0.025,
                0.05,
                0.10,
                0.15,
                0.20,
            ],
            min_val=0,
            max_val=1,
            default_value=0.05,
        )


class EPPowerComboBox(EPDoubleComboBox):
    """数值型参数 - 检验效能"""

    KEY = "power"
    PARAM_KEY = "power"
    LABEL = "检验效能"

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            items=[
                0.80,
                0.90,
                0.95,
                0.98,
                0.99,
            ],
            min_val=0,
            max_val=1,
            default_value=0.80,
        )


class EPRatioComboBox(EPDoubleComboBox):
    """数值型参数 - 样本量分配比例"""

    KEY = "ratio"
    PARAM_KEY = "ratio"
    LABEL = "试验组：对照组"

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            items=[
                ("1 / 5", 1 / 5),
                ("1 / 4", 1 / 4),
                ("1 / 3", 1 / 3),
                ("1 / 2", 1 / 2),
                ("1", 1),
                ("2", 2),
                ("3", 3),
                ("4", 4),
                ("5", 5),
            ],
            min_val=0,
            max_val=100,
            default_value=1,
        )


class EPSizeComboBox(EPIntComboBox):
    """数值型参数 - 样本量"""

    KEY = "size"
    PARAM_KEY = "size"
    LABEL = "样本量"

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            items=[
                10,
                20,
                30,
                40,
                50,
                100,
                200,
                500,
                1_000,
                2_000,
                5_000,
                10_000,
                100_000,
                1_000_000,
            ],
            min_val=1,
            max_val=1_000_000_000,
            default_value=100,
        )


# endregion

# region 选择类型


class EPComboBox(QComboBox, EPWidget):
    """选择型参数"""

    def __init__(self, parent=None, *, items: list[str], default_index: int = 0) -> None:
        super().__init__(parent)

        self.setEditable(False)

        self.addItems(items)
        self.setCurrentIndex(default_index)

    def get_params(self) -> dict[str, str]:

        return {self.PARAM_KEY: self.currentText()}


class EPType1AlternativeComboBox(EPComboBox):
    """选择型参数 - 检验类型（Type 1），允许选择：`'two-sided'`, `'greater'`, `'less'`"""

    KEY = "alternative"
    PARAM_KEY = "alternative"
    LABEL = "检验类型"

    def __init__(self, parent=None) -> None:
        super().__init__(parent, items=["two-sided", "greater", "less"])


class EPType2AlternativeComboBox(EPComboBox):
    """选择型参数 - 检验类型（Type 2），允许选择：`'greater'`, `'less'`"""

    KEY = "alternative"
    PARAM_KEY = "alternative"
    LABEL = "检验类型"

    def __init__(self, parent=None) -> None:
        super().__init__(parent, items=["greater", "less"])


class EPType3AlternativeComboBox(EPComboBox):
    """选择型参数 - 检验类型（Type 3），允许选择：`'two-sided'`, `'one-sided'`"""

    KEY = "alternative"
    PARAM_KEY = "alternative"
    LABEL = "检验类型"

    def __init__(self, parent=None) -> None:
        super().__init__(parent, items=["two-sided", "one-sided"])


class EPType4AlternativeComboBox(EPComboBox):
    """选择型参数 - 检验类型（Type 4），允许选择：`'two-sided'`, `'one-sided'`, `'greater'`, `'less'`"""

    KEY = "alternative"
    PARAM_KEY = "alternative"
    LABEL = "检验类型"

    def __init__(self, parent=None) -> None:
        super().__init__(parent, items=["two-sided", "one-sided", "greater", "less"])


# endregion


# region 布尔类型


class EPCheckBox(QCheckBox, EPWidget):
    """布尔型参数"""

    def __init__(self, parent=None, *, text: str, default_checked: bool = False) -> None:
        super().__init__(text, parent)
        self.setChecked(default_checked)

    def get_params(self) -> dict[str, str]:

        return {self.PARAM_KEY: self.isChecked()}


class EPContinuityCorrectionCheckBox(EPCheckBox):
    """布尔型参数 - 是否进行连续性校正"""

    KEY = "continuity_correction"
    PARAM_KEY = "continuity_correction"
    LABEL = "连续性校正"

    def __init__(self, parent=None) -> None:
        super().__init__(parent, text=self.LABEL)


# endregion
