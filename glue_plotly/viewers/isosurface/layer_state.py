from echo import CallbackProperty, SelectionCallbackProperty, delay_callback, keep_in_sync
from glue.core.data_combo_helper import ComponentIDComboHelper
from glue.core.state_objects import StateAttributeLimitsHelper
from glue.viewers.common.state import LayerState


class PlotlyIsosurfaceLayerState(LayerState):

    attribute = SelectionCallbackProperty()
    level_low = CallbackProperty()
    level_high = CallbackProperty()
    cmap = CallbackProperty()
    step = CallbackProperty()
    color = CallbackProperty()
    alpha = CallbackProperty()

    def __init__(self, layer=None, viewer_state=None, **kwargs):
        super().__init__(viewer_state=viewer_state, layer=layer)

        self._sync_color = None
        self._sync_alpha = None

        self.att_helper = ComponentIDComboHelper(self, 'attribute')

        self.lim_helper = StateAttributeLimitsHelper(self, attribute='attribute',
                                                     lower='level_low', upper='level_high')

        self.add_callback('layer', self._on_layer_change)
        if layer is not None:
            self._on_layer_change()

        self.update_from_dict(kwargs)

    def _on_layer_change(self, layer=None):

        if self._sync_color is not None:
            self._sync_color.stop_syncing()

        if self._sync_alpha is not None:
            self._sync_alpha.stop_syncing()

        if self.layer is not None:
            self.color = self.layer.style.color
            self.alpha = self.layer.style.alpha

            self._sync_color = keep_in_sync(self, 'color', self.layer.style, 'color')
            self._sync_alpha = keep_in_sync(self, 'alpha', self.layer.style, 'alpha')

        with delay_callback(self, 'level_low', 'level_high'):

            if self.layer is None:
                self.att_helper.set_multiple_data([])
            else:
                self.att_helper.set_multiple_data([self.layer])
