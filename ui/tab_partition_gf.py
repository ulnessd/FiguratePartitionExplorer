# ui/tab_partition_gf.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QPushButton, QCheckBox,
    QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt

from partitions_gf import build_partition_generating_functions


class TabPartitionGF(QWidget):
    """
    Tab 3: Partition Generating Functions (Main Theorem Playground).

    Lets the user choose:
        - figurate family (triangular / square / centered k-gonal)
        - m (number of summands)
        - N (max exponent)
    and then computes:
        - ψ(q)^m (representations)
        - P_{m,S}(q) (partitions)
        - P_{m,S}^d(q) (distinct partitions, optional)
    """

    def __init__(self):
        super().__init__()

        # ----------------------------
        # Left controls
        # ----------------------------
        left_layout = QVBoxLayout()

        # Figurate family selector
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

        self.spin_m = QSpinBox()
        self.spin_m.setRange(1, 7)
        self.spin_m.setValue(2)

        self.spin_N = QSpinBox()
        self.spin_N.setRange(10, 1000)
        self.spin_N.setValue(100)

        self.check_distinct = QCheckBox("Compute distinct partitions P^d(q)")
        self.check_distinct.setChecked(True)

        self.btn_compute = QPushButton("Compute generating functions")

        left_layout.addWidget(QLabel("Figurate family:"))
        left_layout.addWidget(self.combo_family)
        left_layout.addSpacing(10)

        left_layout.addWidget(QLabel("k (for centered polygonals):"))
        left_layout.addWidget(self.spin_k)
        left_layout.addSpacing(10)

        left_layout.addWidget(QLabel("Number of summands m:"))
        left_layout.addWidget(self.spin_m)
        left_layout.addSpacing(10)

        left_layout.addWidget(QLabel("Max exponent N:"))
        left_layout.addWidget(self.spin_N)
        left_layout.addSpacing(10)

        left_layout.addWidget(self.check_distinct)
        left_layout.addSpacing(10)

        left_layout.addWidget(self.btn_compute)
        left_layout.addStretch()

        self.combo_family.currentIndexChanged.connect(self._on_family_changed)

        # ----------------------------
        # Right display area
        # ----------------------------
        right_layout = QVBoxLayout()

        self.label_summary = QLabel(
            "Choose parameters on the left and click "
            "<b>Compute generating functions</b>."
        )
        self.label_summary.setWordWrap(True)
        right_layout.addWidget(self.label_summary)

        # Table of conjugacy classes and C_i(q) info
        self.table_classes = QTableWidget()
        self.table_classes.setColumnCount(6)
        self.table_classes.setHorizontalHeaderLabels([
            "Cycle type",
            "Class size",
            "Parity",
            "Example",
            "ψ-term",
            "Coefficient in sum",
        ])
        self.table_classes.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.table_classes, stretch=3)

        # Table of coefficients (preview)
        self.table_coeffs = QTableWidget()
        self.table_coeffs.setColumnCount(4)
        self.table_coeffs.setHorizontalHeaderLabels([
            "n",
            "ψ(q)^m",
            "P_{m,S}(q)",
            "P_{m,S}^d(q)",
        ])
        self.table_coeffs.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.table_coeffs, stretch=2)

        # ----------------------------
        # Main layout
        # ----------------------------
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=3)
        self.setLayout(main_layout)

        # State to hold last computation result
        self._last_result = None

        # Connections
        self.btn_compute.clicked.connect(self.compute_gfs)

    # -----------------------------------------------------
    def _on_family_changed(self):
        idx = self.combo_family.currentIndex()
        self.spin_k.setEnabled(idx == 2)

    # -----------------------------------------------------
    def _get_family_key(self):
        idx = self.combo_family.currentIndex()
        if idx == 0:
            return "triangular"
        elif idx == 1:
            return "square"
        else:
            return "centered_k"

    # -----------------------------------------------------
    def compute_gfs(self):
        family_key = self._get_family_key()
        m = self.spin_m.value()
        N = self.spin_N.value()
        compute_distinct = self.check_distinct.isChecked()

        k = None
        if family_key == "centered_k":
            k = self.spin_k.value()

        result = build_partition_generating_functions(
            family=family_key,
            m=m,
            N=N,
            k=k,
            compute_distinct=compute_distinct,
        )
        self._last_result = result

        self.update_summary_label(result)
        self.update_class_table(result)
        self.update_coeff_table(result)

    # -----------------------------------------------------
    def update_summary_label(self, result):
        family = result["family"]
        m = result["m"]
        N = result["N"]
        k = result["k"]

        if family == "triangular":
            fname = "Triangular numbers T(j)"
        elif family == "square":
            fname = "Square numbers j^2"
        else:
            fname = f"Centered {k}-gonal numbers C_{k}(j)"

        text = (
            f"<b>Figurate family:</b> {fname}<br>"
            f"<b>m:</b> {m}  &nbsp;&nbsp;  <b>N (max exponent):</b> {N}<br><br>"
            f"Representations are given by ψ(q)<sup>{m}</sup>.<br>"
            f"The partition generating function is:<br>"
            f"&emsp;P<sub>{m},S</sub>(q) = (1/{m}!) Σ |C_i| C_i(q).<br>"
        )
        if result["P_distinct"] is not None:
            text += (
                "The distinct-partitions generating function is:<br>"
                f"&emsp;P<sub>{m},S</sub><sup>d</sup>(q) = "
                f"(1/{m}!) Σ sign(C_i) |C_i| C_i(q)."
            )

        self.label_summary.setText(text)

    # -----------------------------------------------------
    def update_class_table(self, result):
        classes = result["class_data"]
        m = result["m"]
        m_fact = 1
        for i in range(2, m + 1):
            m_fact *= i

        self.table_classes.setRowCount(len(classes))

        for row, c in enumerate(classes):
            ct = c["cycle_type"]
            ct_str = "(" + ", ".join(str(x) for x in ct) + ")"
            class_size = c["class_size"]
            parity = c["parity"]
            example = c["example"]
            psi_term = c["psi_term"]

            # coefficient in the P sum: |C_i| / m!
            coeff_num = class_size
            coeff_den = m_fact
            coeff_str = f"{coeff_num}/{coeff_den}"

            items = [
                QTableWidgetItem(ct_str),
                QTableWidgetItem(str(class_size)),
                QTableWidgetItem(parity),
                QTableWidgetItem(example),
                QTableWidgetItem(psi_term),
                QTableWidgetItem(coeff_str),
            ]
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                self.table_classes.setItem(row, col, item)

        self.table_classes.resizeColumnsToContents()

    # -----------------------------------------------------
    def update_coeff_table(self, result):
        reps = result["representations"]
        P = result["P"]
        P_distinct = result["P_distinct"]

        # Show only the first few coefficients for preview
        N = result["N"]
        max_rows = min(30, N + 1)

        self.table_coeffs.setRowCount(max_rows)

        for n in range(max_rows):
            rep_val = reps[n] if n < len(reps) else 0
            P_val = P[n] if n < len(P) else 0
            if P_distinct is not None and n < len(P_distinct):
                Pd_val = P_distinct[n]
                Pd_str = str(Pd_val)
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
                self.table_coeffs.setItem(n, col, item)

        self.table_coeffs.resizeColumnsToContents()
