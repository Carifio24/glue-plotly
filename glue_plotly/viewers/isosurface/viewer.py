from glue_plotly.viewers.isosurface.layer_artist import PlotlyIsosurfaceLayerArtist
from glue_plotly.viewers.isosurface.viewer_state import PlotlyIsosurfaceViewerState
from ..base_3d import PlotlyBase3dView


class PlotlyIsosurfaceView(PlotlyBase3dView):

    _state_cls = PlotlyIsosurfaceViewerState
    _data_artist_cls = PlotlyIsosurfaceLayerArtist 
    _subset_artist_cls = PlotlyIsosurfaceLayerArtist
