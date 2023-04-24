from __future__ import absolute_import, division, print_function

import numpy as np
import matplotlib.colors as colors
from matplotlib.colors import Normalize

from qtpy import compat
from qtpy.QtWidgets import QDialog

from glue.config import viewer_tool, settings
from glue.core import DataCollection, Data
from glue.utils import ensure_numerical
from glue.utils.qt import messagebox_on_error
from glue.utils.qt.threading import Worker

try:
    from glue.viewers.common.qt.tool import Tool
except ImportError:
    from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_ERROR_MESSAGE, PLOTLY_LOGO
from glue_plotly.common import color_info, data_count, layers_to_export
from glue_plotly.common.scatter3d import clipped_data, layout_config, size_info
from .. import save_hover, export_dialog

from plotly.offline import plot
import plotly.graph_objs as go
from glue.core.qt.dialogs import warn

DEFAULT_FONT = 'Arial, sans-serif'
settings.add('SHOW_WARN_PLOTLY_3D_GRAPHICS_DIFFERENT', True)


@viewer_tool
class PlotlyScatter3DStaticExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:plotly3d'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    @messagebox_on_error(PLOTLY_ERROR_MESSAGE)
    def _export_to_plotly(self, filename, checked_dictionary):

        config = layout_config(self.viewer)
        layout = go.Layout(**config)
        fig = go.Figure(layout=layout)

        layers = layers_to_export(self.viewer)
        add_data_label = data_count(layers) > 1
        for layer in layers:

            layer_state = layer.state

            x, y, z, mask = clipped_data(self.viewer, layer)
            marker = dict(color=color_info(layer, mask=mask),
                          size=size_info(layer, mask),
                          opacity=layer_state.alpha,
                          line=dict(width=0))

            # add hover info to layer
            if np.sum(checked_dictionary[layer_state.layer.label]) == 0:
                hoverinfo = 'skip'
                hovertext = None
            else:
                hoverinfo = 'text'
                hovertext = ["" for i in range((mask.shape[0]))]
                for i in range(len(layer_state.layer.components)):
                    if checked_dictionary[layer_state.layer.label][i]:
                        label = layer_state.layer.components[i].label
                        hover_data = layer_state.layer[label][mask]
                        for k in range(len(hover_data)):
                            hovertext[k] = (hovertext[k] + "{}: {} <br>"
                                            .format(label, hover_data[k]))

            if layer_state.vector_visible:
                vx = layer_state.layer[layer_state.vx_attribute][mask]
                vy = layer_state.layer[layer_state.vy_attribute][mask]
                vz = layer_state.layer[layer_state.vz_attribute][mask]
                # convert anchor names from glue values to plotly values
                anchor_dict = {'middle': 'center', 'tip': 'tip', 'tail': 'tail'}
                anchor = anchor_dict[layer_state.vector_origin]
                name = layer_state.layer.label + " cones"
                scaling = layer_state.vector_scaling
                cones = []
                vx_v = scaling * vx
                vy_v = scaling * vy
                vz_v = scaling * vz

                if layer_state.color_mode == 'Fixed':
                    # get the singular color in rgb format
                    rgb_color = [int(c * 256) for c in colors.to_rgb(marker["color"])]
                    c = 'rgb{}'.format(tuple(rgb_color))
                    colorscale = [[0, c], [1, c]]

                    for i in range(len(x)):
                        ht = None if hovertext is None else [hovertext[i]]
                        cone_info = dict(x=[x[i]], y=[y[i]], z=[z[i]],
                                         u=[vx_v[i]], v=[vy_v[i]], w=[vz_v[i]],
                                         name=name, anchor=anchor, colorscale=colorscale,
                                         hoverinfo=hoverinfo, hovertext=ht,
                                         showscale=False, legendgroup=name,
                                         sizemode="absolute", showlegend=not i, sizeref=1)
                        cones.append(cone_info)
                else:
                    rgb_colors = [tuple(int(t * 256) for t in rgba[:3]) for rgba in rgba_list]
                    for i in range(len(marker['color'])):
                        c = 'rgb{}'.format(rgb_colors[i])
                        ht = None if hovertext is None else [hovertext[i]]
                        cone_info = dict(x=[x[i]], y=[y[i]], z=[z[i]],
                                         u=[vx_v[i]], v=[vy_v[i]], w=[vz_v[i]],
                                         name=name, anchor=anchor, colorscale=[[0, c], [1, c]],
                                         hoverinfo=hoverinfo, hovertext=ht,
                                         showscale=False, legendgroup=name,
                                         sizemode="scaled", showlegend=not i, sizeref=1)
                        cones.append(cone_info)
                fig.update_layout(layout)

            # add error bars
            xerr = {}
            if layer_state.xerr_visible:
                xerr['type'] = 'data'
                xerr['array'] = np.absolute(ensure_numerical(
                    layer_state.layer[layer_state.xerr_attribute][mask].ravel()))
                xerr['visible'] = True

            yerr = {}
            if layer_state.yerr_visible:
                yerr['type'] = 'data'
                yerr['array'] = np.absolute(ensure_numerical(
                    layer_state.layer[layer_state.yerr_attribute][mask].ravel()))
                yerr['visible'] = True

            zerr = {}
            if layer_state.zerr_visible:
                zerr['type'] = 'data'
                zerr['array'] = np.absolute(ensure_numerical(
                    layer_state.layer[layer_state.zerr_attribute][mask].ravel()))
                zerr['visible'] = True

            # add layer to axes
            fig.add_scatter3d(x=x, y=y, z=z,
                              error_x=xerr,
                              error_y=yerr,
                              error_z=zerr,
                              mode='markers',
                              marker=marker,
                              hoverinfo=hoverinfo,
                              hovertext=hovertext,
                              name=layer_state.layer.label)

            # add the cones here so that they show up after the data in the legend
            if layer_state.vector_visible:
                for cone in cones:
                    fig.add_cone(**cone)

        plot(fig, filename=filename, auto_open=False)

    def activate(self):

        # grab hover info
        dc_hover = DataCollection()

        for layer in self.viewer.layers:
            layer_state = layer.state
            if layer_state.visible and layer.enabled:
                data = Data(label=layer_state.layer.label)
                for component in layer_state.layer.components:
                    data[component.label] = np.ones(10)
                dc_hover.append(data)

        checked_dictionary = {}

        # figure out which hover info user wants to display
        for layer in self.viewer.layers:
            layer_state = layer.state
            if layer_state.visible and layer.enabled:
                checked_dictionary[layer_state.layer.label] = np.zeros((len(layer_state.layer.components))).astype(bool)

        proceed = warn('Scatter 3d plotly may look different',
                       'Plotly and Matlotlib graphics differ and your graph may look different when exported. Do you '
                       'want to proceed?',
                       default='Cancel', setting='SHOW_WARN_PLOTLY_3D_GRAPHICS_DIFFERENT')
        if not proceed:
            return

        dialog = save_hover.SaveHoverDialog(data_collection=dc_hover, checked_dictionary=checked_dictionary)
        result = dialog.exec_()
        if result == QDialog.Rejected:
            return

        # query filename
        filename, _ = compat.getsavefilename(
            parent=self.viewer, basedir="plot.html")
        if not filename:
            return

        worker = Worker(self._export_to_plotly, filename, checked_dictionary)
        exp_dialog = export_dialog.ExportDialog(parent=self.viewer)
        worker.result.connect(exp_dialog.close)
        worker.error.connect(exp_dialog.close)
        worker.start()
        exp_dialog.exec_()
