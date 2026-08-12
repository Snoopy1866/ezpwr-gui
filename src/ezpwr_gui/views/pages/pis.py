from typing import Any

from PySide6.QtWidgets import QHBoxLayout, QWidget

from ..widgets.param_widgets import (
    EPAlphaComboBox,
    EPComboBox,
    EPContinuityCorrectionCheckBox,
    EPMarginComboBox,
    EPPowerComboBox,
    EPProportionComboBox,
    EPRatioComboBox,
    EPSizeComboBox,
    EPType2AlternativeComboBox,
)
from .base import BasePage, BaseParamGroupBox, BaseResultGroupBox, BaseTargetGroupBox


class TreatmentProportionComboBox(EPProportionComboBox):
    KEY = "treatment_proportion"
    PARAM_KEY = "treatment_proportion"
    LABEL = "试验组的率/比例"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setCurrentText("0.95")


class ReferenceProportionComboBox(EPProportionComboBox):
    KEY = "reference_proportion"
    PARAM_KEY = "reference_proportion"
    LABEL = "对照组的率/比例"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setCurrentText("0.80")


class MarginComboBox(EPMarginComboBox):
    KEY = "margin"
    PARAM_KEY = "margin"
    LABEL = "优效界值"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setCurrentText("0.05")


class SuperiorityProportionComboBox(EPProportionComboBox):
    KEY = "superiority_proportion"
    PARAM_KEY = "superiority_proportion"
    LABEL = "优效的率/比例阈值"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setCurrentText("0.85")


class TreatmentSizeComboBox(EPSizeComboBox):
    KEY = "treatment_size"
    PARAM_KEY = "treatment_size"
    LABEL = "试验组样本量"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)


class ReferenceSizeComboBox(EPSizeComboBox):
    KEY = "reference_size"
    PARAM_KEY = "reference_size"
    LABEL = "对照组样本量"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)


class SizeComboBox(EPSizeComboBox):
    pass


class AlternativeComboBox(EPType2AlternativeComboBox):
    pass


class RatioComboBox(EPRatioComboBox):
    KEY = "ratio"
    PARAM_KEY = "ratio"
    LABEL = "试验组：对照组"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)


class AlphaComboBox(EPAlphaComboBox):
    KEY = "alpha"
    PARAM_KEY = "alpha"
    LABEL = "显著性水平"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)


class PowerComboBox(EPPowerComboBox):
    KEY = "power"
    PARAM_KEY = "power"
    LABEL = "检验效能"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)


class MethodComboBox(EPComboBox):
    KEY = "method"
    PARAM_KEY = "method"
    LABEL = "检验方法"

    def __init__(self, parent=None) -> None:
        super().__init__(parent, items=["z-pooled", "z-unpooled"])


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


class TargetGroupBox(BaseTargetGroupBox):
    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            widgets_cls=[
                PowerComboBox,
                SizeComboBox,
                TreatmentProportionComboBox,
                ReferenceProportionComboBox,
                SuperiorityProportionComboBox,
                MarginComboBox,
            ],
        )


class ParamGroupBoxPower(BaseParamGroupBox):
    """GroupBox - 求解检验效能的参数面板"""

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            widgets_cls=[
                TreatmentProportionComboBox,
                ReferenceProportionComboBox,
                MarginComboBox,
                SuperiorityProportionComboBox,
                TreatmentSizeComboBox,
                ReferenceSizeComboBox,
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
                TreatmentProportionComboBox,
                ReferenceProportionComboBox,
                MarginComboBox,
                SuperiorityProportionComboBox,
                AlternativeComboBox,
                RatioComboBox,
                AlphaComboBox,
                PowerComboBox,
                MethodContinuityCorrectionCompositeWidget,
            ],
        )

        self._init_value()

    def _init_value(self) -> None:
        pass


class ParamGroupBoxTreatmentProportion(BaseParamGroupBox):
    """GroupBox - 求解试验组的率的参数面板"""

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            widgets_cls=[
                ReferenceProportionComboBox,
                MarginComboBox,
                SuperiorityProportionComboBox,
                TreatmentSizeComboBox,
                ReferenceSizeComboBox,
                AlternativeComboBox,
                AlphaComboBox,
                PowerComboBox,
                MethodContinuityCorrectionCompositeWidget,
            ],
        )

        self._init_value()

    def _init_value(self) -> None:
        pass


class ParamGroupBoxReferenceProportion(BaseParamGroupBox):
    """GroupBox - 求解对照组的率的参数面板"""

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            widgets_cls=[
                TreatmentProportionComboBox,
                MarginComboBox,
                TreatmentSizeComboBox,
                ReferenceSizeComboBox,
                AlternativeComboBox,
                AlphaComboBox,
                PowerComboBox,
                MethodContinuityCorrectionCompositeWidget,
            ],
        )

        self._init_value()

    def _init_value(self) -> None:
        pass


class ParamGroupBoxSuperiorityProportion(BaseParamGroupBox):
    """GroupBox - 求解优效性率的参数面板"""

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            widgets_cls=[
                TreatmentProportionComboBox,
                ReferenceProportionComboBox,
                TreatmentSizeComboBox,
                ReferenceSizeComboBox,
                AlternativeComboBox,
                AlphaComboBox,
                PowerComboBox,
                MethodContinuityCorrectionCompositeWidget,
            ],
        )

        self._init_value()

    def _init_value(self) -> None:
        pass


class ParamGroupBoxMargin(BaseParamGroupBox):
    """GroupBox - 求解优效界值的参数面板"""

    def __init__(self, parent=None) -> None:
        super().__init__(
            parent,
            widgets_cls=[
                TreatmentProportionComboBox,
                ReferenceProportionComboBox,
                TreatmentSizeComboBox,
                ReferenceSizeComboBox,
                AlternativeComboBox,
                AlphaComboBox,
                PowerComboBox,
                MethodContinuityCorrectionCompositeWidget,
            ],
        )

        self._init_value()

    def _init_value(self) -> None:
        pass


class PISPage(BasePage):
    """两独立样本率优效性检验页面"""

    LABEL = "两独立样本率优效性检验"

    def __init__(self, parent=None) -> None:

        self.gbx_target = TargetGroupBox()

        self.gbx_param_group_power = ParamGroupBoxPower()
        self.gbx_param_group_sample_size = ParamGroupBoxSampleSize()
        self.gbx_param_group_treatment_proportion = ParamGroupBoxTreatmentProportion()
        self.gbx_param_group_reference_proportion = ParamGroupBoxReferenceProportion()
        self.gbx_param_group_superiority_proportion = ParamGroupBoxSuperiorityProportion()
        self.gbx_param_group_margin = ParamGroupBoxMargin()
        self.gbx_params = (
            self.gbx_param_group_power,
            self.gbx_param_group_sample_size,
            self.gbx_param_group_treatment_proportion,
            self.gbx_param_group_reference_proportion,
            self.gbx_param_group_superiority_proportion,
            self.gbx_param_group_margin,
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

        self.ezpwr_module = self.ezpwr.proportion.independent.superiority
        self.solver_map = {
            0: self.ezpwr_module.solve_power,
            1: self.ezpwr_module.solve_size,
            2: self.ezpwr_module.solve_treatment_proportion,
            3: self.ezpwr_module.solve_reference_proportion,
            4: self.ezpwr_module.solve_superiority_proportion,
            5: self.ezpwr_module.solve_margin,
        }
