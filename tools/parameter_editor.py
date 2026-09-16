#!/usr/bin/env python3
"""Interactive V3.0 parameter editor with live Work/Party SVG preview."""

from __future__ import annotations

import argparse
import base64
import json
import math
import os
import subprocess
import sys
import threading


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from cad.generators import design_parameters as DesignParameters  # noqa: E402
from cad.generators import geometry_v30 as Geometry  # noqa: E402


def derived_values(values):
    values = DesignParameters.normalize_parameters(values)
    arm_sine = math.sin(math.radians(60.0))
    primary_outer_radius = (
        values["technical_channel_width"] / 2.0
        + values["primary_depth"]
        + values["user_edge_width"] / 4.0
    ) / arm_sine
    primary_inner_radius = primary_outer_radius - values["primary_depth"]
    primary_rear_width = 4.0 * (
        arm_sine * primary_inner_radius - values["technical_channel_width"] / 2.0
    )
    return {
        "Šířka S/T = hloubka P": values["primary_depth"],
        "Pracovní šířka ramene = kanál + 2× hloubka": (
            values["technical_channel_width"] + 2.0 * values["primary_depth"]
        ),
        "Vnitřní poloměr P (odvozený)": primary_inner_radius,
        "Vnější poloměr P (odvozený)": primary_outer_radius,
        "Zadní hrana P (odvozená)": primary_rear_width,
        "Poloměr uživatele": (
            primary_outer_radius + values["user_clearance"]
        ),
        "Rezerva liftu k hraně kanálu": (
            values["technical_channel_width"] / 2.0
            - values["side_lift_offset"]
            - values["monitor_lift_diameter"] / 2.0
        ),
        "Posun S/T monitoru lift → Work": math.hypot(
            values["side_lift_radius"] - values["side_monitor_radius"],
            values["side_monitor_offset"] - values["side_lift_offset"],
        ),
        "Délka party ramene": values["side_desk_length"],
        "Výška podpory Party": (
            values["party_surface_height"] - values["party_module_thickness"]
        ),
        "Výška uložené přepážky": (
            values["technical_channel_width"] + 2.0 * values["primary_depth"]
        ),
        "Horní hrana uložené přepážky": (
            values["party_partition_bottom_height"]
            + values["technical_channel_width"]
            + 2.0 * values["primary_depth"]
        ),
        "Mezera přepážka → uložený střed": (
            values["party_storage_vertical_clearance"]
        ),
        "Spodní hrana uloženého středu": (
            values["party_partition_bottom_height"]
            + values["technical_channel_width"]
            + 2.0 * values["primary_depth"]
            + values["party_storage_vertical_clearance"]
        ),
        "Zdvih osy ramenního modulu": (
            values["party_partition_bottom_height"]
            + (values["technical_channel_width"] + 2.0 * values["primary_depth"]) / 2.0
            - values["party_surface_height"]
            + values["party_module_thickness"] / 2.0
        ),
        "Zdvih centrálního modulu": (
            values["party_partition_bottom_height"]
            + values["technical_channel_width"]
            + 2.0 * values["primary_depth"]
            + values["party_storage_vertical_clearance"]
            - values["party_surface_height"]
            + values["party_module_thickness"]
        ),
    }


def geometry_status(values):
    errors = DesignParameters.validate_parameters(values)
    if errors:
        return errors
    Geometry.apply_parameters(values)
    checks = (
        ("Kolize pracovních desek", Geometry.collision_pairs()),
        ("Nerovnoběžné front/rear hrany", Geometry.nonparallel_desk_edges()),
        ("Chyby hran technologického kanálu", Geometry.technical_channel_edge_failures()),
        ("Kolize liftů s deskami", Geometry.monitor_lift_desk_collisions()),
        ("Kolize monitorů s deskami", Geometry.monitor_body_desk_collisions()),
        ("Kolize monitorů", Geometry.monitor_body_collisions()),
        ("Chyby party spár", Geometry.party_seam_failures()),
        ("Chyby pokrytí party vrstvy", Geometry.party_coverage_failures()),
    )
    return ["%s: %s" % (label, value) for label, value in checks if value]


