# ui/tab_symgroup.py

from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QSpinBox, QPushButton, QTableWidget,
    QTableWidgetItem, QTextEdit
)
from PySide6.QtCore import Qt

from symmetric_group import conjugacy_classes_Sm


class TabSymGroup(QWidget):
    """
    Tab 2: Explore conjugacy classes (cycle types) of S_m.
    Shows:
        - cycle types as partitions
        - class sizes
        - parity (even/odd)
        - example permutation
        - ψ-term structure
        - index-equality pattern description
    """

    def __init__(self):
        super().__init__()

        # ----------------------------
        # Left control panel
        # ----------------------------
        left_layout = QVBoxLayout()

        left_layout.addWidget(QLabel("Symmetric Group S_m"))

        self.spin_m = QSpinBox()
        self.spin_m.setRange(2, 20)
        self.spin_m.setValue(4)
        left_layout.addWidget(QLabel("Choose m:"))
        left_layout.addWidget(self.spin_m)

        self.btn_compute = QPushButton("Compute cycle types")
        left_layout.addWidget(self.btn_compute)

        left_layout.addStretch()

        # ----------------------------
        # Right display panel
        # ----------------------------
        right_layout = QVBoxLayout()

        self.label_summary = QLabel("Conjugacy classes will appear here.")
        self.label_summary.setWordWrap(True)
        right_layout.addWidget(self.label_summary)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Cycle type",
            "Example",
            "Class size",
            "Parity",
            "ψ-term structure",
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.table, stretch=3)

        # Details area for index pattern
        self.text_details = QTextEdit()
        self.text_details.setReadOnly(True)
        right_layout.addWidget(self.text_details, stretch=2)

        # ----------------------------
        # Main layout
        # ----------------------------
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, stretch=1)
        main_layout.addLayout(right_layout, stretch=3)

        self.setLayout(main_layout)

        # Connections
        self.btn_compute.clicked.connect(self.update_classes)
        self.table.currentCellChanged.connect(self.on_row_selected)

        # Initial compute
        self.update_classes()

    # -----------------------------------------------------
    def update_classes(self):
        m = self.spin_m.value()
        classes = conjugacy_classes_Sm(m)

        self.label_summary.setText(
            f"Conjugacy classes of S<sub>{m}</sub>: "
            f"{len(classes)} classes (one per partition of {m})."
        )

        self._classes = classes  # store for later use in selection handler

        self.table.setRowCount(len(classes))
        for row, c in enumerate(classes):
            ct_str = "(" + ", ".join(str(x) for x in c["cycle_type"]) + ")"
            items = [
                QTableWidgetItem(ct_str),
                QTableWidgetItem(c["example"]),
                QTableWidgetItem(str(c["class_size"])),
                QTableWidgetItem(c["parity"]),
                QTableWidgetItem(c["psi_term"]),
            ]
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

        self.table.resizeColumnsToContents()

        # Select first row by default
        if classes:
            self.table.setCurrentCell(0, 0)
            self.show_details_for_row(0)
        else:
            self.text_details.clear()

    # -----------------------------------------------------
    def on_row_selected(self, current_row, current_column, prev_row, prev_column):
        if current_row < 0:
            return
        self.show_details_for_row(current_row)

    # -----------------------------------------------------
    def show_details_for_row(self, row: int):
        if not hasattr(self, "_classes"):
            return
        if row < 0 or row >= len(self._classes):
            return
        c = self._classes[row]
        m = self.spin_m.value()
        ct = c["cycle_type"]
        pattern = c["index_pattern"]

        text = []
        text.append(f"Cycle type: {ct}")
        text.append(f"Class size: {c['class_size']}")
        text.append(f"Parity: {c['parity']}")
        text.append(f"Example permutation: {c['example']}")
        text.append("")
        text.append("Index-equality pattern:")
        text.append(pattern)
        text.append("")
        text.append("ψ-term structure (generic figurate family):")
        text.append(c["psi_term"])
        text.append("")
        text.append(
            "Interpretation:\n"
            "Each cycle length ℓ contributes a factor ψ(q^ℓ) for the base "
            "generating function (triangular, square, etc.). This tab is "
            "about the symmetry structure only; figurate choice enters elsewhere."
        )

        self.text_details.setPlainText("\n".join(text))
