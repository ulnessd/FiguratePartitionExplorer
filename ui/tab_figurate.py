# ui/tab_figurate.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QPushButton, QTableWidget,
    QTableWidgetItem, QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from figurate import (
    triangular_series, square_series, centered_polygonal_series
)
from series import pretty_print_series


class TabFigurate(QWidget):
    """
    Tab 1: Explore base figurate generating functions.
    """

    def __init__(self):
        super().__init__()

        # ----------------------------
        # Left control panel
        # ----------------------------
        left_layout = QVBoxLayout()

        # Figurate selector
        self.combo_family = QComboBox()
        self.combo_family.addItems([
            "Triangular numbers T(j)",
            "Square numbers j^2",
            "Centered k-gonal numbers C_k(j)"
        ])

        # k value for centered polygonals
        self.spin_k = QSpinBox()
        self.spin_k.setRange(3, 50)
        self.spin_k.setValue(5)
        self.spin_k.setEnabled(False)  # only enabled for centered polygonals

        # Max exponent N
        self.spin_N = QSpinBox()
        self.spin_N.setRange(1, 10000)
        self.spin_N.setValue(200)

        # Compute button
        self.btn_compute = QPushButton("Compute")

        left_layout.addWidget(QLabel("Figurate Family:"))
        left_layout.addWidget(self.combo_family)
        left_layout.addSpacing(12)

        left_layout.addWidget(QLabel("k (for centered polygonals):"))
        left_layout.addWidget(self.spin_k)
        left_layout.addSpacing(12)

        left_layout.addWidget(QLabel("Max exponent N:"))
        left_layout.addWidget(self.spin_N)
        left_layout.addSpacing(12)

        left_layout.addWidget(self.btn_compute)
        left_layout.addStretch()

        # Enable / disable k selector depending on choice
        self.combo_family.currentIndexChanged.connect(self._on_family_changed)

        # ----------------------------
        # Right display panel
        # ----------------------------
        right_layout = QVBoxLayout()

        self.label_info = QLabel("Generating function will appear here.")
        self.label_info.setWordWrap(True)
        right_layout.addWidget(self.label_info)

        # Table for coefficients
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["n", "coeff[n]"])
        self.table.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.table, stretch=1)

        # Plot area (matplotlib)
        self.fig = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)
        right_layout.addWidget(self.canvas, stretch=1)

        # ----------------------------
        # Main grid layout
        # ----------------------------
        main_layout = QGridLayout()
        main_layout.addLayout(left_layout, 0, 0)
        main_layout.addLayout(right_layout, 0, 1)

        self.setLayout(main_layout)

        # Button connection
        self.btn_compute.clicked.connect(self.compute_series)

    # -----------------------------------------------------
    def _on_family_changed(self):
        """Enable/disable the spin_k widget depending on family."""
        idx = self.combo_family.currentIndex()
        self.spin_k.setEnabled(idx == 2)

    # -----------------------------------------------------
    def compute_series(self):
        """
        Compute the chosen figurate generating function and update display.
        """
        idx = self.combo_family.currentIndex()
        N = self.spin_N.value()

        if idx == 0:
            # Triangular
            coeffs = triangular_series(N)
            name = "Triangular numbers T(j)"
        elif idx == 1:
            # Squares
            coeffs = square_series(N)
            name = "Squares j^2"
        else:
            # Centered polygonal
            k = self.spin_k.value()
            coeffs = centered_polygonal_series(k, N)
            name = f"Centered {k}-gonal numbers C_{k}(j)"

        # Update description
        series_str = pretty_print_series(coeffs[:50])  # show first few terms
        self.label_info.setText(
            f"<b>{name}</b><br>"
            f"Showing first few nonzero terms:<br>"
            f"<code>{series_str}</code>"
        )

        # Update table
        self.update_table(coeffs)

        # Update plot
        self.plot_series(coeffs)

    # -----------------------------------------------------
    def update_table(self, coeffs):
        """
        Fill the table with (n, coeff[n]) up to N.
        """
        N = len(coeffs) - 1
        self.table.setRowCount(N + 1)

        for n in range(N + 1):
            item_n = QTableWidgetItem(str(n))
            item_c = QTableWidgetItem(str(coeffs[n]))
            item_n.setTextAlignment(Qt.AlignCenter)
            item_c.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(n, 0, item_n)
            self.table.setItem(n, 1, item_c)

        self.table.resizeColumnsToContents()

    # -----------------------------------------------------
    def plot_series(self, coeffs):
        """
        Plot the generating function coefficients.
        """
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        xs = []
        ys = []
        for n, c in enumerate(coeffs):
            if c != 0:
                xs.append(n)
                ys.append(c)

        # Matplotlib >= 3.9 removed 'use_line_collection'
        try:
            ax.stem(xs, ys, basefmt=" ")
        except TypeError:
            # For older versions that still require the argument
            ax.stem(xs, ys, basefmt=" ", use_line_collection=True)

        ax.set_xlabel("n")
        ax.set_ylabel("coeff[n]")
        ax.set_title("Non-zero generating function coefficients")

        self.canvas.draw()
