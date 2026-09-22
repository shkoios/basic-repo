#!/usr/bin/env python3

"""
Basic Repo
A lightweight graphical package and repository manager for Fedora.

License: MIT
"""

import os
import re
import shutil
import subprocess
import tempfile
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


# ============================================================
# APPLICATION
# ============================================================

APP_NAME = "Basic Repo"
VERSION = "2.1.0"

REPO_DIR = "/etc/yum.repos.d"

# Automatic repository checking
AUTO_REPO_CHECK = True

# First automatic check: 30 seconds after launch
AUTO_CHECK_START_DELAY = 30 * 1000

# Repeat every 30 minutes
AUTO_CHECK_INTERVAL = 30 * 60 * 1000


# ============================================================
# COLORS
# ============================================================

COLORS = {
    "background": "#0F1115",
    "surface": "#171A20",
    "surface_alt": "#20242C",
    "surface_hover": "#292E38",
    "border": "#303640",

    "text": "#F4F6F8",
    "text_secondary": "#A4ABB6",
    "text_muted": "#737B88",

    "accent": "#4C8DFF",
    "accent_hover": "#6BA1FF",

    "success": "#45C486",
    "warning": "#F0B35A",
    "danger": "#EF6262",

    "input": "#13161B",
}


# ============================================================
# BASIC REPO
# ============================================================

