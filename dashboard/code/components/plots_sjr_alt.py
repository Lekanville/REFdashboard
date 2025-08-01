import plotly.graph_objs as go
from code.plots.colors import Colors
from code.plots.plots import plot_research_methods, plot_sjr_scores, plot_altmetric_scores


class_colors = Colors.get_class_colors()
embedding_class_colors = Colors.get_embeddings_class_colors()
bristol_uoa_colors = Colors.get_bristol_uoa_colors()
ref_uoa_colors = Colors.get_ref_uoa_colors()

def plot_sjr_scores_over_time(years, all_sjr):
    plot = go.Figure()
    for year in years:
        plot = plot_sjr_scores(plot, year, all_sjr)

    plot.update_layout(
        title='Distribution of SJR Scores (Scaled) Over Time',
        xaxis_title='Year',
        yaxis_title='SJR Score',
        xaxis=dict(type='category'),
        hoverlabel=dict(
            bgcolor="white",
            font=dict(color="black")
        )
    )
    return plot

def plot_altmetric_scores_over_time(years, all_alt):
    plot = go.Figure()
    for year in years:
        plot = plot_altmetric_scores(plot, year, all_alt)
    plot.update_layout(
        title='Distribution of Altmetric Scores (Scaled) Over Time',
        xaxis_title='Year',
        yaxis_title='Altmetric Score',
        xaxis=dict(type='category'),
        hoverlabel=dict(
            bgcolor="white",
            font=dict(color="black")
        )
    )
    return plot