def check_payload(values):
    errors = geometry_status(values)
    return {
        "config": DesignParameters.CONFIG_PATH,
        "status": "fail" if errors else "pass",
        "errors": errors,
        "parameters": DesignParameters.normalize_parameters(values),
        "derived": derived_values(values),
    }


class ParameterEditor:
    def __init__(self, root):
        import tkinter as tk
        from tkinter import ttk

        self.tk = tk
        self.ttk = ttk
        self.root = root
        self.root.title("MultiRoleWorkIsland — parametry V3.0")
        self.root.geometry("1420x920")
        self.root.minsize(1100, 720)
        self.variables = {}
        self.preview_image = None
        self.preview_job = None
        self.mode = tk.StringVar(value="work")
        self.status = tk.StringVar(value="Načítám…")
        self.build_running = False

        outer = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
        outer.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        preview_frame = ttk.Frame(outer)
        controls_frame = ttk.Frame(outer, width=480)
        outer.add(preview_frame, weight=3)
        outer.add(controls_frame, weight=2)

        preview_toolbar = ttk.Frame(preview_frame)
        preview_toolbar.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(preview_toolbar, text="Náhled:").pack(side=tk.LEFT)
        ttk.Radiobutton(
            preview_toolbar, text="Work", variable=self.mode, value="work",
            command=self.schedule_preview,
        ).pack(side=tk.LEFT, padx=(8, 2))
        ttk.Radiobutton(
            preview_toolbar, text="Party", variable=self.mode, value="party",
            command=self.schedule_preview,
        ).pack(side=tk.LEFT, padx=2)
        ttk.Label(
            preview_toolbar, text=DesignParameters.CONFIG_PATH,
            foreground="#5b6470",
        ).pack(side=tk.RIGHT)

        self.preview = ttk.Label(preview_frame, anchor=tk.CENTER)
        self.preview.pack(fill=tk.BOTH, expand=True)
        ttk.Label(
            preview_frame, textvariable=self.status, anchor=tk.W,
            wraplength=850,
        ).pack(fill=tk.X, pady=(6, 0))

        buttons = ttk.Frame(controls_frame)
        buttons.pack(fill=tk.X, pady=(0, 6))
        ttk.Button(buttons, text="Uložit", command=self.save).pack(side=tk.LEFT)
        ttk.Button(buttons, text="Načíst znovu", command=self.reload).pack(side=tk.LEFT, padx=6)
        ttk.Button(buttons, text="Uložit + vytvořit CAD", command=self.save_and_build).pack(side=tk.LEFT)

        notebook = ttk.Notebook(controls_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        parameter_tab = ttk.Frame(notebook)
        dependency_tab = ttk.Frame(notebook)
        notebook.add(parameter_tab, text="Vstupní parametry")
        notebook.add(dependency_tab, text="Vazby a kontroly")

        canvas = tk.Canvas(parameter_tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parameter_tab, orient=tk.VERTICAL, command=canvas.yview)
        self.parameter_form = ttk.Frame(canvas)
        self.parameter_form.bind(
            "<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.parameter_form, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        for row, spec in enumerate(DesignParameters.PARAMETER_SPECS):
            key, label, _default, minimum, maximum, unit, help_text = spec
            ttk.Label(self.parameter_form, text=label).grid(row=row * 2, column=0, sticky="w", padx=6, pady=(5, 0))
            variable = tk.StringVar()
            variable.trace_add("write", lambda *_args: self.schedule_preview())
            self.variables[key] = variable
            entry = ttk.Entry(self.parameter_form, textvariable=variable, width=14)
            entry.grid(row=row * 2, column=1, sticky="ew", padx=6, pady=(5, 0))
            ttk.Label(self.parameter_form, text=unit).grid(row=row * 2, column=2, sticky="w", pady=(5, 0))
            ttk.Label(
                self.parameter_form,
                text="%s  (%.0f–%.0f %s)" % (help_text, minimum, maximum, unit),
                foreground="#5b6470",
                wraplength=420,
            ).grid(row=row * 2 + 1, column=0, columnspan=3, sticky="w", padx=6, pady=(0, 3))
        self.parameter_form.columnconfigure(0, weight=1)

        self.dependency_text = tk.Text(
            dependency_tab, wrap="word", state="disabled", padx=10, pady=10,
            font=("TkFixedFont", 10),
        )
        self.dependency_text.pack(fill=tk.BOTH, expand=True)
        self.reload()

    def collect_values(self):
        values = {}
        parse_errors = []
        for key, variable in self.variables.items():
            raw = variable.get().strip().replace(",", ".")
            try:
                values[key] = float(raw)
            except ValueError:
                parse_errors.append("%s není číslo" % DesignParameters.SPEC_BY_KEY[key][1])
        return values, parse_errors

    def schedule_preview(self):
        if self.preview_job is not None:
            self.root.after_cancel(self.preview_job)
        self.preview_job = self.root.after(180, self.update_preview)

    def update_preview(self):
        import cairosvg

        self.preview_job = None
        values, errors = self.collect_values()
        if not errors:
            errors = geometry_status(values)
        if errors:
            self.status.set("Nelze použít: " + " | ".join(errors))
            self.update_dependencies(values, errors)
            return
        svg = Geometry.svg_party_plan() if self.mode.get() == "party" else Geometry.svg_plan()
        png = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=820, output_height=820)
        encoded = base64.b64encode(png).decode("ascii")
        self.preview_image = self.tk.PhotoImage(data=encoded)
        self.preview.configure(image=self.preview_image)
        self.status.set("Geometrie je platná. Změny zatím nejsou uložené.")
        self.update_dependencies(values, [])

    def update_dependencies(self, values, errors):
        lines = ["ODVOZENÉ VAZBY", ""]
        if not errors:
            for label, value in derived_values(values).items():
                lines.append("%-48s %8.2f mm" % (label, value))
        else:
            lines.extend("CHYBA: " + error for error in errors)
        lines.extend(("", "KONTROLY", ""))
        if errors:
            lines.append("Náhled a uložení jsou blokované.")
        else:
            lines.extend((
                "✓ P/S/T front–rear hloubka je společný parametr",
                "✓ technologický kanál je odvozen mezi hranami S/T",
                "✓ lift se musí vejít do poloviny kanálu",
                "✓ party podpora = výška Party − tloušťka modulu",
                "✓ kontrola kolizí, rovnoběžnosti, spár a pokrytí prošla",
            ))
        self.dependency_text.configure(state="normal")
        self.dependency_text.delete("1.0", "end")
        self.dependency_text.insert("1.0", "\n".join(lines))
        self.dependency_text.configure(state="disabled")

    def reload(self):
        try:
            values = DesignParameters.load_parameters()
        except Exception as error:
            self.status.set("Chyba načtení: %s" % error)
            return
        for key, value in values.items():
            self.variables[key].set(format(value, ".6g"))
        self.schedule_preview()

    def save(self):
        values, errors = self.collect_values()
        if not errors:
            errors = geometry_status(values)
        if errors:
            self.status.set("Uložení odmítnuto: " + " | ".join(errors))
            return False
        try:
            DesignParameters.save_parameters(values)
        except Exception as error:
            self.status.set("Chyba uložení: %s" % error)
            return False
        self.status.set("Uloženo do %s" % DesignParameters.CONFIG_PATH)
        return True

    def save_and_build(self):
        if self.build_running or not self.save():
            return
        self.build_running = True
        self.status.set("FreeCAD build běží…")

        def worker():
            process = subprocess.run(
                [os.path.join(PROJECT_ROOT, "run.sh")],
                cwd=PROJECT_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            tail = "\n".join(process.stdout.splitlines()[-4:])
            self.root.after(0, lambda: self.build_finished(process.returncode, tail))

        threading.Thread(target=worker, daemon=True).start()

    def build_finished(self, returncode, tail):
        self.build_running = False
        if returncode == 0:
            self.status.set("FreeCAD build dokončen. " + tail.replace("\n", " | "))
        else:
            self.status.set("FreeCAD build selhal. " + tail.replace("\n", " | "))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate the text configuration without opening a window.")
    args = parser.parse_args(argv)
    values = DesignParameters.load_parameters()
    if args.check:
        payload = check_payload(values)
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if payload["status"] == "pass" else 1

    import tkinter as tk

    root = tk.Tk()
    ParameterEditor(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
