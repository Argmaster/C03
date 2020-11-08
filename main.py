# -*- encoding: utf-8 -*-
from tkinter import Canvas, StringVar, Tk, Text, IntVar
from tkinter.constants import BOTH, COMMAND, END, FLAT, LEFT, RADIOBUTTON, X, Y
import logging
from tkinter.font import Font
from tkinter.ttk import *
import json
from widget import AbstractWidget, Frame, AbstractMenu
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showwarning, askyesno


class DarkMenu(AbstractMenu):
    def __apperance__(self):
        self.config(
            background="#444444", foreground="white", relief=FLAT, activeborderwidth=5
        )


class ReText(Text):
    def highlight_pattern(self, pattern, tag, start="1.0", end="end", regexp=True):

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = IntVar()
        while True:
            index = self.search(
                pattern, "matchEnd", "searchLimit", count=count, regexp=regexp
            )
            if index == "":
                break
            if count.get() == 0:
                break  # degenerate pattern which matches zero-length strings
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")


class TextLineNumbers(Canvas):
    def start(self, textwidget, font):
        self.textwidget = textwidget
        self.font = font
        self.redraw()

    def redraw(self, *args):
        """redraw line numbers"""
        self.delete("all")

        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = f"{str(i).split('.')[0]: >4}"
            self.create_text(
                10, y, anchor="nw", text=linenum, fill="#AAAAAA", font=self.font
            )
            i = self.textwidget.index("%s+1line" % i)

        # Refreshes the canvas widget 30fps
        self.after(30, self.redraw)


