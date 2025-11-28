# ui/tab_bruteforce.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QComboBox, QSpinBox, QPushButton, QCheckBox,
    QTableWidget, QTableWidgetItem, QTextEdit
)
from PySide6.QtCore import Qt

from partitions_gf import build_partition_generating_functions
from bruteforce_partitions import (
    figurate_values_up_to,
    count_ordered_representations,
    count_unordered_partitions_non_distinct,
    count_unordered_partitions_distinct,
)


class TabBruteForce(QWidget):
    """
    Tab 5: Brute Force Checker.

    For given family, m, and target n, we:
        - compute coefficients from generating functions ψ(q)^m, P, P^d
        - compute counts by brute force
        - compare them
        - optionally show explicit examples of representations / partitions
    """

    def __init__(self):
        super().__init__()

        # ----------------------------
        # Left controls
        # ----------------------------
        left_layout = QVBoxLayout()

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
        self.spin_m.setValue(3)

        self.spin_n = QSpinBox()
        self.spin_n.setRange(0, 1000)
        self.spin_n.setValue(10)

        self.spin_max_examples = QSpinBox()
        self.spin_max_examples.setRange(0, 500)
        self.spin_max_examples.setValue(50)

        self.check_show_examples = QCheckBox("List example solutions")
        self.check_show_examples.setChecked(True)

        self.btn_run = QPushButton("Run brute-force check")

        left_layout.addWidget(QLabel("Figurate family:"))
        left_layout.addWidget(self.combo_family)
        left_layout.addSpacing(8)

        left_layout.addWidget(QLabel("k (for centered polygonals):"))
        left_layout.addWidget(self.spin_k)
        left_layout.addSpacing(8)

        left_layout.addWidget(QLabel("Number of summands m:"))
        left_layout.addWidget(self.spin_m)
        left_layout.addSpacing(8)

        left_layout.addWidget(QLabel("Target n (sum value):"))
        left_layout.addWidget(self.spin_n)
        left_layout.addSpacing(16)

        left_layout.addWidget(QLabel("Max examples to list:"))
        left_layout.addWidget(self.spin_max_examples)
        left_layout.addWidget(self.check_show_examples)
        left_layout.addSpacing(16)

        left_layout.addWidget(self.btn_run)
        left_layout.addStretch()

        self.combo_family.currentIndexChanged.connect(self._on_family_changed)

        # ----------------------------
        # Right side: summary, comparison table, examples
        # ----------------------------
        right_layout = QVBoxLayout()

        self.label_summary = QLabel(
            "Choose parameters on the left and click "
            "<b>Run brute-force check</b>."
        )
        self.label_summary.setWordWrap(True)
        right_layout.addWidget(self.label_summary)

        # Comparison table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Series",
            "GF coefficient",
            "Brute-force count",
            "Match?",
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.table, stretch=2)

        # Text area for explicit examples
        self.text_examples = QTextEdit()
        self.text_examples.setReadOnly(True)
        right_layout.addWidget(self.text_examples, stretch=3)

        # ----------------------------
        # Main layout
        # ----------------------------
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=3)
        self.setLayout(main_layout)

        # Connections
        self.btn_run.clicked.connect(self.run_check)

        self._last_result = None

    # -----------------------------------------------------
    def _on_family_changed(self):
        idx = self.combo_family.currentIndex()
        self.spin_k.setEnabled(idx == 2)

    def _get_family_key(self):
        idx = self.combo_family.currentIndex()
        if idx == 0:
            return "triangular"
        elif idx == 1:
            return "square"
        else:
            return "centered_k"

    # -----------------------------------------------------
    def run_check(self):
        family = self._get_family_key()
        m = self.spin_m.value()
        n = self.spin_n.value()
        max_examples = self.spin_max_examples.value()
        show_examples = self.check_show_examples.isChecked()

        k = None
        if family == "centered_k":
            k = self.spin_k.value()

        # Compute generating functions up to exponent N >= n
        N = max(n, 10)
        result = build_partition_generating_functions(
            family=family,
            m=m,
            N=N,
            k=k,
            compute_distinct=True,
        )
        self._last_result = result

        reps = result["representations"]
        P = result["P"]
        P_distinct = result["P_distinct"]

        gf_reps = reps[n] if n < len(reps) else 0
        gf_P = P[n] if n < len(P) else 0
        gf_Pd = P_distinct[n] if (P_distinct is not None and n < len(P_distinct)) else 0

        # Brute force values
        values = figurate_values_up_to(family, n, k)

        bf_reps, ex_reps = count_ordered_representations(values, m, n, max_examples)
        bf_P, ex_P = count_unordered_partitions_non_distinct(values, m, n, max_examples)
        bf_Pd, ex_Pd = count_unordered_partitions_distinct(values, m, n, max_examples)

        # Summary label
        fam_name = self._family_name_for_display(family, k)
        self.label_summary.setText(
            f"<b>Family:</b> {fam_name}; "
            f"<b>m = {m}</b>, <b>n = {n}</b><br>"
            "Comparing generating-function coefficients with explicit enumeration."
        )

        # Fill comparison table
        rows = [
            ("ψ(q)^m (ordered reps)", gf_reps, bf_reps),
            ("P_{m,S}(q) (unordered)", gf_P, bf_P),
            ("P_{m,S}^d(q) (distinct)", gf_Pd, bf_Pd),
        ]
        self.table.setRowCount(len(rows))

        for row_idx, (label, gf_val, bf_val) in enumerate(rows):
            match = (gf_val == bf_val)
            match_text = "✔" if match else "✘"
            items = [
                QTableWidgetItem(label),
                QTableWidgetItem(str(gf_val)),
                QTableWidgetItem(str(bf_val)),
                QTableWidgetItem(match_text),
            ]
            for col, item in enumerate(items):
                if col == 3:
                    # Center the match symbol and maybe bold it
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col, item)

        self.table.resizeColumnsToContents()

        # Examples text
        if show_examples:
            self._update_examples_text(values, ex_reps, ex_P, ex_Pd)
        else:
            self.text_examples.clear()

    # -----------------------------------------------------
    def _family_name_for_display(self, family_key: str, k: int | None) -> str:
        if family_key == "triangular":
            return "Triangular numbers T(j)"
        elif family_key == "square":
            return "Square numbers j^2"
        else:
            return f"Centered {k}-gonal numbers C_{k}(j)"

    def _update_examples_text(
        self,
        values,
        ex_reps,
        ex_P,
        ex_Pd,
    ):
        lines = []
        lines.append("Figurate values used (≤ n):")
        lines.append(str(values))
        lines.append("")

        def fmt_tuple(t):
            return "(" + ", ".join(str(x) for x in t) + ")"

        lines.append("Ordered representations (examples):")
        if ex_reps:
            for t in ex_reps:
                lines.append("  " + fmt_tuple(t))
        else:
            lines.append("  [none]")
        lines.append("")

        lines.append("Unordered partitions (nondecreasing, examples):")
        if ex_P:
            for t in ex_P:
                lines.append("  " + fmt_tuple(t))
        else:
            lines.append("  [none]")
        lines.append("")

        lines.append("Unordered distinct partitions (examples):")
        if ex_Pd:
            for t in ex_Pd:
                lines.append("  " + fmt_tuple(t))
        else:
            lines.append("  [none]")

        self.text_examples.setPlainText("\n".join(lines))
