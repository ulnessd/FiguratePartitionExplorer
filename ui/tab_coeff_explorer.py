# ui/tab_coeff_explorer.py

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QSpinBox,
    QPushButton,
    QCheckBox,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
)
from PySide6.QtCore import Qt

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from partitions_gf import build_partition_generating_functions


class TabCoeffExplorer(QWidget):
    """
    Tab 4: Coefficient & Plot Explorer.

    Lets the user:
        - choose figurate family, m, N
        - choose which series to display:
            * representations ψ(q)^m
            * partitions P_{m,S}(q)
            * distinct partitions P_{m,S}^d(q)
        - select a range n_min..n_max
        - see a table of coefficients
        - see plots in several modes:
            * coefficients vs n (overlay)
            * ratio P^d / P
            * difference P - P^d
        - export the current data range to CSV
    """

    def __init__(self):
        super().__init__()

        # ----------------------------
        # Left control panel
        # ----------------------------
        left_layout = QVBoxLayout()

        # Figurate family
        self.combo_family = QComboBox()
        self.combo_family.addItems([
            "Triangular numbers T(j)",
            "Square numbers j^2",
            "Centered k-gonal numbers C_k(j)",
        ])

        self.spin_k = QSpinBox()
        self.spin_k.setRange(3, 50)
        self.spin_k.setValue(5)
        self.spin_k.setEnabled(False)

        # m and N
        self.spin_m = QSpinBox()
        self.spin_m.setRange(1, 20)
        self.spin_m.setValue(2)

        self.spin_N = QSpinBox()
        self.spin_N.setRange(10, 5000)
        self.spin_N.setValue(200)

        # Which series to show (for coefficient mode)
        self.check_reps = QCheckBox("Show representations ψ(q)^m")
        self.check_reps.setChecked(True)
        self.check_P = QCheckBox("Show partitions P_{m,S}(q)")
        self.check_P.setChecked(True)
        self.check_Pd = QCheckBox("Show distinct P_{m,S}^d(q)")
        self.check_Pd.setChecked(True)

        # Plot type
        self.combo_plot_mode = QComboBox()
        self.combo_plot_mode.addItems([
            "Coefficients vs n",
            "Ratio  P^d / P",
            "Difference  P - P^d",
        ])

        # n-range
        self.spin_n_min = QSpinBox()
        self.spin_n_min.setRange(0, 5000)
        self.spin_n_min.setValue(0)

        self.spin_n_max = QSpinBox()
        self.spin_n_max.setRange(0, 5000)
        self.spin_n_max.setValue(50)

        # Buttons
        self.btn_compute = QPushButton("Compute / Update")
        self.btn_export_csv = QPushButton("Export current data to CSV…")

        # Assemble left layout
        left_layout.addWidget(QLabel("Figurate family:"))
        left_layout.addWidget(self.combo_family)
        left_layout.addSpacing(8)

        left_layout.addWidget(QLabel("k (for centered polygonals):"))
        left_layout.addWidget(self.spin_k)
        left_layout.addSpacing(8)

        left_layout.addWidget(QLabel("Number of summands m:"))
        left_layout.addWidget(self.spin_m)
        left_layout.addSpacing(8)

        left_layout.addWidget(QLabel("Max exponent N:"))
        left_layout.addWidget(self.spin_N)
        left_layout.addSpacing(16)

        left_layout.addWidget(QLabel("Series to display (coeff mode):"))
        left_layout.addWidget(self.check_reps)
        left_layout.addWidget(self.check_P)
        left_layout.addWidget(self.check_Pd)
        left_layout.addSpacing(16)

        left_layout.addWidget(QLabel("Plot type:"))
        left_layout.addWidget(self.combo_plot_mode)
        left_layout.addSpacing(16)

        left_layout.addWidget(QLabel("Display range for n:"))
        left_layout.addWidget(QLabel("n_min:"))
        left_layout.addWidget(self.spin_n_min)
        left_layout.addWidget(QLabel("n_max:"))
        left_layout.addWidget(self.spin_n_max)
        left_layout.addSpacing(16)

        left_layout.addWidget(self.btn_compute)
        left_layout.addSpacing(16)
        left_layout.addWidget(self.btn_export_csv)
        left_layout.addStretch()

        self.combo_family.currentIndexChanged.connect(self._on_family_changed)

        # ----------------------------
        # Right side: summary, table, plot
        # ----------------------------
        right_layout = QVBoxLayout()

        self.label_info = QLabel(
            "Choose parameters on the left, then click "
            "<b>Compute / Update</b> to explore coefficients."
        )
        self.label_info.setWordWrap(True)
        right_layout.addWidget(self.label_info)

        # Coefficient table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "n",
            "ψ(q)^m",
            "P_{m,S}(q)",
            "P_{m,S}^d(q)",
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.table, stretch=2)

        # Plot
        self.fig = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.fig)
        right_layout.addWidget(self.canvas, stretch=3)

        # ----------------------------
        # Main layout
        # ----------------------------
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=3)
        self.setLayout(main_layout)

        # State
        self._result = None
        self._last_nmin = 0
        self._last_nmax = 0

        # Connections
        self.btn_compute.clicked.connect(self.compute_and_update)
        self.btn_export_csv.clicked.connect(self.export_csv)

    # -----------------------------------------------------
    def _on_family_changed(self):
        idx = self.combo_family.currentIndex()
        self.spin_k.setEnabled(idx == 2)

    def _get_family_key(self) -> str:
        idx = self.combo_family.currentIndex()
        if idx == 0:
            return "triangular"
        elif idx == 1:
            return "square"
        else:
            return "centered_k"

    # -----------------------------------------------------
    def compute_and_update(self):
        """
        Compute generating functions (if needed) and refresh table + plot.
        """
        family = self._get_family_key()
        m = self.spin_m.value()
        N = self.spin_N.value()
        compute_distinct = self.check_Pd.isChecked()  # only compute if we might show it

        k = None
        if family == "centered_k":
            k = self.spin_k.value()

        # Compute (always; cheap enough and keeps logic simple)
        self._result = build_partition_generating_functions(
            family=family,
            m=m,
            N=N,
            k=k,
            compute_distinct=compute_distinct,
        )

        # Clamp n_min, n_max to [0, N]
        nmin = max(0, min(self.spin_n_min.value(), N))
        nmax = max(0, min(self.spin_n_max.value(), N))
        if nmax < nmin:
            nmin, nmax = nmax, nmin

        # Update spin boxes to reflect clamped values
        self.spin_n_min.setMaximum(N)
        self.spin_n_max.setMaximum(N)
        self.spin_n_min.setValue(nmin)
        self.spin_n_max.setValue(nmax)

        # Remember last used range (for CSV export)
        self._last_nmin = nmin
        self._last_nmax = nmax

        self.update_summary_label()
        self.update_table(nmin, nmax)
        self.update_plot(nmin, nmax)

    # -----------------------------------------------------
    def update_summary_label(self):
        if self._result is None:
            return

        family = self._result["family"]
        m = self._result["m"]
        N = self._result["N"]
        k = self._result["k"]

        if family == "triangular":
            fname = "Triangular numbers T(j)"
        elif family == "square":
            fname = "Square numbers j^2"
        else:
            fname = f"Centered {k}-gonal numbers C_{k}(j)"

        self.label_info.setText(
            f"<b>Figurate family:</b> {fname} &nbsp; "
            f"<b>m:</b> {m} &nbsp; <b>N:</b> {N}"
        )

    # -----------------------------------------------------
    def update_table(self, nmin: int, nmax: int):
        if self._result is None:
            return

        reps = self._result["representations"]
        P = self._result["P"]
        P_distinct = self._result["P_distinct"]

        num_rows = nmax - nmin + 1
        self.table.setRowCount(num_rows)

        for i, n in enumerate(range(nmin, nmax + 1)):
            rep_val = reps[n] if n < len(reps) else 0
            P_val = P[n] if n < len(P) else 0
            if P_distinct is not None and n < len(P_distinct):
                Pd_str = str(P_distinct[n])
            else:
                Pd_str = ""

            items = [
                QTableWidgetItem(str(n)),
                QTableWidgetItem(str(rep_val)),
                QTableWidgetItem(str(P_val)),
                QTableWidgetItem(Pd_str),
            ]
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, col, item)

        self.table.resizeColumnsToContents()

    # -----------------------------------------------------
    def update_plot(self, nmin: int, nmax: int):
        if self._result is None:
            return

        reps = self._result["representations"]
        P = self._result["P"]
        P_distinct = self._result["P_distinct"]

        xs = list(range(nmin, nmax + 1))

        self.fig.clear()
        ax = self.fig.add_subplot(111)

        mode = self.combo_plot_mode.currentIndex()

        # Mode 0: coefficients vs n (overlay, original behavior)
        if mode == 0:
            show_reps = self.check_reps.isChecked()
            show_P = self.check_P.isChecked()
            show_Pd = self.check_Pd.isChecked() and (P_distinct is not None)

            if show_reps:
                ys_reps = [reps[n] if n < len(reps) else 0 for n in xs]
                ax.plot(xs, ys_reps, label="ψ(q)^m")

            if show_P:
                ys_P = [P[n] if n < len(P) else 0 for n in xs]
                ax.plot(xs, ys_P, label="P_{m,S}(q)")

            if show_Pd:
                ys_Pd = [P_distinct[n] if n < len(P_distinct) else 0 for n in xs]
                ax.plot(xs, ys_Pd, label="P_{m,S}^d(q)")

            ax.set_ylabel("Coefficient")
            if show_reps or show_P or show_Pd:
                ax.legend()

        # Mode 1: ratio P^d / P
        elif mode == 1:
            if P_distinct is None:
                ax.text(
                    0.5,
                    0.5,
                    "P_{m,S}^d(q) not computed.",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
            else:
                xs_ratio = []
                ys_ratio = []
                for n in xs:
                    if n < len(P) and n < len(P_distinct) and P[n] != 0:
                        xs_ratio.append(n)
                        ys_ratio.append(P_distinct[n] / P[n])

                if xs_ratio:
                    ax.plot(xs_ratio, ys_ratio, label="P^d / P")
                    ax.set_ylabel("Ratio")
                    ax.legend()
                else:
                    ax.text(
                        0.5,
                        0.5,
                        "No points with P_{m,S}(n) > 0 in range.",
                        ha="center",
                        va="center",
                        transform=ax.transAxes,
                    )

        # Mode 2: difference P - P^d
        elif mode == 2:
            if P_distinct is None:
                ax.text(
                    0.5,
                    0.5,
                    "P_{m,S}^d(q) not computed.",
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                )
            else:
                ys_diff = []
                for n in xs:
                    if n < len(P) and n < len(P_distinct):
                        ys_diff.append(P[n] - P_distinct[n])
                    else:
                        ys_diff.append(0)
                ax.plot(xs, ys_diff, label="P - P^d")
                ax.set_ylabel("Difference")
                ax.legend()

        ax.set_xlabel("n")
        ax.set_title("Generating function coefficients in selected range")
        self.canvas.draw()

    # -----------------------------------------------------
    def export_csv(self):
        """
        Export current data (for n in [nmin, nmax]) to a CSV file.

        Columns: n, psi^m, P_{m,S}, P_{m,S}^d
        """
        if self._result is None:
            return

        import csv

        nmin = self._last_nmin
        nmax = self._last_nmax

        reps = self._result["representations"]
        P = self._result["P"]
        P_distinct = self._result["P_distinct"]

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save coefficients to CSV",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )
        if not filename:
            return  # user cancelled

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["n", "psi^m", "P_{m,S}", "P_{m,S}^d"])

            for n in range(nmin, nmax + 1):
                psi_val = reps[n] if n < len(reps) else 0
                P_val = P[n] if n < len(P) else 0
                Pd_val = (
                    P_distinct[n]
                    if (P_distinct is not None and n < len(P_distinct))
                    else ""
                )
                writer.writerow([n, psi_val, P_val, Pd_val])
