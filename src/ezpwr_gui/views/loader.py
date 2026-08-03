import importlib

from PySide6.QtCore import QThread, Signal


class CoreLibLoaderThread(QThread):
    """后台异步加载算法库的线程"""

    loaded_signal = Signal(object)
    failed_signal = Signal(object)

    def run(self) -> None:
        try:
            ezpwr = importlib.import_module("ezpwr")

            self.loaded_signal.emit(ezpwr)

        except Exception as e:  # noqa: BLE001
            self.failed_signal.emit(str(e))
