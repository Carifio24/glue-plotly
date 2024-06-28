from echo import CallbackProperty
from glue.viewers.common.state import ViewerState


class PlotlyBase3dViewerState(ViewerState):
    native_aspect = CallbackProperty(False)
