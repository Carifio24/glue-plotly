from glue.viewers.scatter.state import DDCProperty, ScatterLayerState


class PlotlyScatterLayerState(ScatterLayerState):

    border_visible = DDCProperty(False, docstring="Whether to show borders on the markers")
    border_size = DDCProperty(1, docstring="The size of the marker borders")
    border_color = DDCProperty(docstring="The color of the marker borders")