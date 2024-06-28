from ..common import PlotlyBaseView
from ...common.base_3d import layout_config


__all__ = ["PlotlyBase3dView"]


class PlotlyBase3dView(PlotlyBaseView):

    def __init__(self, session, state=None):
        super(PlotlyBase3dView, self).__init__(session, state=state)

    def _create_layout_config(self):
        return layout_config(self.state, **self.LAYOUT_SETTINGS, width=1200, height=800)

    @property
    def axis_z(self):
        return self.figure.layout.zaxis

    def update_z_axislabel(self, label):
        self.axis_z.title['title'] = label

    def _update_axes_visible(self, *args):
        with self.figure.batch_update():
            super()._update_axes_visible(*args)
            self.axis_z.visible = self.state.show_axes

    def _set_z_state_bounds(self, z_range):
        with self.figure.batch_update():
            self.state.z_min = z_range[0]
            self.state.z_max = z_range[1]

