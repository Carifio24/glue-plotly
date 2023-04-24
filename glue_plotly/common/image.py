from glue.viewers.image.state import ImageLayerState, ImageSubsetLayerState
from glue.viewers.scatter.state import ScatterLayerState

from glue_plotly.common import base_layout_config, layers_to_export


def slice_to_bound(slc, size):
    min, max, step = slc.indices(size)
    n = (max - min - 1) // step
    max = min + step * n
    return min, max, n + 1


def background_color(viewer):
    using_colormaps = viewer.state.color_mode == 'Colormaps'
    bg_color = [256, 256, 256, 1] if using_colormaps else [0, 0, 0, 1]
    return bg_color


def layout_config(viewer):
    bg_color = background_color(viewer)
    return base_layout_config(viewer,
                              plot_bgcolor='rgba{0}'.format(tuple(bg_color)),
                              showlegend=True)


def layers_by_type(viewer):
    layers = sorted(layers_to_export(viewer), key=lambda lyr: lyr.zorder)
    scatter_layers, image_layers, image_subset_layers = [], [], []
    for layer in layers:
        if isinstance(layer.state, ImageLayerState):
            image_layers.append(layer)
        elif isinstance(layer.state, ImageSubsetLayerState):
            image_subset_layers.append(layer)
        elif isinstance(layer.state, ScatterLayerState):
            scatter_layers.append(layer)

    return dict(scatter=scatter_layers, image=image_layers, image_subset=image_subset_layers)


def traces(viewer):
    pass