from PyQt6.QtCore import QThread, pyqtSignal


class AnalysisWorker(QThread):
    """Выполняет вызов backend-сервиса в отдельном потоке, чтобы не блокировать UI."""

    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as exc:
            self.failed.emit(str(exc))
