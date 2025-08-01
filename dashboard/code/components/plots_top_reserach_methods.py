import plotly.graph_objs as go
from code.plots.colors import Colors
from code.tools.tools import get_research_methods_for_uoa
from code.plots.plots import plot_research_methods


class_colors = Colors.get_class_colors()

def plot_top_research_methods(data, 
                              predictions_selector, 
                              class_columns,
                              current_uoa, st, 
                              key_prefix="class"):
    for class_column in class_columns:
        methods, scores = get_research_methods_for_uoa(data, class_column, predictions_selector)
        plot = go.Figure()
        plot = plot_research_methods(plot, class_column, methods, scores, class_colors)
        st.plotly_chart(plot, key=f"{key_prefix}_{class_column}_{current_uoa}", use_container_width=True)