from ipywidgets import VBox


class Plotly3dViewerStateWidget(VBox):

    def __init__(self, viewer_state):
        self.state = viewer_state
        super().__init__([])
        
