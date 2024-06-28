from echo import CallbackProperty
from glue.viewers.common.state import LayerState


class PlotlyIsosurfaceLayerState(LayerState):

    attribute = CallbackProperty()
    level_low = CallbackProperty()
    level_high = CallbackProperty()
    cmap = CallbackProperty()
    step = CallbackProperty()

    def __init__(self, layer=None, **kwargs):
        super().__init__(layer=layer)
        self.update_from_dict(**kwargs)
