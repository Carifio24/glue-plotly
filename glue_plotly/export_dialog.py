
import os

from qtpy.QtWidgets import QDialog, QLabel, QVBoxLayout
from qtpy.QtCore import QTimer, Qt

from glue.utils.qt import load_ui


class ExportDialog(QDialog):

    max_dots = 3

    def __init__(self, parent=None):
        super(ExportDialog, self).__init__(parent=parent, flags=Qt.FramelessWindowHint)

        # self.ui = load_ui('export_dialog.ui', self,
        #                   directory=os.path.dirname(__file__))
        # self.label = self.ui.label

        self.label = QLabel()
        self.label.setText("Exporting to Plotly")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        self.setModal(True)
        #self.setWindowFlags(Qt.FramelessWindowHint)

        ending_spaces = " " * self.max_dots
        if not self.label.text().endswith(ending_spaces):
            self.label.setText(self.label.text() + ending_spaces)
        self.n_dots = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_update)
        self.timer.start(500)

    def _on_timer_update(self):
        self.n_dots = ((self.n_dots + 1) % (self.max_dots + 1)) or self.max_dots
        print(self.n_dots)
        text = self.label.text()
        text = text[:-self.max_dots] + "." * self.n_dots + " " * (self.max_dots - self.n_dots)
        self.label.setText(text)

    def close(self):
        super(ExportDialog, self).close()
        self.timer.stop()