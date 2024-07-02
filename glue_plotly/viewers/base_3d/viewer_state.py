from echo import CallbackProperty
from glue_jupyter.common.state3d import ViewerState3D


class Plotly3dViewerState(ViewerState3D):
   perspective_view = CallbackProperty(True)
   show_axes = CallbackProperty(True)

   x_axislabel = CallbackProperty()
   y_axislabel = CallbackProperty()
   z_axislabel = CallbackProperty()
   
