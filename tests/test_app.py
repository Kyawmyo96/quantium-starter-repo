from dash import dcc, html

from app import app


def _walk_components(component):
    yield component
    children = getattr(component, "children", None)

    if children is None:
        return

    if isinstance(children, (list, tuple)):
        for child in children:
            yield from _walk_components(child)
    else:
        yield from _walk_components(children)


def test_header_is_present():
    headers = [
        component
        for component in _walk_components(app.layout)
        if isinstance(component, html.H1)
    ]
    assert any(
        header.children == "Soul Foods Pink Morsel Sales Visualiser" for header in headers
    )


def test_visualisation_is_present():
    graphs = [
        component
        for component in _walk_components(app.layout)
        if isinstance(component, dcc.Graph) and getattr(component, "id", None) == "sales-chart"
    ]
    assert len(graphs) == 1


def test_region_picker_is_present():
    radio_pickers = [
        component
        for component in _walk_components(app.layout)
        if isinstance(component, dcc.RadioItems)
        and getattr(component, "id", None) == "region-filter"
    ]
    assert len(radio_pickers) == 1
