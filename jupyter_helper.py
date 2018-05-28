import qgrid

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