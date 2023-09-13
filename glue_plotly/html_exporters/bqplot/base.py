from tkinter import filedialog, Tk 

from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO  # noqa


class PlotlyBaseBqplotExport(Tool):
    icon = PLOTLY_LOGO
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):

        # We need the Tk shenanigans in order to make sure that the dialog gets focus on OSX
        root = Tk()
        # Hide the window
        root.attributes('-alpha', 0.0)
        # Always have it on top
        root.attributes('-topmost', True)

        filepath = filedialog.asksaveasfilename(parent=root,
                                                filetypes=[('HTML document', '*.html')],
                                                defaultextension=".html",
                                                title="Select export filepath",
                                                initialfile="plot.html")
        root.withdraw()
        root.destroy()
        if filepath:
            self.save_figure(filepath)

    def save_figure(self, filepath):
        raise NotImplementedError()
