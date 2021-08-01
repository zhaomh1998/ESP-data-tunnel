import re
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class NodeTableModel(QAbstractTableModel):
    def __init__(self, backend):
        super(NodeTableModel, self).__init__()
        self.headers = ['Status', 'Node ID', 'IP', 'Ping Loss']
        self.backend = backend

    def data(self, index, role):
        if role == Qt.DisplayRole:
            nth_node = index.row()
            col = index.column()
            nodes_sorted = sorted(self.backend.nodes.keys())
            if col == 0:
                return 'OK'
            elif col == 1:
                return nodes_sorted[nth_node]
            elif col == 2:
                return self.backend.nodes[nodes_sorted[nth_node]].addr[0]
            elif col == 3:
                return self.backend.nodes[nodes_sorted[nth_node]].loss_cntr.get_loss()
            else:
                raise NotImplementedError(f'Column {col} data() not implemented!')

    def rowCount(self, index):
        return len(self.backend.nodes)

    def columnCount(self, index):
        return len(self.headers)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)