class BasicRepo:

    def __init__(self, root):

        self.root = root

        self.root.title(f"{APP_NAME} {VERSION}")
        self.root.geometry("1280x780")
        self.root.minsize(1000, 620)

        self.root.configure(
            bg=COLORS["background"]
        )

        # Package state
        self.packages = []
        self.current_package = None

        # Repository state
        self.repositories = []
        self.current_repo = None

        # packages / repositories
        self.mode = "packages"

        # Prevent two automatic checks at once
        self.auto_check_running = False

        self.setup_theme()
        self.build_ui()

        self.show_installed()

        # Automatic repository check
        if AUTO_REPO_CHECK:
            self.root.after(
                AUTO_CHECK_START_DELAY,
                self.start_automatic_repo_check
            )

    # ========================================================
    # THEME
    # ========================================================

    def setup_theme(self):

        self.style = ttk.Style()

        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.style.configure(
            ".",
            background=COLORS["background"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["surface"],
            bordercolor=COLORS["border"]
        )

        self.style.configure(
            "TFrame",
            background=COLORS["background"]
        )

        self.style.configure(
            "Surface.TFrame",
            background=COLORS["surface"]
        )

        self.style.configure(
            "TLabel",
            background=COLORS["background"],
            foreground=COLORS["text"]
        )

        self.style.configure(
            "Surface.TLabel",
            background=COLORS["surface"],
            foreground=COLORS["text"]
        )

        self.style.configure(
            "Muted.TLabel",
            background=COLORS["background"],
            foreground=COLORS["text_secondary"]
        )

        self.style.configure(
            "SurfaceMuted.TLabel",
            background=COLORS["surface"],
            foreground=COLORS["text_secondary"]
        )

        self.style.configure(
            "Title.TLabel",
            font=("Sans", 22, "bold"),
            foreground=COLORS["text"]
        )

        self.style.configure(
            "Page.TLabel",
            font=("Sans", 17, "bold"),
            foreground=COLORS["text"]
        )

        self.style.configure(
            "Package.TLabel",
            font=("Sans", 18, "bold"),
            background=COLORS["surface"],
            foreground=COLORS["text"]
        )

        self.style.configure(
            "TButton",
            padding=(12, 8),
            background=COLORS["surface_alt"],
            foreground=COLORS["text"],
            borderwidth=0
        )

        self.style.map(
            "TButton",
            background=[
                ("active", COLORS["surface_hover"])
            ]
        )

        self.style.configure(
            "Accent.TButton",
            background=COLORS["accent"],
            foreground="#FFFFFF",
            borderwidth=0
        )

        self.style.map(
            "Accent.TButton",
            background=[
                ("active", COLORS["accent_hover"])
            ]
        )

        self.style.configure(
            "Success.TButton",
            background=COLORS["success"],
            foreground="#FFFFFF",
            borderwidth=0
        )

        self.style.configure(
            "Danger.TButton",
            background=COLORS["danger"],
            foreground="#FFFFFF",
            borderwidth=0
        )

        self.style.configure(
            "TEntry",
            padding=9,
            fieldbackground=COLORS["input"],
            foreground=COLORS["text"],
            insertcolor=COLORS["text"]
        )

        self.style.configure(
            "Treeview",
            background=COLORS["surface"],
            fieldbackground=COLORS["surface"],
            foreground=COLORS["text"],
            rowheight=33,
            borderwidth=0
        )

        self.style.map(
            "Treeview",
            background=[
                ("selected", COLORS["accent"])
            ],
            foreground=[
                ("selected", "#FFFFFF")
            ]
        )

        self.style.configure(
            "Treeview.Heading",
            background=COLORS["surface_alt"],
            foreground=COLORS["text"],
            padding=9,
            borderwidth=0
        )

        self.style.map(
            "Treeview.Heading",
            background=[
                ("active", COLORS["surface_hover"])
            ]
        )

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = ttk.Frame(
            self.root,
            padding=(18, 14)
        )

        header.pack(fill="x")

        ttk.Label(
            header,
            text="Basic Repo",
            style="Title.TLabel"
        ).pack(side="left")

        ttk.Label(
            header,
            text=f"v{VERSION}",
            style="Muted.TLabel"
        ).pack(
            side="left",
            padx=(10, 20)
        )

        self.search_var = tk.StringVar()

        self.search_entry = ttk.Entry(
            header,
            textvariable=self.search_var
        )

        self.search_entry.pack(
            side="right",
            fill="x",
            expand=True,
            padx=(80, 0)
        )

        self.search_entry.bind(
            "<Return>",
            lambda event: self.search_packages()
        )

        # ----------------------------------------------------
        # BODY
        # ----------------------------------------------------

        body = ttk.Frame(self.root)

        body.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # SIDEBAR
        # ----------------------------------------------------

        sidebar = ttk.Frame(
            body,
            padding=12,
            style="Surface.TFrame"
        )

        sidebar.pack(
            side="left",
            fill="y"
        )

        ttk.Label(
            sidebar,
            text="PACKAGES",
            style="SurfaceMuted.TLabel"
        ).pack(
            anchor="w",
            pady=(5, 8)
        )

        self.sidebar_button(
            sidebar,
            "Installed",
            self.show_installed
        )

        self.sidebar_button(
            sidebar,
            "Available",
            self.show_available
        )

        self.sidebar_button(
            sidebar,
            "Updates",
            self.show_updates
        )

        ttk.Separator(
            sidebar
        ).pack(
            fill="x",
            pady=16
        )

        ttk.Label(
            sidebar,
            text="SOURCES",
            style="SurfaceMuted.TLabel"
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        self.sidebar_button(
            sidebar,
            "Repositories",
            self.show_repositories
        )

        ttk.Separator(
            sidebar
        ).pack(
            fill="x",
            pady=16
        )

        ttk.Label(
            sidebar,
            text="SYSTEM",
            style="SurfaceMuted.TLabel"
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        self.sidebar_button(
            sidebar,
            "Install RPM",
            self.install_local_rpm
        )

        self.sidebar_button(
            sidebar,
            "Refresh Metadata",
            self.refresh_metadata
        )

        self.sidebar_button(
            sidebar,
            "Update All",
            self.update_all
        )

        # ----------------------------------------------------
        # MAIN CONTENT
        # ----------------------------------------------------

        self.content = ttk.Frame(
            body,
            padding=15
        )

        self.content.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.page_title = ttk.Label(
            self.content,
            text="Packages",
            style="Page.TLabel"
        )

        self.page_title.pack(
            anchor="w",
            pady=(0, 12)
        )

        self.paned = ttk.Panedwindow(
            self.content,
            orient="horizontal"
        )

        self.paned.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # LIST
        # ----------------------------------------------------

        list_frame = ttk.Frame(
            self.paned
        )

        self.tree = ttk.Treeview(
            list_frame,
            columns=(
                "name",
                "version",
                "arch",
                "source"
            ),
            show="headings",
            selectmode="browse"
        )

        self.tree.heading(
            "name",
            text="Name"
        )

        self.tree.heading(
            "version",
            text="Version"
        )

        self.tree.heading(
            "arch",
            text="Architecture"
        )

        self.tree.heading(
            "source",
            text="Source / Status"
        )

        self.tree.column(
            "name",
            width=280
        )

        self.tree.column(
            "version",
            width=180
        )

        self.tree.column(
            "arch",
            width=110
        )

        self.tree.column(
            "source",
            width=180
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.item_selected
        )

        self.paned.add(
            list_frame,
            weight=3
        )

        # ----------------------------------------------------
        # DETAILS
        # ----------------------------------------------------

        detail_frame = ttk.Frame(
            self.paned,
            padding=15,
            style="Surface.TFrame"
        )

        self.detail_title = ttk.Label(
            detail_frame,
            text="Select an item",
            style="Package.TLabel"
        )

        self.detail_title.pack(
            anchor="w"
        )

        self.detail_status = ttk.Label(
            detail_frame,
            text="",
            style="SurfaceMuted.TLabel"
        )

        self.detail_status.pack(
            anchor="w",
            pady=(5, 12)
        )

        self.details = tk.Text(
            detail_frame,
            wrap="word",
            bg=COLORS["surface"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief="flat",
            highlightthickness=0,
            padx=5,
            pady=5
        )

        self.details.pack(
            fill="both",
            expand=True
        )

        self.actions = ttk.Frame(
            detail_frame,
            style="Surface.TFrame"
        )

        self.actions.pack(
            fill="x",
            pady=(12, 0)
        )

        self.paned.add(
            detail_frame,
            weight=2
        )

        # ----------------------------------------------------
        # STATUS BAR
        # ----------------------------------------------------

        status_frame = ttk.Frame(
            self.root,
            padding=(15, 8),
            style="Surface.TFrame"
        )

        status_frame.pack(
            fill="x"
        )

        self.status_var = tk.StringVar(
            value="Ready"
        )

        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            style="SurfaceMuted.TLabel"
        ).pack(
            side="left"
        )

    # ========================================================
    # SIDEBAR BUTTON
    # ========================================================

    def sidebar_button(
        self,
        parent,
        text,
        command
    ):

        button = ttk.Button(
            parent,
            text=text,
            command=command,
            width=19
        )

        button.pack(
            fill="x",
            pady=2
        )

        return button

    # ========================================================
    # COMMAND EXECUTION
    # ========================================================

    def command(
        self,
        args,
        timeout=None
    ):

        try:

            result = subprocess.run(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                check=False
            )

            return (
                result.returncode,
                result.stdout,
                result.stderr
            )

        except subprocess.TimeoutExpired:

            return (
                124,
                "",
                "Command timed out."
            )

        except Exception as error:

            return (
                1,
                "",
                str(error)
            )

    def background(
        self,
        function
    ):

        thread = threading.Thread(
            target=function,
            daemon=True
        )

        thread.start()

    # ========================================================
    # CLEAR ACTION BUTTONS
    # ========================================================

    def clear_actions(self):

        for widget in self.actions.winfo_children():
            widget.destroy()

    # ========================================================
    # RESET DETAILS
    # ========================================================

    def reset_details(
        self,
        title="Select an item"
    ):

        self.detail_title.config(
            text=title
        )

        self.detail_status.config(
            text=""
        )

        self.details.delete(
            "1.0",
            "end"
        )

        self.clear_actions()

    # ========================================================
    # PACKAGE PARSER
    # ========================================================

    def parse_dnf_list(
        self,
        output
    ):

        packages = []

        ignored = (
            "Installed Packages",
            "Available Packages",
            "Last metadata",
            "Repositories loaded",
            "Updating and loading",
            "Updating Subscription",
            "Obsoleting Packages"
        )

        for line in output.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.startswith(ignored):
                continue

            parts = line.split()

            if len(parts) < 2:
                continue

            name_arch = parts[0]

            if "." not in name_arch:
                continue

            try:
                name, arch = name_arch.rsplit(
                    ".",
                    1
                )
            except ValueError:
                continue

            version = parts[1]

            source = ""

            if len(parts) >= 3:
                source = parts[2]

            packages.append({
                "name": name,
                "version": version,
                "arch": arch,
                "source": source
            })

        return packages

    # ========================================================
    # POPULATE PACKAGE LIST
    # ========================================================

    def populate_packages(
        self,
        packages
    ):

        self.mode = "packages"
        self.packages = packages
        self.current_package = None

        self.tree.delete(
            *self.tree.get_children()
        )

        for index, package in enumerate(
            packages
        ):

            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    package["name"],
                    package["version"],
                    package["arch"],
                    package["source"]
                )
            )

        self.status_var.set(
            f"{len(packages)} package(s)"
        )

        self.reset_details()

    # ========================================================
    # INSTALLED PACKAGES
    # ========================================================

    def show_installed(self):

        self.page_title.config(
            text="Installed Packages"
        )

        self.status_var.set(
            "Loading installed packages..."
        )

        def worker():

            code, out, error = self.command([
                "rpm",
                "-qa",
                "--qf",
                "%{NAME}|%{VERSION}-%{RELEASE}|%{ARCH}\n"
            ])

            packages = []

            if code == 0:

                for line in out.splitlines():

                    parts = line.split("|")

                    if len(parts) != 3:
                        continue

                    packages.append({
                        "name": parts[0],
                        "version": parts[1],
                        "arch": parts[2],
                        "source": "Installed"
                    })

                packages.sort(
                    key=lambda item:
                    item["name"].lower()
                )

            self.root.after(
                0,
                lambda:
                self.populate_packages(
                    packages
                )
            )

        self.background(worker)

    # ========================================================
    # AVAILABLE PACKAGES
    # ========================================================

    def show_available(self):

        self.page_title.config(
            text="Available Packages"
        )

        self.status_var.set(
            "Loading available packages..."
        )

        def worker():

            code, out, error = self.command([
                "dnf",
                "list",
                "available"
            ])

            packages = self.parse_dnf_list(
                out
            )

            self.root.after(
                0,
                lambda:
                self.populate_packages(
                    packages
                )
            )

        self.background(worker)

    # ========================================================
    # SEARCH PACKAGES
    # ========================================================

    def search_packages(self):

        query = (
            self.search_var
            .get()
            .strip()
        )

        if not query:
            return

        self.page_title.config(
            text=f"Search — {query}"
        )

        self.status_var.set(
            f"Searching for {query}..."
        )

        def worker():

            code, out, error = self.command([
                "dnf",
                "list",
                f"*{query}*"
            ])

            packages = self.parse_dnf_list(
                out
            )

            self.root.after(
                0,
                lambda:
                self.populate_packages(
                    packages
                )
            )

        self.background(worker)

    # ========================================================
    # UPDATES
    # ========================================================

    def show_updates(self):

        self.page_title.config(
            text="Available Updates"
        )

        self.status_var.set(
            "Checking for updates..."
        )

        def worker():

            code, out, error = self.command([
                "dnf",
                "list",
                "updates"
            ])

            packages = self.parse_dnf_list(
                out
            )

            self.root.after(
                0,
                lambda:
                self.populate_packages(
                    packages
                )
            )

        self.background(worker)

    # ========================================================
    # TREE SELECTION
    # ========================================================

    def item_selected(
        self,
        event=None
    ):

        if self.mode == "repositories":
            self.repository_selected()
        else:
            self.package_selected()

    # ========================================================
    # PACKAGE DETAILS
    # ========================================================

    def package_selected(self):

        selection = self.tree.selection()

        if not selection:
            return

        try:

            package = self.packages[
                int(selection[0])
            ]

        except (
            IndexError,
            ValueError
        ):
            return

        self.current_package = package

        name = package["name"]

        self.detail_title.config(
            text=name
        )

        self.detail_status.config(
            text="Loading package information..."
        )

        self.details.delete(
            "1.0",
            "end"
        )

        self.clear_actions()

        def worker():

            code, out, error = self.command([
                "dnf",
                "info",
                name
            ])

            installed_code, _, _ = self.command([
                "rpm",
                "-q",
                name
            ])

            installed = (
                installed_code == 0
            )

            def update():

                self.details.delete(
                    "1.0",
                    "end"
                )

                self.details.insert(
                    "1.0",
                    out or error or
                    "No package information available."
                )

                self.clear_actions()

                if installed:

                    self.detail_status.config(
                        text="Installed"
                    )

                    ttk.Button(
                        self.actions,
                        text="Remove",
                        style="Danger.TButton",
                        command=self.remove_selected
                    ).pack(
                        side="left"
                    )

                    ttk.Button(
                        self.actions,
                        text="Update",
                        style="Accent.TButton",
                        command=self.update_selected
                    ).pack(
                        side="left",
                        padx=6
                    )

                else:

                    self.detail_status.config(
                        text="Available"
                    )

                    ttk.Button(
                        self.actions,
                        text="Install",
                        style="Success.TButton",
                        command=self.install_selected
                    ).pack(
                        side="left"
                    )

            self.root.after(
                0,
                update
            )

        self.background(worker)

    # ========================================================
    # PRIVILEGED DNF
    # ========================================================

    def privileged_dnf(
        self,
        arguments,
        success_message="Operation completed."
    ):

        if not shutil.which("pkexec"):

            messagebox.showerror(
                APP_NAME,
                "PolicyKit's pkexec command was not found."
            )

            return

        command = [
            "pkexec",
            "dnf"
        ] + arguments

        self.status_var.set(
            "Waiting for authentication..."
        )

        def worker():

            code, out, error = self.command(
                command
            )

            def finished():

                if code == 0:

                    messagebox.showinfo(
                        APP_NAME,
                        success_message
                    )

                    self.status_var.set(
                        "Operation completed."
                    )

                else:

                    messagebox.showerror(
                        APP_NAME,
                        error or out or
                        "The operation failed."
                    )

                    self.status_var.set(
                        "Operation failed."
                    )

            self.root.after(
                0,
                finished
            )

        self.background(worker)

    # ========================================================
    # INSTALL PACKAGE
    # ========================================================

    def install_selected(self):

        if not self.current_package:
            return

        name = self.current_package[
            "name"
        ]

        if not messagebox.askyesno(
            "Install Package",
            f"Install {name}?"
        ):
            return

        self.privileged_dnf(
            [
                "install",
                "-y",
                name
            ],
            f"{name} was installed successfully."
        )

    # ========================================================
    # REMOVE PACKAGE
    # ========================================================

    def remove_selected(self):

        if not self.current_package:
            return

        name = self.current_package[
            "name"
        ]

        if not messagebox.askyesno(
            "Remove Package",
            f"Remove {name}?\n\n"
            "DNF will calculate dependency changes before removal."
        ):
            return

        self.privileged_dnf(
            [
                "remove",
                "-y",
                name
            ],
            f"{name} was removed."
        )

    # ========================================================
    # UPDATE PACKAGE
    # ========================================================

    def update_selected(self):

        if not self.current_package:
            return

        name = self.current_package[
            "name"
        ]

        self.privileged_dnf(
            [
                "upgrade",
                "-y",
                name
            ],
            f"{name} was updated."
        )

    # ========================================================
    # INSTALL LOCAL RPM
    # ========================================================

    def install_local_rpm(self):

        path = filedialog.askopenfilename(
            title="Select RPM Package",
            filetypes=[
                (
                    "RPM Packages",
                    "*.rpm"
                ),
                (
                    "All Files",
                    "*"
                )
            ]
        )

        if not path:
            return

        filename = os.path.basename(
            path
        )

        if not messagebox.askyesno(
            "Install RPM",
            f"Install this RPM?\n\n{filename}"
        ):
            return

        self.privileged_dnf(
            [
                "install",
                "-y",
                os.path.abspath(path)
            ],
            f"{filename} was installed."
        )

    # ========================================================
    # REFRESH METADATA
    # ========================================================

    def refresh_metadata(self):

        self.privileged_dnf(
            [
                "makecache",
                "--refresh"
            ],
            "Repository metadata refreshed."
        )

    # ========================================================
    # UPDATE SYSTEM
    # ========================================================

    def update_all(self):

        if not messagebox.askyesno(
            "Update System",
            "Install all available system updates?"
        ):
            return

        self.privileged_dnf(
            [
                "upgrade",
                "-y"
            ],
            "System update completed."
        )

    # ========================================================
    # REPOSITORIES
    # ========================================================

    def show_repositories(self):

        self.mode = "repositories"

        self.page_title.config(
            text="Repositories"
        )

        self.status_var.set(
            "Reading repository configuration..."
        )

        self.current_repo = None

        self.tree.delete(
            *self.tree.get_children()
        )

        self.repositories = (
            self.read_repository_files()
        )

        for index, repo in enumerate(
            self.repositories
        ):

            status = (
                "Enabled"
                if repo["enabled"]
                else "Disabled"
            )

            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    repo["id"],
                    "",
                    "",
                    status
                )
            )

        self.status_var.set(
            f"{len(self.repositories)} repositories"
        )

        self.detail_title.config(
            text="Repository Sources"
        )

        self.detail_status.config(
            text="Select a repository to view its configuration."
        )

        self.details.delete(
            "1.0",
            "end"
        )

        self.details.insert(
            "1.0",
            "Basic Repo reads repository definitions from:\n\n"
            f"{REPO_DIR}\n\n"
            "Use Check All to test every enabled repository."
        )

        self.clear_actions()

        ttk.Button(
            self.actions,
            text="Add .repo File",
            style="Accent.TButton",
            command=self.add_repo_file
        ).pack(
            side="left"
        )

        ttk.Button(
            self.actions,
            text="Check All",
            command=self.check_all_repositories
        ).pack(
            side="left",
            padx=6
        )

    # ========================================================
    # READ REPOSITORY FILES
    # ========================================================

    def read_repository_files(self):

        repositories = []

        if not os.path.isdir(
            REPO_DIR
        ):
            return repositories

        try:
            filenames = sorted(
                os.listdir(REPO_DIR)
            )
        except OSError:
            return repositories

        for filename in filenames:

            if not filename.endswith(
                ".repo"
            ):
                continue

            path = os.path.join(
                REPO_DIR,
                filename
            )

            try:

                with open(
                    path,
                    "r",
                    encoding="utf-8",
                    errors="replace"
                ) as file:

                    lines = file.readlines()

            except OSError:
                continue

            current = None

            for line in lines:

                stripped = line.strip()

                section = re.match(
                    r"^\[([^\]]+)\]$",
                    stripped
                )

                if section:

                    if current:
                        repositories.append(
                            current
                        )

                    current = {
                        "id": section.group(1),
                        "file": path,
                        "enabled": True,
                        "name": "",
                        "baseurl": "",
                        "metalink": "",
                        "mirrorlist": ""
                    }

                    continue

                if current is None:
                    continue

                if not stripped:
                    continue

                if stripped.startswith(
                    ("#", ";")
                ):
                    continue

                if "=" not in stripped:
                    continue

                key, value = stripped.split(
                    "=",
                    1
                )

                key = key.strip().lower()
                value = value.strip()

                if key == "enabled":

                    current["enabled"] = (
                        value.lower()
                        not in (
                            "0",
                            "false",
                            "no"
                        )
                    )

                elif key in (
                    "name",
                    "baseurl",
                    "metalink",
                    "mirrorlist"
                ):

                    current[key] = value

            if current:
                repositories.append(
                    current
                )

        return repositories

    # ========================================================
    # REPOSITORY SELECTED
    # ========================================================

    def repository_selected(self):

        selection = self.tree.selection()

        if not selection:
            return

        try:

            repo = self.repositories[
                int(selection[0])
            ]

        except (
            IndexError,
            ValueError
        ):
            return

        self.current_repo = repo

        self.detail_title.config(
            text=repo["id"]
        )

        status = (
            "Enabled"
            if repo["enabled"]
            else "Disabled"
        )

        self.detail_status.config(
            text=status
        )

        info = (
            "Repository ID\n"
            f"{repo['id']}\n\n"

            "Name\n"
            f"{repo['name'] or 'Not specified'}\n\n"

            "Status\n"
            f"{status}\n\n"

            "Configuration file\n"
            f"{repo['file']}\n\n"
        )

        if repo["baseurl"]:

            info += (
                "Base URL\n"
                f"{repo['baseurl']}\n\n"
            )

        if repo["metalink"]:

            info += (
                "Metalink\n"
                f"{repo['metalink']}\n\n"
            )

        if repo["mirrorlist"]:

            info += (
                "Mirror List\n"
                f"{repo['mirrorlist']}\n\n"
            )

        self.details.delete(
            "1.0",
            "end"
        )

        self.details.insert(
            "1.0",
            info
        )

        self.clear_actions()

        ttk.Button(
            self.actions,
            text="Check Health",
            style="Accent.TButton",
            command=self.check_selected_repo
        ).pack(
            side="left"
        )

        if repo["enabled"]:

            ttk.Button(
                self.actions,
                text="Disable",
                command=self.disable_selected_repo
            ).pack(
                side="left",
                padx=6
            )

        else:

            ttk.Button(
                self.actions,
                text="Enable",
                style="Success.TButton",
                command=self.enable_selected_repo
            ).pack(
                side="left",
                padx=6
            )

        ttk.Button(
            self.actions,
            text="Delete",
            style="Danger.TButton",
            command=self.delete_selected_repo
        ).pack(
            side="left"
        )

    # ========================================================
    # REPOSITORY HEALTH CHECK
    # ========================================================

    def check_repo_health(
        self,
        repo
    ):

        """
        Test one repository through DNF.

        IMPORTANT:
        We inspect DNF's output BEFORE trusting the exit code.

        DNF/DNF5 can report a repository-specific failure such
        as HTTP 403 while the surrounding operation does not
        behave the way a simple return-code check expects.
        """

        repo_id = repo["id"]

        command = [
            "dnf",
            "--disablerepo=*",
            f"--enablerepo={repo_id}",
            "makecache",
            "--refresh"
        ]

        code, out, error = self.command(
            command,
            timeout=45
        )

        output = (
            (out or "")
            + "\n"
            + (error or "")
        ).strip()

        lower = output.lower()

        # ----------------------------------------------------
        # HTTP 404
        # ----------------------------------------------------

        if (
            "status code: 404" in lower
            or "http 404" in lower
            or "404 not found" in lower
        ):

            return (
                "404",
                "Repository returned HTTP 404 Not Found. "
                "The configured repository path may no longer exist."
            )

        # ----------------------------------------------------
        # HTTP 403
        # ----------------------------------------------------

        if (
            "status code: 403" in lower
            or "http 403" in lower
            or "403 forbidden" in lower
        ):

            return (
                "403",
                "Repository returned HTTP 403 Forbidden. "
                "The server refused access to its repository metadata."
            )

        # ----------------------------------------------------
        # HTTP 401
        # ----------------------------------------------------

        if (
            "status code: 401" in lower
            or "http 401" in lower
            or "401 unauthorized" in lower
        ):

            return (
                "401",
                "Repository returned HTTP 401 Unauthorized."
            )

        # ----------------------------------------------------
        # HTTP 410
        # ----------------------------------------------------

        if (
            "status code: 410" in lower
            or "http 410" in lower
            or "410 gone" in lower
        ):

            return (
                "410",
                "Repository returned HTTP 410 Gone. "
                "The repository may have been permanently removed."
            )

        # ----------------------------------------------------
        # HTTP 500+
        # ----------------------------------------------------

        server_error = re.search(
            r"status code:\s*(5\d\d)",
            lower
        )

        if server_error:

            code_text = server_error.group(1)

            return (
                code_text,
                f"Repository server returned HTTP {code_text}. "
                "This may be a temporary server-side problem."
            )

        # ----------------------------------------------------
        # USABLE URL NOT FOUND
        # ----------------------------------------------------

        if "usable url not found" in lower:

            return (
                "unusable",
                "DNF could not find a usable URL for this repository."
            )

        # ----------------------------------------------------
        # METADATA FAILURE
        # ----------------------------------------------------

        if (
            "failed to download metadata" in lower
            or
            "failed to download repository metadata" in lower
        ):

            return (
                "metadata",
                "DNF could not download repository metadata."
            )

        if (
            "repomd.xml" in lower
            and (
                "failed" in lower
                or "error" in lower
            )
        ):

            return (
                "metadata",
                "The repository metadata file repomd.xml "
                "could not be downloaded."
            )

        # ----------------------------------------------------
        # DNS FAILURE
        # ----------------------------------------------------

        if (
            "could not resolve" in lower
            or "couldn't resolve" in lower
            or "name or service not known" in lower
            or "could not resolve host" in lower
            or "couldn't resolve host" in lower
        ):

            return (
                "dns",
                "The repository hostname could not be resolved."
            )

        # ----------------------------------------------------
        # CONNECTION FAILURE
        # ----------------------------------------------------

        if (
            "connection refused" in lower
            or "couldn't connect" in lower
            or "could not connect" in lower
            or "failed to connect" in lower
        ):

            return (
                "connection",
                "Basic Repo could not connect to the repository server."
            )

        # ----------------------------------------------------
        # TIMEOUT
        # ----------------------------------------------------

        if (
            code == 124
            or "timed out" in lower
            or "timeout" in lower
            or "operation too slow" in lower
        ):

            return (
                "timeout",
                "The repository did not respond before the timeout."
            )

        # ----------------------------------------------------
        # TLS / SSL
        # ----------------------------------------------------

        if (
            "certificate verify failed" in lower
            or "ssl certificate" in lower
            or "peer certificate" in lower
            or "certificate problem" in lower
            or "tls error" in lower
        ):

            return (
                "certificate",
                "The repository has an SSL/TLS certificate problem."
            )

        # ----------------------------------------------------
        # CURL / DOWNLOAD ERRORS
        # ----------------------------------------------------

        if (
            "curl error" in lower
            or "download error" in lower
        ):

            return (
                "network",
                "A network/download error occurred while contacting "
                "the repository."
            )

        # ----------------------------------------------------
        # ONLY NOW TRUST EXIT CODE
        # ----------------------------------------------------

        if code == 0:

            return (
                "online",
                "Repository metadata loaded successfully."
            )

        # ----------------------------------------------------
        # UNKNOWN ERROR
        # ----------------------------------------------------

        if len(output) > 1500:
            output = output[-1500:]

        return (
            "error",
            output or
            f"DNF failed while checking the repository "
            f"(exit code {code})."
        )

    # ========================================================
    # CHECK SELECTED REPOSITORY
    # ========================================================

    def check_selected_repo(self):

        if not self.current_repo:
            return

        repo = self.current_repo

        self.status_var.set(
            f"Checking {repo['id']}..."
        )

        self.detail_status.config(
            text="Checking..."
        )

        def worker():

            state, message = (
                self.check_repo_health(
                    repo
                )
            )

            def finished():

                if state == "online":

                    self.detail_status.config(
                        text="Online"
                    )

                    self.status_var.set(
                        f"{repo['id']} is healthy."
                    )

                    messagebox.showinfo(
                        "Repository Healthy",
                        f"{repo['id']}\n\n{message}"
                    )

                else:

                    self.detail_status.config(
                        text=f"Problem — {state.upper()}"
                    )

                    self.status_var.set(
                        f"{repo['id']}: {state.upper()}"
                    )

                    self.show_repo_problem(
                        repo,
                        state,
                        message
                    )

            self.root.after(
                0,
                finished
            )

        self.background(worker)

    # ========================================================
    # REPOSITORY PROBLEM DIALOG
    # ========================================================

    def show_repo_problem(
        self,
        repo,
        state,
        message
    ):

        answer = messagebox.askyesno(
            "Repository Problem",
            f"{repo['id']} has a problem.\n\n"
            f"Status: {state.upper()}\n\n"
            f"{message}\n\n"
            "Would you like to disable this repository?\n\n"
            "Choose No if you want to keep it enabled."
        )

        if answer:

            self.set_repo_enabled(
                repo,
                False
            )

    # ========================================================
    # CHECK ALL REPOSITORIES
    # ========================================================

    def check_all_repositories(self):

        repositories = (
            self.read_repository_files()
        )

        enabled = [
            repo
            for repo in repositories
            if repo["enabled"]
        ]

        if not enabled:

            messagebox.showinfo(
                APP_NAME,
                "There are no enabled repositories to check."
            )

            return

        self.status_var.set(
            "Checking repositories..."
        )

        def worker():

            broken = []

            for index, repo in enumerate(
                enabled,
                start=1
            ):

                self.root.after(
                    0,
                    lambda r=repo, i=index:
                    self.status_var.set(
                        f"Checking {r['id']} "
                        f"({i}/{len(enabled)})..."
                    )
                )

                state, message = (
                    self.check_repo_health(
                        repo
                    )
                )

                if state != "online":

                    broken.append({
                        "repo": repo,
                        "state": state,
                        "message": message
                    })

            self.root.after(
                0,
                lambda:
                self.finish_check_all(
                    enabled,
                    broken
                )
            )

        self.background(worker)

    # ========================================================
    # FINISH CHECK ALL
    # ========================================================

    def finish_check_all(
        self,
        enabled,
        broken
    ):

        if not broken:

            self.status_var.set(
                f"All {len(enabled)} enabled repositories are healthy."
            )

            messagebox.showinfo(
                "Repository Check",
                f"Checked {len(enabled)} enabled repositories.\n\n"
                "No problems were detected."
            )

            return

        self.status_var.set(
            f"{len(broken)} repository problem(s) found."
        )

        report_lines = []

        for problem in broken:

            repo = problem["repo"]
            state = problem["state"]
            message = problem["message"]

            report_lines.append(
                f"{repo['id']}\n"
                f"Status: {state.upper()}\n"
                f"{message}"
            )

        report = "\n\n".join(
            report_lines
        )

        if len(report) > 5000:
            report = (
                report[:5000]
                + "\n\nAdditional results were omitted."
            )

        messagebox.showwarning(
            "Repository Problems",
            f"Checked: {len(enabled)}\n"
            f"Problems: {len(broken)}\n\n"
            f"{report}"
        )

    # ========================================================
    # ENABLE / DISABLE REPOSITORY
    # ========================================================

    def enable_selected_repo(self):

        if not self.current_repo:
            return

        self.set_repo_enabled(
            self.current_repo,
            True
        )

    def disable_selected_repo(self):

        if not self.current_repo:
            return

        self.set_repo_enabled(
            self.current_repo,
            False
        )

    def set_repo_enabled(
        self,
        repo,
        enabled
    ):

        value = (
            "1"
            if enabled
            else "0"
        )

        repo_file = repo["file"]
        repo_id = repo["id"]

        script = f"""
import re

path = {repo_file!r}
repo_id = {repo_id!r}
value = {value!r}

with open(path, "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

output = []
inside = False
found_enabled = False

for line in lines:

    stripped = line.strip()

    section = re.match(
        r"^\\[([^\\]]+)\\]$",
        stripped
    )

    if section:

        if inside and not found_enabled:
            output.append(
                "enabled=" + value + "\\n"
            )

        inside = (
            section.group(1) == repo_id
        )

        found_enabled = False

        output.append(line)
        continue

    if (
        inside
        and stripped.lower().startswith(
            "enabled="
        )
    ):

        output.append(
            "enabled=" + value + "\\n"
        )

        found_enabled = True

    else:

        output.append(line)

if inside and not found_enabled:

    output.append(
        "enabled=" + value + "\\n"
    )

with open(path, "w", encoding="utf-8") as f:
    f.writelines(output)
"""

        message = (
            "Repository enabled."
            if enabled
            else "Repository disabled."
        )

        self.run_privileged_python(
            script,
            message
        )

    # ========================================================
    # DELETE REPOSITORY
    # ========================================================

    def delete_selected_repo(self):

        repo = self.current_repo

        if not repo:
            return

        if not messagebox.askyesno(
            "Delete Repository",
            f"Delete repository '{repo['id']}'?\n\n"
            "Only this repository section will be removed.\n"
            "Other repositories in the same .repo file will be preserved.\n\n"
            "This action cannot be automatically undone."
        ):
            return

        repo_file = repo["file"]
        repo_id = repo["id"]

        script = f"""
import re
import shutil

path = {repo_file!r}
repo_id = {repo_id!r}

backup = path + ".basicrepo.bak"

shutil.copy2(
    path,
    backup
)

with open(
    path,
    "r",
    encoding="utf-8",
    errors="replace"
) as f:
    lines = f.readlines()

output = []
skip = False

for line in lines:

    stripped = line.strip()

    section = re.match(
        r"^\\[([^\\]]+)\\]$",
        stripped
    )

    if section:

        skip = (
            section.group(1)
            == repo_id
        )

    if not skip:
        output.append(line)

with open(
    path,
    "w",
    encoding="utf-8"
) as f:
    f.writelines(output)
"""

        self.run_privileged_python(
            script,
            "Repository deleted.\n\n"
            "A .basicrepo.bak backup was created."
        )

    # ========================================================
    # RUN PRIVILEGED PYTHON
    # ========================================================

    def run_privileged_python(
        self,
        script,
        success_message
    ):

        if not shutil.which(
            "pkexec"
        ):

            messagebox.showerror(
                APP_NAME,
                "pkexec was not found."
            )

            return

        fd, path = tempfile.mkstemp(
            suffix=".py",
            prefix="basic_repo_"
        )

        try:

            with os.fdopen(
                fd,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(script)

        except OSError as error:

            messagebox.showerror(
                APP_NAME,
                str(error)
            )

            return

        command = [
            "pkexec",
            "python3",
            path
        ]

        self.status_var.set(
            "Waiting for authentication..."
        )

        def worker():

            code, out, error = (
                self.command(
                    command
                )
            )

            try:
                os.remove(path)
            except OSError:
                pass

            def finished():

                if code == 0:

                    messagebox.showinfo(
                        APP_NAME,
                        success_message
                    )

                    self.show_repositories()

                else:

                    messagebox.showerror(
                        APP_NAME,
                        error or out or
                        "Operation failed."
                    )

            self.root.after(
                0,
                finished
            )

        self.background(worker)

    # ========================================================
    # AUTOMATIC REPOSITORY CHECK
    # ========================================================

    def start_automatic_repo_check(self):

        if not AUTO_REPO_CHECK:
            return

        if self.auto_check_running:

            self.schedule_next_auto_check()
            return

        self.auto_check_running = True

        self.status_var.set(
            "Automatic repository check started..."
        )

        self.background(
            self.automatic_repo_check_worker
        )

    # ========================================================
    # AUTOMATIC CHECK WORKER
    # ========================================================

    def automatic_repo_check_worker(self):

        repositories = (
            self.read_repository_files()
        )

        enabled = [
            repo
            for repo in repositories
            if repo["enabled"]
        ]

        broken = []

        for index, repo in enumerate(
            enabled,
            start=1
        ):

            self.root.after(
                0,
                lambda r=repo, i=index:
                self.status_var.set(
                    f"Auto-check: {r['id']} "
                    f"({i}/{len(enabled)})"
                )
            )

            state, message = (
                self.check_repo_health(
                    repo
                )
            )

            if state != "online":

                broken.append({
                    "repo": repo,
                    "state": state,
                    "message": message
                })

        self.root.after(
            0,
            lambda:
            self.automatic_repo_check_finished(
                broken,
                len(enabled)
            )
        )

    # ========================================================
    # AUTOMATIC CHECK FINISHED
    # ========================================================

    def automatic_repo_check_finished(
        self,
        broken,
        checked_count
    ):

        self.auto_check_running = False

        if not broken:

            self.status_var.set(
                f"Automatic check: "
                f"{checked_count} repositories healthy."
            )

            self.schedule_next_auto_check()
            return

        self.status_var.set(
            f"Automatic check found "
            f"{len(broken)} problem(s)."
        )

        report_lines = []

        for problem in broken:

            repo = problem["repo"]
            state = problem["state"]
            message = problem["message"]

            report_lines.append(
                f"{repo['id']}\n"
                f"Status: {state.upper()}\n"
                f"{message}"
            )

        report = "\n\n".join(
            report_lines
        )

        if len(report) > 4500:

            report = (
                report[:4500]
                + "\n\nMore results were omitted."
            )

        answer = messagebox.askyesno(
            "Repository Problems Detected",
            f"Basic Repo automatically checked "
            f"{checked_count} enabled repositories.\n\n"
            f"{len(broken)} problem(s) were found:\n\n"
            f"{report}\n\n"
            "Open the Repositories page?"
        )

        if answer:
            self.show_repositories()

        self.schedule_next_auto_check()

    # ========================================================
    # SCHEDULE NEXT AUTO CHECK
    # ========================================================

    def schedule_next_auto_check(self):

        if not AUTO_REPO_CHECK:
            return

        self.root.after(
            AUTO_CHECK_INTERVAL,
            self.start_automatic_repo_check
        )

    # ========================================================
    # ADD REPOSITORY FILE
    # ========================================================

    def add_repo_file(self):

        source = filedialog.askopenfilename(
            title="Select Repository File",
            filetypes=[
                (
                    "DNF Repository",
                    "*.repo"
                ),
                (
                    "All Files",
                    "*"
                )
            ]
        )

        if not source:
            return

        filename = os.path.basename(
            source
        )

        destination = os.path.join(
            REPO_DIR,
            filename
        )

        if os.path.exists(
            destination
        ):

            if not messagebox.askyesno(
                "Repository Exists",
                f"{filename} already exists in:\n\n"
                f"{REPO_DIR}\n\n"
                "Replace it?"
            ):
                return

        else:

            if not messagebox.askyesno(
                "Add Repository",
                f"Add this repository configuration?\n\n"
                f"{filename}\n\n"
                f"Destination:\n{destination}"
            ):
                return

        command = [
            "pkexec",
            "install",
            "-m",
            "0644",
            os.path.abspath(source),
            destination
        ]

        self.status_var.set(
            "Waiting for authentication..."
        )

        def worker():

            code, out, error = (
                self.command(
                    command
                )
            )

            def finished():

                if code == 0:

                    messagebox.showinfo(
                        APP_NAME,
                        "Repository file added."
                    )

                    self.show_repositories()

                else:

                    messagebox.showerror(
                        APP_NAME,
                        error or out or
                        "Could not add repository."
                    )

            self.root.after(
                0,
                finished
            )

        self.background(worker)


# ============================================================
# STARTUP
# ============================================================

def main():

    required = (
        "dnf",
        "rpm",
        "pkexec"
    )

    missing = [
        command
        for command in required
        if not shutil.which(command)
    ]

    if missing:

        print(
            f"{APP_NAME} cannot start.\n\n"
            "Missing command(s): "
            + ", ".join(missing)
        )

        return

    root = tk.Tk()

    BasicRepo(root)

    root.mainloop()


if __name__ == "__main__":
    main()
