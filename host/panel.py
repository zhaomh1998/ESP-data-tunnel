import sys

from server import Server
from ui.panel_ui import *
from ui.models import *


class BackendWorker(QObject, Server):
    nodes_updated = pyqtSignal()

    def __init__(self, port=8000):
        super().__init__(args={'server_port': port})

    def run(self):
        self.set_mac_interval(3)
        self.set_ping_interval(0.5)
        self.start()

    def nodelist_update(self):
        """ Callback for any updates on node list (node goes online / offline) """
        self.nodes_updated.emit()


class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.backend = BackendWorker()
        self.backend_thread = QThread()
        self.nodes_model = NodeTableModel(self.backend)
        self.refresh_panel_timer = QTimer(self)

        self.start_backend()
        self.init_panel()
        self.init_callback()

    def start_backend(self):
        self.backend.moveToThread(self.backend_thread)
        self.backend_thread.started.connect(self.backend.run)
        self.backend.nodes_updated.connect(self.refresh_panel)
        self.backend_thread.start()

    def init_callback(self):
        self.button_refresh.clicked.connect(self.refresh_panel)

    def init_panel(self):
        self.table_nodes.setModel(self.nodes_model)
        self.refresh_panel_timer.setInterval(1000)
        self.refresh_panel_timer.timeout.connect(self.refresh_panel)
        self.refresh_panel_timer.start()

    def refresh_panel(self):
        self.nodes_model.layoutChanged.emit()


if __name__ == "__main__":
    sys.argv += []
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
