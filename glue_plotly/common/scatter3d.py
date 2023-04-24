from glue.config import settings
from glue.utils import ensure_numerical
from numpy import clip

from glue_plotly.common import rectilinear_axis


def dimensions(viewer):
    # when vispy viewer is in "native aspect ratio" mode, scale axes size by data
    if viewer.state.native_aspect:
        width = viewer.state.x_max - viewer.state.x_min
        height = viewer.state.y_max - viewer.state.y_min
        depth = viewer.state.z_max - viewer.state.z_min

    # otherwise, set all axes to be equal size
    else:
        width = 1200  # this 1200 size is arbitrary, could change to any width; just need to scale rest accordingly
        height = 1200
        depth = 1200

    return [width, height, depth]


def projection_type(viewer):
    return "perspective" if viewer.state.perspective_view else "orthographic"


def axis(viewer, ax):
    a = rectilinear_axis(viewer, ax)
    a.update(visible=viewer.state.visible_axes)
    return a


def clipped_data(viewer, layer):
    x = layer.state.layer[viewer.state.x_att]
    y = layer.state.layer[viewer.state.y_att]
    z = layer.state.layer[viewer.state.z_att]

    # Plotly doesn't show anything outside the bounding box
    viewer_state = viewer.state
    mask = (x >= viewer_state.x_min) & (x <= viewer_state.x_max) & \
              (y >= viewer_state.y_min) & (y <= viewer_state.y_max) & \
              (z >= viewer_state.z_min) & (z <= viewer_state.z_max)

    return x[mask], y[mask], z[mask], mask


def size_info(layer, mask):
    state = layer.state

    # set all points to be the same size, with set scaling
    if state.size_mode == 'Fixed':
        return state.size_scaling * state.size

    # scale size of points by set size scaling
    else:
        s = ensure_numerical(state.layer[state.size_attribute][mask].ravel())
        s = ((s - state.size_vmin) /
             (state.size_vmax - state.size_vmin))
        # The following ensures that the sizes are in the
        # range 3 to 30 before the final size scaling.
        clip(s, 0, 1, out=s)
        s *= 0.95
        s += 0.05
        s *= (30 * state.size_scaling)
        return s


def layout_config(viewer):
    width, height, depth = dimensions(viewer)
    return dict(
        margin=dict(r=50, l=50, b=50, t=50),  # noqa
        width=1200,
        paper_bgcolor=settings.BACKGROUND_COLOR,
        scene=dict(
            xaxis=axis(viewer, 'x'),
            yaxis=axis(viewer, 'y'),
            zaxis=axis(viewer, 'z'),
            camera=dict(
                projection=dict(
                    type=projection_type
                )
            ),
            aspectratio=dict(x=1 * viewer.state.x_stretch,
                             y=height / width * viewer.state.y_stretch,
                             z=depth / width * viewer.state.z_stretch),
            aspectmode='manual'
        )
    )
    