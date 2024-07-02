from glue_plotly.viewers.base_3d.layer_options_widget import Plotly3dLayerStateWidget
from glue_plotly.viewers.base_3d.viewer_options_widget import Plotly3dViewerStateWidget
from glue_plotly.viewers.isosurface.layer_artist import PlotlyIsosurfaceLayerArtist
from glue_plotly.viewers.isosurface.viewer_state import PlotlyIsosurfaceViewerState
from ..base_3d import PlotlyBase3dView


class PlotlyIsosurfaceView(PlotlyBase3dView):

    _state_cls = PlotlyIsosurfaceViewerState
    _options_cls = Plotly3dViewerStateWidget
    _data_artist_cls = PlotlyIsosurfaceLayerArtist 
    _subset_artist_cls = PlotlyIsosurfaceLayerArtist
    _layer_style_widget_cls = Plotly3dLayerStateWidget
