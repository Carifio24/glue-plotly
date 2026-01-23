
import plotly.graph_objs as go
from glue_qt.core.dialogs import warn
from glue_qt.utils import messagebox_on_error
from plotly.offline import plot
from qtpy import compat
from qtpy.QtWidgets import QDialog
import numpy as np

from glue.config import settings, viewer_tool
from glue.viewers.common.tool import Tool
from glue_plotly import PLOTLY_ERROR_MESSAGE, PLOTLY_LOGO
from glue_plotly.common import data_count, layers_to_export
from glue_plotly.common.scatter2d import (
    geo_annotations,
    geo_layout_config,
    geo_ticks,
    polar_layout_config_from_mpl,
    rectilinear_layout_config,
    traces_for_layer,
)
from glue_plotly.html_exporters.hover_utils import hover_data_collection_for_viewer
from glue_plotly.html_exporters.qt.save_hover import SaveHoverDialog

DEFAULT_FONT = "Arial, sans-serif"

SHOW_PLOTLY_VECTORS_2D_DIFFERENT = "SHOW_PLOTLY_2D_VECTORS_DIFFERENT"
settings.add(SHOW_PLOTLY_VECTORS_2D_DIFFERENT, True)

import plotly.graph_objects as go

def add_scattergeo_size_legend(fig, sizes, labels=None, units="", text_color="black", title="Size scale"):
    """
    Adds a real marker-size legend to a scattergeo figure by using
    dummy traces whose markers match the real pixel sizes exactly.
    """

    if labels is None:
        labels = [f"{s} {units}".strip() for s in sizes]

    if len(labels) != len(sizes):
        raise ValueError("labels must match sizes in length")

    # We use 'lon=[None], lat=[None]' so they do not appear on the map,
    # but they DO appear in the legend.
    for s, label in zip(sizes, labels):
        fig.add_trace(go.Scattergeo(
            lon=[None],
            lat=[None],
            mode="markers",
            marker=dict(size=s, color=text_color),
            showlegend=True,
            name=label
        ))

    # optional: move legend to the right
    update = dict(
        margin=dict(r=120),
        legend=dict(
            itemclick=False,
            itemdoubleclick=False,
            font=dict(color=text_color),
            x=1.05,
            y=0.95
        )
    )
    if title:
        update["legend"]["title"] = title
    fig.update_layout(update)

def add_geo_size_legend(
    fig,
    sizes,
    labels=None,        # optional custom labels
    units="",
    title="Size Scale",
    x=1.05,             # paper coordinates (0–1)
    y=0.8,
    spacing=0.10,
    bubble_scale=0.6,   # scales marker size -> font size
    bubble_color="gray",
    text_color="black",
    font_size=12,
):
    """
    Add a bubble-size legend to a scattergeo figure using annotations.

    Parameters
    ----------
    fig : go.Figure
        Figure with a Scattergeo trace.
    sizes : list[float]
        Marker sizes used in the plot (in px).
    labels : list[str] or None
        Custom labels for each bubble. If None, uses "<size> <units>".
    units : str
        Units suffix for auto labels.
    title : str
        Title shown above the size legend.
    x, y : float
        Anchor position in *paper* coordinates (0–1).
    spacing : float
        Vertical spacing between entries in paper coords.
    bubble_scale : float
        Multiplier from marker.size to font.size for the “●” bubbles.
    bubble_color : str
        Color of the bubble symbols.
    text_color : str
        Color of the labels.
    font_size : int
        Base font size for the labels.
    """

    if labels is not None and len(labels) != len(sizes):
        raise ValueError("labels must be the same length as sizes")

    annotations = []

    # Title
    if title:
        annotations.append(dict(
            x=x,
            y=y + spacing * 0.5,
            xref="paper",
            yref="paper",
            text=f"<b>{title}</b>",
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
            font=dict(size=font_size + 2, color=text_color),
        ))

    # Each bubble + label
    for i, s in enumerate(sizes):
        y_pos = y - i * spacing
        bubble_font_size = s * bubble_scale

        if labels is None:
            label = f"{s} {units}".strip()
        else:
            label = labels[i]

        # Bubble (big dot)
        annotations.append(dict(
            x=x,
            y=y_pos,
            xref="paper",
            yref="paper",
            text="●",
            showarrow=False,
            xanchor="center",
            yanchor="middle",
            font=dict(size=bubble_font_size, color=bubble_color),
        ))

        # Label
        annotations.append(dict(
            x=x + 0.01,
            y=y_pos,
            xref="paper",
            yref="paper",
            text=label,
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            font=dict(size=font_size, color=text_color),
        ))

    # Apply annotations & leave room on right
    fig.update_layout(
        annotations=(fig.layout.annotations or []) + tuple(annotations),
        margin=dict(r=120)
    )

