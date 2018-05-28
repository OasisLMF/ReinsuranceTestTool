import qgrid

def show_df(df):
    grid_options = {'forceFitColumns': False}
    qgrid_widget = qgrid.QgridWidget(
        df=df, grid_options=grid_options, show_toolbar=True)
    return qgrid_widget