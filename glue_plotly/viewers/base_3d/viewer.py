from ..common import PlotlyBaseView
from ...common.base_3d import layout_config


__all__ = ["PlotlyBase3dView"]


class PlotlyBase3dView(PlotlyBaseView):

    def __init__(self, session, state=None):
        super(PlotlyBase3dView, self).__init__(session, state=state)
        self.state.add_callback('z_min', self._update_plotly_z_limits)
        self.state.add_callback('z_max', self._update_plotly_z_limits)
        self.axis_z.on_change(lambda _obj, z_range: self._set_z_state_bounds(z_range), 'range')

    def _create_layout_config(self):
        return layout_config(self.state, **self.LAYOUT_SETTINGS, width=1200, height=800)

    @property
    def axis_x(self):
        return self.figure.layout.scene.xaxis

    @property
    def axis_y(self):
        return self.figure.layout.scene.yaxis

    @property
    def axis_z(self):
        return self.figure.layout.scene.zaxis

    def _update_plotly_z_limits(self, *args):
        with self.figure.batch_update():
            if self.state.z_min is not None and self.state.z_max is not None:
                self.axis_z['range'] = [self.state.z_min, self.state.z_max]

    def update_z_axislabel(self, label):
        self.axis_z.title['title'] = label

    def _update_axes_visible(self, *args):
        with self.figure.batch_update():
            super()._update_axes_visible(*args)
            # self.axis_z.visible = self.state.show_axes

    def _set_z_state_bounds(self, z_range):
        with self.figure.batch_update():
            self.state.z_min = z_range[0]
            self.state.z_max = z_range[1]

