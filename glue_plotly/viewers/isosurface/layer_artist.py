from glue.viewers.common.layer_artist import LayerArtist
from glue_plotly.common.volume import traces_for_layer
from glue_plotly.viewers.isosurface.layer_state import PlotlyIsosurfaceLayerState


VISUAL_PROPERTIES = {'alpha', 'visible'}


class PlotlyIsosurfaceLayerArtist(LayerArtist):

    _layer_state_cls = PlotlyIsosurfaceLayerState

    def __init__(self, view, viewer_state, layer_state=None, layer=None):
        super().__init__(
            viewer_state,
            layer_state=layer_state,
            layer=layer
        )

        self._viewer_state.add_global_callback(self._update_display)
        self.state.add_global_callback(self._update_display)
        self.state.add_callback("zorder", self._update_zorder)
        self.view = view

        surface = self._create_surface()
        self._volume_id = surface.meta if surface else None
        self.view.figure.add_trace(surface)
        

    def _create_surface(self):
        # TODO: Use 256 as the resolution for now
        resolution = 128
        bounds = [
            (self._viewer_state.z_min, self._viewer_state.z_max, resolution),
            (self._viewer_state.y_min, self._viewer_state.y_max, resolution),
            (self._viewer_state.x_min, self._viewer_state.x_max, resolution)
        ]
        # isosurface_count = int(self.state.level_high - self.state.level_low)
        isosurface_count = 5
        traces = traces_for_layer(self._viewer_state,
                                  self.state,
                                  bounds=bounds,
                                  isosurface_count=isosurface_count,
                                  reference_data=self.layer,
                                  add_data_label=True)
        return traces[0]

    def _get_surface(self):
        return next(self.view.figure.select_traces(dict(meta=self._volume_id)))

    def traces(self):
        return [self._get_surface()]

    def _update_zorder(self, *args):
        current_traces = self.view.figure.data
        traces = [self.view.selection_layer]
        for layer in self.view.layers:
            traces += list(layer.traces())
        self.view.figure.data = traces + [t for t in current_traces if t not in traces]

    def _update_visual_attributes(self, changed, force=False):
        if not self.enabled:
            return

        surface = self._get_surface()
        update = {}
        if "alpha" in changed:
            update["opacity"] = self.state.alpha
        if "visible" in changed:
            update["visible"] = self.state.visible

        if update:
            surface.update(**update)

    def _update_display(self, force=False, **kwargs):
        changed = self.pop_changed_properties()

        if 'layout_update' in kwargs:
            self.view._clear_traces()
            surface = self._create_surface()
            self.view.figure.add_trace(surface)
            force = True

        if force or len(changed & VISUAL_PROPERTIES) > 0:
            self._update_visual_attributes(changed, force=force)

    def update(self):
        self._update_display(force=True)



        
