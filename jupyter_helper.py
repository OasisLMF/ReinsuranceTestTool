import qgrid
import io
from IPython.display import display
import fileupload
import os

def show_df(df):
    grid_options = {
        'fullWidthRows': True,
        'syncColumnCellResize': True,
        'forceFitColumns': False,
        'defaultColumnWidth': 150,
        'rowHeight': 28,
        'enableColumnReorder': False,
        'enableTextSelectionOnCells': True,
        'editable': True,
        'autoEdit': True,
        'explicitInitialization': True,
        'maxVisibleRows': 15,
        'minVisibleRows': 8,
        'sortable': True,
        'filterable': True,
        'highlightSelectedCell': False,
        'highlightSelectedRow': True
    }
    qgrid_widget = qgrid.QgridWidget(
        df=df, grid_options=grid_options, show_toolbar=True)
    return qgrid_widget


def file_uploader(upload_dir='examples/uploaded', button_label='Upload .CSV file'):
    _upload_widget = fileupload.FileUploadWidget(label=button_label)
    if not os.path.exists(upload_dir):                                                                                                                                                                                                                                                                  
        os.makedirs(upload_dir)

    def _cb(change):
        decoded = io.StringIO(change['owner'].data.decode('utf-8'))
        filename = change['owner'].filename
        fpath = os.path.join(upload_dir,filename) 
        print('Uploaded `{}` ({:.2f} kB)'.format(
            fpath, len(decoded.read()) / 2 **10))
        with io.open(fpath, 'w') as fd:
            fd.write(decoded.getvalue())
            decoded.close()

    _upload_widget.observe(_cb, names='data')
    display(_upload_widget)

