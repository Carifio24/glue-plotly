from mock import patch

from glue_jupyter import jglue


class TestBqplotExporter:

    viewer_type = None
    tool_id = None

    def setup_method(self, method):
        self.data = self.make_data()
        self.app = jglue()
        self.app.session.data_collection.append(self.data)
        self.viewer = self.app.new_data_viewer(self.viewer_type)
        self.viewer.add_data(self.data)
        self.tool = self.viewer.toolbar.tools[self.tool_id]

    def teardown_method(self, method):
        self.viewer = None
        self.app = None

    def export_figure(self, tmpdir, output_filename):
        output_path = tmpdir.join(output_filename).strpath
        with patch('tkinter.filedialog.asksaveasfilename') as fd:
            fd.return_value = output_path
            self.tool.activate()
        return output_path