@viewer_tool
class PlotlyScatter2DStaticExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = "save:plotly2d"
    action_text = "Save Plotly HTML page"
    tool_tip = "Save Plotly HTML page"

    @messagebox_on_error(PLOTLY_ERROR_MESSAGE)
    def activate(self):

        dc_hover = hover_data_collection_for_viewer(self.viewer)
        checked_dictionary = {}

        # figure out which hover info user wants to display
        for layer in self.viewer.layers:
            layer_state = layer.state
            if layer_state.visible and layer.enabled:
                components_checked = { component.label: False
                                       for component in layer_state.layer.components }
                checked_dictionary[layer_state.layer.label] = components_checked

        dialog = SaveHoverDialog(data_collection=dc_hover,
                                 checked_dictionary=checked_dictionary)
        # result = dialog.exec_()
        # if result == QDialog.Rejected:
        #     return

        # filename, _ = compat.getsavefilename(parent=self.viewer, basedir="plot.html")
        filename = "/Users/jon/dev/klessen-interactive-figure/mollweide_nolegend_bw.html"
        if not filename:
            return

        rectilinear = getattr(self.viewer.state, "using_rectilinear", True)
        polar = getattr(self.viewer.state, "using_polar", False)

        if rectilinear:
            layout_config = rectilinear_layout_config(self.viewer)
        elif polar:
            layout_config = polar_layout_config_from_mpl(self.viewer)
        else:
            layout_config = geo_layout_config(self.viewer)

        if rectilinear:
            need_vectors = any(layer.state.vector_visible and \
                               layer.state.vector_scaling > 0.1
                               for layer in self.viewer.layers)
            if need_vectors:
                warning_title = "Arrows may look different"
                warning_text = (
                    "Plotly and Matlotlib vector graphics differ "
                    "and your graph may look different when exported. "
                    "Do you want to proceed?",
                )
                proceed = warn(title=warning_title,
                               text=warning_text,
                               default="Cancel",
                               setting=SHOW_PLOTLY_VECTORS_2D_DIFFERENT)
                if not proceed:
                    return

        layout = go.Layout(**layout_config)
        fig = go.Figure(layout=layout)

        if not (rectilinear or polar):
            for tick in geo_ticks(self.viewer.state):
                fig.add_trace(tick)
            for ann in geo_annotations(self.viewer.state):
                fig.add_annotation(ann)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1

        def size_for_value(v):
            scale = 0.251188643150958
            vmax = -1.44
            vmin = 6.499575
            norm = (v - vmin) / (vmax - vmin)
            s = norm * 0.95 + 0.05
            s *= (45 * scale)
            return s

        mags = [i for i in range(-1, 7)]
        sizes = [size_for_value(v) for v in mags]
        labels = [str(i) for i in mags]

        add_scattergeo_size_legend(
            fig=fig,
            sizes=sizes,
            labels=labels,
            units="m",
            text_color="white",
            title="m",
        )

        n_traces_so_far = len(fig.data)
        layers = sorted(layers, key=lambda layer: -layer.zorder)
        for layer in layers:
            hover_data = checked_dictionary[layer.state.layer.label]
            traces = traces_for_layer(self.viewer,
                                      layer.state,
                                      hover_data=hover_data,
                                      add_data_label=add_data_label)
            fig.add_traces(traces)

        positions = ["Sun", "P1", "P2"]
        colors = ["#f8f8f4", "#10fdf5", "#f3ab9b"]
        buttons = [
            dict(label=name,
                 method="update",
                 args=[
                     {"visible": ([True] * n_traces_so_far) + [i == index for i in range(len(positions))] + [True, True]},
                     {"geo.framecolor": colors[index]},
                 ]
            ) for index, name in enumerate(positions)
        ]
        for trace in fig.data:
            trace.update(showlegend=False)
        fig.update_layout(
            autosize=True,
            width=None,
            height=None,
            updatemenus=[
                dict(
                    type="buttons",
                    direction="left",
                    bgcolor="darkgray",
                    font=dict(color="black"),
                    active=0,
                    x=0.57,
                    y=1.2,
                    buttons=buttons
                )
            ]
        )

        config = dict(responsive=True, displayModeBar=False)

        plot(fig, filename=filename, auto_open=False, config=config)
