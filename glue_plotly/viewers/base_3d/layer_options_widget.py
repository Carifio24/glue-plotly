from ipywidgets import VBox


class Plotly3dLayerStateWidget(VBox):

    def __init__(self, layer_state):
        self.state = layer_state
        super().__init__([])
