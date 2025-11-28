# ui/main_window.py

from PySide6.QtWidgets import QMainWindow, QWidget, QTabWidget, QVBoxLayout
from ui.tab_figurate import TabFigurate
from ui.tab_symgroup import TabSymGroup
from ui.tab_partition_gf import TabPartitionGF
from ui.tab_coeff_explorer import TabCoeffExplorer
from ui.tab_bruteforce import TabBruteForce

class MainWindow(QMainWindow):
    """
    Main application window with a tab widget.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Figurate Partition Explorer")
        self.resize(1100, 700)

        container = QWidget()
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        container.setLayout(layout)
        self.setCentralWidget(container)

        # Add tabs
        self.tab_figurate = TabFigurate()
        self.tabs.addTab(self.tab_figurate, "Figurate Explorer")

        # Tab 2: Symmetric Group Explorer
        self.tab_symgroup = TabSymGroup()
        self.tabs.addTab(self.tab_symgroup, "Symmetric Group")

        # Tab 3: Partition GF Builder
        self.tab_partition_gf = TabPartitionGF()
        self.tabs.addTab(self.tab_partition_gf, "Partition GFs")


        # Tab 4: Coefficient & Plot Explorer
        self.tab_coeff_explorer = TabCoeffExplorer()
        self.tabs.addTab(self.tab_coeff_explorer, "Coefficient Explorer")

        # Tab 5
        self.tab_bruteforce = TabBruteForce()
        self.tabs.addTab(self.tab_bruteforce, "Brute Force Checker")

