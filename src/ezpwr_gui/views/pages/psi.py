from typing import Any

from PySide6.QtWidgets import QHBoxLayout, QWidget

from ..widgets.param_widgets import (
    EPAlphaComboBox,
    EPComboBox,
    EPContinuityCorrectionCheckBox,
    EPPowerComboBox,
    EPProportionComboBox,
    EPSizeComboBox,
    EPType1AlternativeComboBox,
)
from .base import BasePage, BaseParamGroupBox, BaseResultGroupBox, BaseTargetGroupBox


class H0ProportionComboBox(EPProportionComboBox):
    KEY = "h0_proportion"
    PARAM_KEY = "null_proportion"
    LABEL = "H0 下的率"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setCurrentText("0.80")


class H1ProportionComboBox(EPProportionComboBox):
    KEY = "h1_proportion"
    PARAM_KEY = "proportion"
    LABEL = "H1 下的率"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setCurrentText("0.90")


class SizeComboBox(EPSizeComboBox):
    pass


class AlternativeComboBox(EPType1AlternativeComboBox):
    pass


class AlphaComboBox(EPAlphaComboBox):
    pass


class PowerComboBox(EPPowerComboBox):
    pass


class MethodComboBox(EPComboBox):
    KEY = "method"
    PARAM_KEY = "method"
    LABEL = "检验方法"

    def __init__(self, parent=None) -> None:
        super().__init__(parent, items=["exact", "z-p0", "z-phat"])


class ContinuityCorrectionCheckBox(EPContinuityCorrectionCheckBox):
    KEY = "continuity_correction"
    PARAM_KEY = "continuity_correction"
    LABEL = "连续性校正"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)


class MethodContinuityCorrectionCompositeWidget(QWidget):
    """组合控件 - 检验方法 + 连续性校正"""

    KEY = "method_cc"
    LABEL = "检验方法"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.cbx_method = MethodComboBox()
        self.chk_cc = ContinuityCorrectionCheckBox()
        layout.addWidget(self.cbx_method)
        layout.addWidget(self.chk_cc)

        self.cbx_method.currentTextChanged.connect(self._on_cbx_method_current_text_changed)
        self._on_cbx_method_current_text_changed(self.cbx_method.currentText())

    def _on_cbx_method_current_text_changed(self, text: str) -> None:
        """检验方法下拉框选择的文本发生变化时触发事件"""

        self.chk_cc.setVisible(text != "exact")

    def get_params(self) -> dict[str, Any]:
        return self.cbx_method.get_params() | self.chk_cc.get_params()


class DirectionComboBox(EPComboBox):
    KEY = "direction"
    PARAM_KEY = "direction"
    LABEL = "求解方向"

    def __init__(self, parent=None) -> None:
        super().__init__(parent, items=["greater", "less"])


class TargetGroupBox(BaseTargetGroupBox):
    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            widgets_cls=[
                PowerComboBox,
                SizeComboBox,
                H0ProportionComboBox,
                H1ProportionComboBox,
            ],
        )


class ParamGroupBoxPower(BaseParamGroupBox):
    """GroupBox - 求解检验效能的参数面板"""

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            widgets_cls=[
                H0ProportionComboBox,
                H1ProportionComboBox,
                SizeComboBox,
                AlternativeComboBox,
                AlphaComboBox,
                MethodContinuityCorrectionCompositeWidget,
            ],
        )

        self._init_value()

    def _init_value(self) -> None:
        pass


class ParamGroupBoxSampleSize(BaseParamGroupBox):
    """GroupBox - 求解样本量的参数面板"""

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            widgets_cls=[
                H0ProportionComboBox,
                H1ProportionComboBox,
                AlternativeComboBox,
                AlphaComboBox,
                PowerComboBox,
                MethodContinuityCorrectionCompositeWidget,
            ],
        )

        self._init_value()

    def _init_value(self) -> None:
        pass


class ParamGroupBoxH0Proportion(BaseParamGroupBox):
    """GroupBox - 求解 H0 下的率的参数面板"""

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            widgets_cls=[
                H1ProportionComboBox,
                SizeComboBox,
                AlternativeComboBox,
                AlphaComboBox,
                PowerComboBox,
                MethodContinuityCorrectionCompositeWidget,
                DirectionComboBox,
            ],
        )

        self._init_value()

    def _init_value(self) -> None:
        cbx_direction: DirectionComboBox = self.get_widget(DirectionComboBox.KEY)
        cbx_direction.setCurrentIndex(0)


class ParamGroupBoxH1Proportion(BaseParamGroupBox):
    """GroupBox - 求解 H1 下的率的参数面板"""

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            widgets_cls=[
                H0ProportionComboBox,
                SizeComboBox,
                AlternativeComboBox,
                AlphaComboBox,
                PowerComboBox,
                MethodContinuityCorrectionCompositeWidget,
                DirectionComboBox,
            ],
        )

        self._init_value()

    def _init_value(self) -> None:
        cbx_direction: DirectionComboBox = self.get_widget(DirectionComboBox.KEY)
        cbx_direction.setCurrentIndex(1)


class PSIPage(BasePage):
    """单样本率差异性检验页面"""

    LABEL = "单样本率差异性检验"

    def __init__(self, parent=None) -> None:

        self.gbx_target = TargetGroupBox()

        self.gbx_param_group_power = ParamGroupBoxPower()
        self.gbx_param_group_sample_size = ParamGroupBoxSampleSize()
        self.gbx_param_group_h0_proportion = ParamGroupBoxH0Proportion()
        self.gbx_param_group_h1_proportion = ParamGroupBoxH1Proportion()
        self.gbx_params = (
            self.gbx_param_group_power,
            self.gbx_param_group_sample_size,
            self.gbx_param_group_h0_proportion,
            self.gbx_param_group_h1_proportion,
        )

        self.gbx_result = BaseResultGroupBox()

        super().__init__(
            parent,
            gbx_target=self.gbx_target,
            gbx_params=self.gbx_params,
            gbx_result=self.gbx_result,
        )

    def init_ezpwr(self, ezpwr_module: object) -> None:
        super().init_ezpwr(ezpwr_module)

        self.ezpwr_module = self.ezpwr.proportion.single.inequality
        self.solver_map = {
            0: self.ezpwr_module.solve_power,
            1: self.ezpwr_module.solve_size,
            2: self.ezpwr_module.solve_null_proportion,
            3: self.ezpwr_module.solve_proportion,
        }
