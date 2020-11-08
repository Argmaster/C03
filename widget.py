# -*- encoding: utf-8 -*-
from tkinter.constants import CASCADE, CHECKBUTTON, COMMAND, RADIOBUTTON
from tkinter.ttk import Widget, Frame
from tkinter import Menu, Variable

from typing_extensions import IntVar


class AbstractWidget:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._children = {}
        self.__apperance__()
        self.__children__()
        self.__bind__()

    def __bind__(self):
        pass

    def __children__(self):
        pass

    def __apperance__(self):
        pass

    def pack_in(
        self,
        name: str,
        widget: Widget,
        widget_kwargs: dict = {},
        placing_kwargs: dict = {},
    ):
        widget = widget(self, **widget_kwargs)
        widget.pack(**placing_kwargs)
        self._children[name] = widget
        return widget

    def grid_in(
        self,
        name: str,
        widget: Widget,
        widget_kwargs: dict = {},
        placing_kwargs: dict = {},
    ):
        widget = widget(self, **widget_kwargs)
        widget.grid(**placing_kwargs)
        self._children[name] = widget
        return widget

    def place_in(
        self,
        name: str,
        widget: Widget,
        widget_kwargs: dict = {},
        placing_kwargs: dict = {},
    ):
        widget = widget(self, **widget_kwargs)
        widget.place(**placing_kwargs)
        self._children[name] = widget
        return widget

    def get_child(self, child_name: str):
        return self._children[child_name]

    def add_child(self, child_name: str, child: Widget):
        self._children[child_name] = child
        return child


class AbstractMenu(AbstractWidget, Menu):
    def __init__(self, menu, **kwargs) -> None:
        super().__init__(**kwargs)
        self.kwargs = kwargs
        self._children = {}
        self._menu = menu
        self.__resolve__()
        self.__apperance__()
        self.__children__()
        self.__bind__()

    def __resolve__(self):
        for opt in self._menu:
            if opt[0] == CASCADE:
                in_menu = self.__class__(opt[2], **self.kwargs)
                self.add_cascade(label=opt[1], menu=in_menu)
            else:
                self.add(opt[0], **opt[1])


class Frame(AbstractWidget, Frame):
    pass
