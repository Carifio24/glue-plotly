from tkinter import filedialog

from glue.viewers.common.tool import Tool

from pytest import importorskip

importorskip('ipyvuetify')

from glue_plotly import PLOTLY_LOGO  # noqa


class PlotlyBaseBqplotExport(Tool):
    icon = PLOTLY_LOGO
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):
        filepath = filedialog.asksaveasfilename(filetypes=[('HTML document', '*.html')],
                                                defaultextension=".html",
                                                title="Select export filepath",
                                                initialfile="plot.html")
        print("In activate")
        print(filepath)
        if filepath:
            self.save_figure(filepath)

    def save_figure(self, filepath):
        raise NotImplementedError()
