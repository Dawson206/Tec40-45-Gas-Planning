import customtkinter as ctk
import json
from tkinter import filedialog
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class GasPlanningApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tec40-45 Gas Planning Sheet")
        self.geometry("1000x1150")

        self.sections = {}

        # --- General Info ---
        general_frame = ctk.CTkFrame(self)
        general_frame.pack(padx=10, pady=10, fill="x")
        self.sections['General Info'] = self.add_entry_row(
            general_frame, ["Max Depth", "Gas Mix", "Bottom Time", "Gradient Factor (Lo/Hi)", "Total Back Gas Req (CUFT/PSI)", "Deco Gas Req (CUFT)",]
        )

        # --- Gas Reserve / Rock Bottom ---
        reserve_frame = ctk.CTkFrame(self)
        reserve_frame.pack(padx=10, pady=10, fill="x")
        self.sections['Gas Reserve / Rock Bottom'] = self.add_entry_row(
            reserve_frame, ["First Gas Switch Depth", "Gas Reserve Volume For Two Divers (CUFT)", "Rock Bottom Pressure (PSI) [Total/Per Tank]"]
        )
        self.sections['Gas Reserve (Emergency)'] = self.add_table(
            reserve_frame, "Gas Reserve (Emergency)",
            ["Depth", "ATA", "Emergency SAC", "Time", "Gas Volume"], rows=3
        )

        # Max Depth → Gas Reserve Emergency Row 1
        max_depth_entry = self.sections['General Info'][0][1]
        row1_depth_entry = self.sections['Gas Reserve (Emergency)'][0][1][0][0]
        row1_ata_entry   = self.sections['Gas Reserve (Emergency)'][0][1][1][0]  # ATA column

        def update_row1_depth(event=None):
            try:
                val = max_depth_entry.get()
                float(val)
                row1_depth_entry.delete(0, "end")
                row1_depth_entry.insert(0, val)

                # Update ATA automatically
                ata_val = float(val) / 33 + 1
                row1_ata_entry.delete(0, "end")
                row1_ata_entry.insert(0, f"{ata_val:.2f}")
            except ValueError:
                pass

        max_depth_entry.bind("<KeyRelease>", update_row1_depth)

        # References
        max_depth_entry   = self.sections['General Info'][0][1]       # Max Depth
        first_gas_entry   = self.sections['Gas Reserve / Rock Bottom'][0][1]  # First Gas Switch Depth
        row2_depth_entry  = self.sections['Gas Reserve (Emergency)'][1][1][0][0]  # Row 2 Depth
        row2_ata_entry    = self.sections['Gas Reserve (Emergency)'][1][1][1][0]  # Row 2 ATA

        def update_row2_midpoint(event=None):
            try:
                max_depth = float(max_depth_entry.get())
                first_gas = float(first_gas_entry.get())
                midpoint = (max_depth + first_gas) / 2
                row2_depth_entry.delete(0, "end")
                row2_depth_entry.insert(0, f"{midpoint:.1f}")
                # Update ATA
                ata_val = midpoint / 33 + 1
                row2_ata_entry.delete(0, "end")
                row2_ata_entry.insert(0, f"{ata_val:.2f}")
            except ValueError:
                # If either field is empty/non-numeric, keep (A)
                row2_depth_entry.delete(0, "end")
                row2_depth_entry.insert(0, "(A)")
                row2_ata_entry.delete(0, "end")

        # Bind both Max Depth and First Gas
        max_depth_entry.bind("<KeyRelease>", update_row2_midpoint)
        first_gas_entry.bind("<KeyRelease>", update_row2_midpoint)


        row1_depth_entry = self.sections['Gas Reserve (Emergency)'][0][1][0][0]  # Row 1 Depth
        row2_depth_entry = self.sections['Gas Reserve (Emergency)'][1][1][0][0]  # Row 2 Depth
        row2_ata_entry   = self.sections['Gas Reserve (Emergency)'][1][1][1][0]  # Row 2 ATA
        row3_depth_entry = self.sections['Gas Reserve (Emergency)'][2][1][0][0]  # Row 3 Depth
        row3_ata_entry   = self.sections['Gas Reserve (Emergency)'][2][1][1][0]  # Row 3 ATA
        first_gas_entry  = self.sections['Gas Reserve / Rock Bottom'][0][1]       # First Gas Switch Depth

        def update_row3_depth(event=None):
            try:
                val = first_gas_entry.get()
                float(val)  # ensures it's numeric
                # Update Row 3
                row3_depth_entry.delete(0, "end")
                row3_depth_entry.insert(0, val)
                ata_val = float(val) / 33 + 1
                row3_ata_entry.delete(0, "end")
                row3_ata_entry.insert(0, f"{ata_val:.2f}")

                # Update Row 2 if it currently contains (A)
                if row2_depth_entry.get() == "(A)":
                    try:
                        depth1 = float(row1_depth_entry.get())
                        depth3 = float(val)
                        midpoint = (depth1 + depth3) / 2
                        row2_depth_entry.delete(0, "end")
                        row2_depth_entry.insert(0, f"{midpoint:.1f}")
                        # Update ATA for Row 2
                        ata_val2 = midpoint / 33 + 1
                        row2_ata_entry.delete(0, "end")
                        row2_ata_entry.insert(0, f"{ata_val2:.2f}")
                    except ValueError:
                        pass  # in case Row 1 is still empty
            except ValueError:
                pass

        first_gas_entry.bind("<KeyRelease>", update_row3_depth)

        # Update Gas Reserve for Two Divers
        row3_gas_entry = self.sections['Gas Reserve (Emergency)'][2][1][4][0]  # Row 3 Gas Volume
        two_divers_entry = self.sections['Gas Reserve / Rock Bottom'][1][1]     # Gas Reserve Volume For Two Divers

        def update_two_diver_reserve(event=None):
            try:
                val = float(row3_gas_entry.get())
                two_divers_entry.delete(0, "end")
                two_divers_entry.insert(0, f"{val*2:.1f}")
            except ValueError:
                two_divers_entry.delete(0, "end")

        # Bind callback to Row 3 Gas Volume changes
        row3_gas_entry.bind("<KeyRelease>", update_two_diver_reserve)

        # --- Bottom Gas Requirements ---
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(padx=10, pady=10, fill="x")
        self.sections['Bottom Gas Requirements'] = self.add_table(
            bottom_frame, "Bottom Gas Requirements",
            ["Depth", "ATA", "SAC", "Time", "Gas Volume"], rows=1
        )

        # --- Deco Stops ---
        deco_frame = ctk.CTkFrame(self)
        deco_frame.pack(padx=10, pady=10, fill="x")
        self.sections['Deco Stops'] = self.add_table(
            deco_frame, "Deco Stops", ["Depth", "Time"], rows=6,
            default_depths=["70", "60", "50", "40", "30", "20"]
        )

        # --- Deco Gas Requirements ---
        deco_gas_frame = ctk.CTkFrame(self)
        deco_gas_frame.pack(padx=10, pady=10, fill="x")
        self.sections['Deco Gas Requirements'] = self.add_table(
            deco_gas_frame, "Deco Gas Requirements",
            ["Depth", "ATA", "SAC", "Time", "Gas Volume"], rows=7,
            default_depths=["70", "60", "50", "40", "30", "20"],
            default_atas=["3.1", "2.8", "2.5", "2.2", "1.9", "1.6"],
            default_sac=[".6", ".6", ".6", ".6", ".6", ".6"],
            default_total=["", "", "", "", "", "", "Total"]
        )

        # --- Sync Deco Stops -> Deco Gas Requirements (time), recalc gas + total ---
        deco_stops = self.sections['Deco Stops']                 # 6 rows
        deco_gas   = self.sections['Deco Gas Requirements']      # 7 rows (last = total)

        def recalc_deco_total():
            total = 0.0
            for row in deco_gas[:6]:  # sum first 6 rows
                gv = row[1][4][0]     # Gas Volume entry
                try:
                    total += float(gv.get())
                except ValueError:
                    pass

            total_entry = deco_gas[6][1][4][0]  # row 7 Gas Volume cell
            # it's readonly (set in add_table), so temporarily enable, write, then lock
            try:
                total_entry.configure(state="normal")
            except Exception:
                pass
            total_entry.delete(0, "end")
            total_entry.insert(0, f"{total:.2f}")
            try:
                total_entry.configure(state="readonly")
            except Exception:
                pass

        # Build per-row callback to mirror Time and compute gas
        def make_sync_and_calc(i):
            src_time = deco_stops[i][1][1][0]   # Deco Stops: Time (col 1)
            dst_time = deco_gas[i][1][3][0]     # Deco Gas Req: Time (col 3)
            ata      = deco_gas[i][1][1][0]     # ATA
            sac      = deco_gas[i][1][2][0]     # SAC
            gas      = deco_gas[i][1][4][0]     # Gas Volume

            def callback(event=None):
                # mirror time
                dst_time.delete(0, "end")
                dst_time.insert(0, src_time.get())

                # GV = ATA * SAC * Time
                try:
                    ata_val  = float(ata.get())
                    sac_val  = float(sac.get())
                    time_val = float(dst_time.get())
                    value = ata_val * sac_val * time_val
                    gas.delete(0, "end")
                    gas.insert(0, f"{value:.2f}")
                except ValueError:
                    gas.delete(0, "end")

                recalc_deco_total()
            return callback

        # Bind all 6 stop rows
        for i in range(6):
            deco_stops[i][1][1][0].bind("<KeyRelease>", make_sync_and_calc(i))

        # --- Buttons ---
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=15)
        ctk.CTkButton(button_frame, text="Save", command=self.save_to_json).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Load", command=self.load_from_json).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Clear All", command=self.clear_all_entries).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Export to PDF", command=self.export_to_pdf).pack(side="left", padx=10)

    def add_entry_row(self, parent, labels):
        entries = []
        row = ctk.CTkFrame(parent)
        row.pack(pady=5, fill="x")
        for label in labels:
            frame = ctk.CTkFrame(row)
            frame.pack(side="left", padx=5, expand=True, fill="x")
            lbl = ctk.CTkLabel(frame, text=label)
            lbl.pack(anchor="w")
            entry = ctk.CTkEntry(frame)
            entry.pack(fill="x")
            entries.append((label, entry))
        return entries

    def add_table(self, parent, title, headers, rows=5, default_depths=None,
                  default_atas=None, default_sac=None, default_total=None):
        table_entries = []
        ctk.CTkLabel(parent, text=title, font=("Arial", 14, "bold")).pack(anchor="w", pady=(10, 5))
        table = ctk.CTkFrame(parent)
        table.pack()

        # Headers
        for h in headers:
            ctk.CTkLabel(table, text=h, width=100).grid(row=0, column=headers.index(h), padx=5, pady=2)

        # Rows
        for r in range(1, rows + 1):
            row_entries = []
            for c, h in enumerate(headers):
                entry = ctk.CTkEntry(table, width=100)
                entry.grid(row=r, column=c, padx=5, pady=2)

                default_val = ""
                if default_depths and c == 0 and r <= len(default_depths):
                    entry.insert(0, default_depths[r - 1])
                    default_val = default_depths[r - 1]
                if default_atas and c == 1 and r <= len(default_atas):
                    entry.insert(0, default_atas[r - 1])
                    default_val = default_atas[r - 1]
                if default_sac and c == 2 and r <= len(default_sac):
                    entry.insert(0, default_sac[r - 1])
                    default_val = default_sac[r - 1]
                if default_total and c == 3 and r <= len(default_total):
                    entry.insert(0, default_total[r - 1])
                    default_val = default_total[r - 1]

                row_entries.append((entry, default_val))
            table_entries.append((headers, row_entries))

        # Automatic calculations
        if title in ["Deco Gas Requirements", "Bottom Gas Requirements"]:
            gas_volume_entries = []
            total_entry = None

            if title == "Deco Gas Requirements":
                gas_volume_entries = [row[1][4][0] for row in table_entries[:6]]
                total_entry = table_entries[6][1][4][0]
                total_entry.configure(state="readonly")

            for i, row in enumerate(table_entries):
                depth_entry = row[1][0][0]
                ata_entry = row[1][1][0]
                sac_entry = row[1][2][0]
                time_entry = row[1][3][0]
                gv_entry = row[1][4][0]

                # Depth → ATA
                def make_ata_callback(depth, ata):
                    def callback(event=None):
                        try:
                            depth_val = float(depth.get())
                            ata_val = depth_val / 33 + 1
                            ata.delete(0, "end")
                            ata.insert(0, f"{ata_val:.2f}")
                        except ValueError:
                            ata.delete(0, "end")
                    return callback

                depth_entry.bind("<KeyRelease>", make_ata_callback(depth_entry, ata_entry))

                # ATA × SAC × Time → Gas Volume
                def make_gv_callback(ata, sac, time, gv):
                    def callback(event=None):
                        try:
                            value = float(ata.get()) * float(sac.get()) * float(time.get())
                            gv.delete(0, "end")
                            gv.insert(0, f"{value:.2f}")
                        except ValueError:
                            gv.delete(0, "end")
                        if total_entry and gv in gas_volume_entries:
                            update_total()
                    return callback

                ata_entry.bind("<KeyRelease>", make_gv_callback(ata_entry, sac_entry, time_entry, gv_entry))
                sac_entry.bind("<KeyRelease>", make_gv_callback(ata_entry, sac_entry, time_entry, gv_entry))
                time_entry.bind("<KeyRelease>", make_gv_callback(ata_entry, sac_entry, time_entry, gv_entry))

            # Function to update Deco Gas sum row
            if title == "Deco Gas Requirements":
                def update_total():
                    total = 0
                    for e in gas_volume_entries:
                        try:
                            total += float(e.get())
                        except ValueError:
                            pass
                    total_entry.configure(state="normal")
                    total_entry.delete(0, "end")
                    total_entry.insert(0, f"{total:.2f}")
                    total_entry.configure(state="readonly")

        # Auto midpoint calculation for Gas Reserve (Emergency)
        if title == "Gas Reserve (Emergency)" and len(table_entries) >= 3:
            row2_depth_entry = table_entries[1][1][0][0]  # row 2, column 0 = Depth
            row2_depth_entry.delete(0, "end")
            row2_depth_entry.insert(0, "(A)")
            row3_time_entry = table_entries[2][1][3][0]  # row 3, column index 3 = Time
            row3_time_entry.delete(0, "end")
            row3_time_entry.insert(0, "Total Per Diver")


            # --- Auto midpoint depth (Row 2) ---
            def update_row2_depth(event=None):
                try:
                    depth1 = float(table_entries[0][1][0][0].get())
                    depth3 = float(table_entries[2][1][0][0].get())
                    midpoint = (depth1 + depth3) / 2
                    row2_depth = table_entries[1][1][0][0]
                    row2_depth.delete(0, "end")
                    row2_depth.insert(0, f"{midpoint:.1f}")

                    # --- Update ATA for row 2 ---
                    ata_entry = table_entries[1][1][1][0]  # row 2, ATA column
                    ata_val = midpoint / 33 + 1
                    ata_entry.delete(0, "end")
                    ata_entry.insert(0, f"{ata_val:.2f}")

                    # --- Trigger Gas Volume recalculation for row 2 ---
                    sac_entry  = table_entries[1][1][2][0]
                    time_entry = table_entries[1][1][3][0]
                    gas_entry  = table_entries[1][1][4][0]
                    try:
                        gas_val = ata_val * float(sac_entry.get()) * float(time_entry.get())
                        gas_entry.delete(0, "end")
                        gas_entry.insert(0, f"{gas_val:.1f}")
                    except ValueError:
                        gas_entry.delete(0, "end")

                    # --- Update row 3 total ---
                    update_row3_total()

                except ValueError:
                    pass

            table_entries[0][1][0][0].bind("<KeyRelease>", update_row2_depth)
            table_entries[2][1][0][0].bind("<KeyRelease>", update_row2_depth)

            # --- Auto ATA from Depth for all rows ---
            for row in table_entries:
                depth_entry = row[1][0][0]
                ata_entry = row[1][1][0]

                def make_ata_callback(depth, ata):
                    def callback(event=None):
                        try:
                            depth_val = float(depth.get())
                            ata_val = depth_val / 33 + 1
                            ata.delete(0, "end")
                            ata.insert(0, f"{ata_val:.2f}")
                        except ValueError:
                            ata.delete(0, "end")
                    return callback

                depth_entry.bind("<KeyRelease>", make_ata_callback(depth_entry, ata_entry))

            # --- Row 3 = total of Row 1 + Row 2 ---
            def update_row3_total():
                try:
                    row1_val = float(table_entries[0][1][4][0].get())
                except ValueError:
                    row1_val = 0
                try:
                    row2_val = float(table_entries[1][1][4][0].get())
                except ValueError:
                    row2_val = 0

                total = row1_val + row2_val
                row3_gas = table_entries[2][1][4][0]
                row3_gas.configure(state="normal")
                row3_gas.delete(0, "end")
                row3_gas.insert(0, f"{total:.1f}")
                row3_gas.configure(state="readonly")

            # --- Update Gas Reserve for Two Divers ---
                two_divers_entry = self.sections['Gas Reserve / Rock Bottom'][1][1]  # your existing reference
                two_divers_entry.delete(0, "end")
                two_divers_entry.insert(0, f"{total*2:.1f}")

            # --- Auto Gas Volume for rows 1 & 2 ---
            def make_gas_calc_callback(row):
                ata_entry   = row[1][1][0]
                sac_entry   = row[1][2][0]
                time_entry  = row[1][3][0]
                gas_entry   = row[1][4][0]

                def callback(event=None):
                    try:
                        ata_val  = float(ata_entry.get())
                        sac_val  = float(sac_entry.get())
                        time_val = float(time_entry.get())
                        gas_val  = ata_val * sac_val * time_val
                        gas_entry.delete(0, "end")
                        gas_entry.insert(0, f"{gas_val:.1f}")
                    except ValueError:
                        gas_entry.delete(0, "end")
                    # always update row 3 after row 1 or 2 changes
                    update_row3_total()
                return callback

            # Attach callbacks for rows 1 & 2
            for row in table_entries[:2]:
                for entry in [row[1][1][0], row[1][2][0], row[1][3][0]]:
                    entry.bind("<KeyRelease>", make_gas_calc_callback(row))

        return table_entries

    def save_to_json(self):
        data = {}
        for section, widgets in self.sections.items():
            if all(isinstance(w, tuple) and isinstance(w[1], list) for w in widgets):
                data[section] = [[e.get() for e, default in row_entries] for headers, row_entries in widgets]
            else:
                data[section] = [e.get() for label, e in widgets]

        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)

    def load_from_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            with open(file_path, "r") as f:
                data = json.load(f)
            for section, widgets in self.sections.items():
                values = data.get(section)
                if values:
                    if all(isinstance(w, tuple) and isinstance(w[1], list) for w in widgets):
                        for (headers, row_entries), row_values in zip(widgets, values):
                            for (e, default), v in zip(row_entries, row_values):
                                e.delete(0, "end")
                                e.insert(0, v)
                    else:
                        for (label, e), v in zip(widgets, values):
                            e.delete(0, "end")
                            e.insert(0, v)

    def export_to_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                 filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return

        doc = SimpleDocTemplate(file_path, pagesize=letter,
                                leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
        elements = []
        styles = getSampleStyleSheet()
        spacer = Spacer(1, 6)

        for section, widgets in self.sections.items():
            elements.append(Paragraph(section, styles['Heading2']))
            data = []
            if all(isinstance(w, tuple) and isinstance(w[1], list) for w in widgets):
                headers, _ = widgets[0]
                data.append(headers)
                for headers, row_entries in widgets:
                    data.append([e.get() for e, default in row_entries])
            else:
                data.append(["", ""])
                for label, e in widgets:
                    data.append([label, e.get()])

            page_width = 8.5 * 72 - 40
            num_cols = len(data[0])
            col_width = page_width / num_cols

            table = Table(data, colWidths=[col_width]*num_cols, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
                ('FONTSIZE', (0,0), (-1,-1), 8),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ('TOPPADDING', (0,0), (-1,-1), 1)
            ]))
            elements.append(table)
            elements.append(spacer)

        doc.build(elements)

    def clear_all_entries(self):
        for section, widgets in self.sections.items():
            if all(isinstance(w, tuple) and isinstance(w[1], list) for w in widgets):
                for row_idx, (headers, row_entries) in enumerate(widgets):
                    for col_idx, (e, default) in enumerate(row_entries):
                        # Special handling for Gas Reserve (Emergency)
                        if section == "Gas Reserve (Emergency)":
                            if row_idx == 1 and col_idx == 0:  # Row 2 Depth
                                e.delete(0, "end")
                                e.insert(0, "(A)")
                                continue
                            if row_idx == 2 and col_idx == 3:  # Row 3 Time ("Total Per Diver")
                                continue
                            if row_idx == 2 and col_idx == 4:  # Row 3 Gas Volume
                                e.delete(0, "end")
                                continue
                        # Default clear for other entries
                        e.delete(0, "end")
                        e.insert(0, default)
            else:
                for label, e in widgets:
                    e.delete(0, "end")

if __name__ == "__main__":
    app = GasPlanningApp()
    app.mainloop()