class Window(AbstractWidget, Tk):
    def __apperance__(self):
        self.eval(
            """
    set base_theme_dir awthemes-9.5.0/

    package ifneeded awthemes 9.5.0 \
        [list source [file join $base_theme_dir awthemes.tcl]]
    package ifneeded colorutils 4.8 \
        [list source [file join $base_theme_dir colorutils.tcl]]
    package ifneeded awdark 7.9 \
        [list source [file join $base_theme_dir awdark.tcl]]
    # ... (you can add the other themes from the package if you want
    """
        )
        self.tk.call("package", "require", "awdark")
        STYLE = Style()
        STYLE.theme_use("awdark")
        STYLE.map(
            ".",
            relief=[("pressed", FLAT), ("!pressed", FLAT)],
            padding=[("pressed", "5 5"), ("!pressed", "5 5")],
            focuscolor=[
                ("pressed", STYLE.lookup("TButton", "background")),
                ("!pressed", STYLE.lookup("TButton", "background")),
            ],
        )
        STYLE.configure(".", background="#252525")
        self.title("Compare")
        self.minsize(900, 600)

    def __children__(self):
        self.FONT = Font(family="consolas", size=14)
        self.FILE = [
            {
                "path": "",
                "opened": False,
                "text": StringVar(),
                "need_save": False,
                "encoding": "utf-8",
            },
            {
                "path": "",
                "opened": False,
                "text": StringVar(),
                "need_save": False,
                "encoding": "utf-8",
            },
        ]
        self.FILE[0]["text"].trace("w", lambda *_: self.replace_text_content(0))
        self.FILE[1]["text"].trace("w", lambda *_: self.replace_text_content(1))
        topbar = self.pack_in(
            "menuFrame", Frame, {"style": "TFrame"}, {"expand": False, "fill": X}
        )
        topmenu0 = self.add_child(
            "topMenuBar0",
            DarkMenu(
                [
                    (
                        COMMAND,
                        {"label": "Open", "command": lambda: self.open_file_dialog(0)},
                    ),
                    (
                        COMMAND,
                        {"label": "Save", "command": lambda: self.save_file_dialog(0)},
                    ),
                ],
                tearoff=False,
            ),
        )
        topbar.pack_in(
            "menuButton0",
            Menubutton,
            {"menu": topmenu0, "text": "First file"},
            {"side": LEFT},
        )
        topmenu1 = self.add_child(
            "topMenuBar1",
            DarkMenu(
                [
                    (
                        COMMAND,
                        {"label": "Open", "command": lambda: self.open_file_dialog(1)},
                    ),
                    (
                        COMMAND,
                        {"label": "Save", "command": lambda: self.save_file_dialog(1)},
                    ),
                ],
                tearoff=False,
            ),
        )
        topbar.pack_in(
            "menuButton1",
            Menubutton,
            {"menu": topmenu1, "text": "Second file"},
            {"side": LEFT},
        )
        topbar.pack_in(
            "compareButton",
            Button,
            {
                "text": "Compare",
                "command": lambda *_: self.compare(self.text_0, self.text_1),
            },
            {"side": LEFT},
        )
        numbers_0 = self.pack_in(
            "numbers",
            TextLineNumbers,
            {"width": 70, "background": "#242424", "highlightthickness": 0},
            {"expand": False, "fill": Y, "side": LEFT},
        )
        text_frame_0 = self.pack_in(
            "text_frame_0",
            Frame,
            {"style": "TFrame"},
            {"expand": True, "fill": BOTH, "side": LEFT},
        )
        self.text_0 = text_frame_0.place_in(
            0,
            ReText,
            {
                "selectbackground": "#393e4d",
                "relief": FLAT,
                "insertwidth": 3,
                "undo": 10,
                "insertbackground": "#AAAAFF",
                "background": "#292929",
                "borderwidth": 5,
                "foreground": "white",
                "font": self.FONT,
            },
            {"relx": 0, "relwidth": 1, "relheight": 1},
        )
        scroll_0 = self.pack_in(
            "scroll1",
            Scrollbar,
            {"command": self.text_0.yview},
            {"expand": False, "fill": Y, "side": LEFT},
        )
        self.text_0["yscrollcommand"] = scroll_0.set
        numbers_0.start(self.text_0, self.FONT)
        numbers_1 = self.pack_in(
            "numbers",
            TextLineNumbers,
            {"width": 70, "background": "#242424", "highlightthickness": 0},
            {"expand": False, "fill": Y, "side": LEFT},
        )
        text_frame_1 = self.pack_in(
            "text_frame_1",
            Frame,
            {"style": "TFrame"},
            {"expand": True, "fill": BOTH, "side": LEFT},
        )
        self.text_1 = text_frame_1.place_in(
            1,
            ReText,
            {
                "selectbackground": "#393e4d",
                "relief": FLAT,
                "insertwidth": 3,
                "undo": 10,
                "insertbackground": "#AAFFAA",
                "background": "#292929",
                "borderwidth": 5,
                "foreground": "white",
                "font": self.FONT,
            },
            {"relx": 0, "relwidth": 1, "relheight": 1},
        )
        scroll_1 = self.pack_in(
            "scroll1",
            Scrollbar,
            {"command": self.text_1.yview},
            {"expand": False, "fill": Y, "side": LEFT},
        )
        self.text_1["yscrollcommand"] = scroll_1.set
        numbers_1.start(self.text_1, self.FONT)
        self.text_widget = [self.text_0, self.text_1]
        self.load_patterns()
        self.selected_laguage = "none"
        self.select_language("none")
        topmenu3 = self.add_child(
            "topMenuBar1",
            DarkMenu(
                [
                    (
                        RADIOBUTTON,
                        {
                            "label": "None",
                            "command": lambda: self.select_language("none"),
                        },
                    ),
                    (
                        RADIOBUTTON,
                        {
                            "label": "Python",
                            "command": lambda: self.select_language("python"),
                        },
                    ),
                    (
                        RADIOBUTTON,
                        {
                            "label": "C++",
                            "command": lambda: self.select_language("cpp"),
                        },
                    ),
                ],
                tearoff=False,
            ),
        )
        topbar.pack_in(
            "menuButton3",
            Menubutton,
            {"menu": topmenu3, "text": "Language"},
            {"side": LEFT},
        )

    def load_patterns(self):
        with open("patterns.json") as file:
            self.patterns = json.load(file)

    def select_language(self, lang):
        for text in self.text_widget:
            for pattern in self.patterns[self.selected_laguage]:
                text.tag_delete(pattern[0])
        self.selected_laguage = lang
        for text in self.text_widget:

            text.tag_configure("ERROR", background="#ff3355", foreground="white")
            for pattern in self.patterns[lang]:
                text.tag_configure(pattern[0], **pattern[2])

    def replace_text_content(self, file_index):
        text_widget = self.text_widget[file_index]
        text_widget.delete("0.0", END)
        text_widget.insert(END, self.FILE[file_index]["text"].get())

    def open_file_dialog(self, file_index):
        if self.FILE[file_index]["need_save"]:
            if not askyesno(
                "Opening new file",
                "You have unsaved changes in file one, do you want to save current file?",
            ):
                return
            else:
                self.save_file_dialog(file_index)
        path = askopenfilename(initialdir=".", title="Select file")
        if path:
            try:
                with open(path) as file:
                    self.FILE[file_index]["text"].set(file.read())
                self.FILE[file_index]["path"] = path
                self.FILE[file_index]["opened"] = True
            except UnicodeDecodeError:
                self.FILE[file_index]["path"] = ""
                showwarning("Cannot open file")
                return

    def highlight_func(self, text):
        text.tag_remove("COMMENT", 0.0, END)
        try:
            for pattern in self.patterns[self.selected_laguage]:
                for sub_pattern in pattern[1]:
                    text.highlight_pattern(sub_pattern, pattern[0])
        except Exception as e:
            logging.error(e)
        self.after(500, lambda: self.highlight_func(text))

    def compare(self, text_0: ReText, text_1: ReText):
        text_0.tag_remove("ERROR", 0.0, END)
        text_1.tag_remove("ERROR", 0.0, END)
        l = [text_0.count(0.0, END, "lines"), text_1.count(0.0, END, "lines")]
        for i, v in enumerate(l):
            if isinstance(v, tuple):
                l[i] = v[0]
            elif isinstance(v, int):
                pass
            else:
                l[i] = 0
        line_count = max(l)
        for line in range(line_count if line_count is not None else 0):
            c = [
                text_0.count(f"{line}.0", f"{line}.0 lineend", "chars"),
                text_1.count(f"{line}.0", f"{line}.0 lineend", "chars"),
            ]
            for i, v in enumerate(c):
                if isinstance(v, tuple):
                    c[i] = v[0]
                elif isinstance(v, int):
                    pass
                else:
                    c[i] = 0
            char_count = max(c)
            comment = False
            for char in range(char_count if char_count is not None else 0):
                curr = f"{line}.{char}"
                if text_0.get(curr) != text_1.get(curr):
                    self.text_1.tag_add("ERROR", curr)
                    self.text_0.tag_add("ERROR", curr)

    def save_file_dialog(self, file_index):
        pass

    def __bind__(self):
        self.bind("<Escape>", self.exit)
        self.bind("<Control-MouseWheel>", self.zoom)
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.after(500, lambda: self.highlight_func(self.text_0))
        self.after(500, lambda: self.highlight_func(self.text_1))

    def zoom(self, event):
        if event.delta > 0:
            self.FONT.config(size=self.FONT.cget("size") + 1)
        else:
            self.FONT.config(size=self.FONT.cget("size") - 1)

    def exit(self, *args, **kwargs):
        self.destroy()
        exit()


if __name__ == "__main__":
    Window().mainloop()
