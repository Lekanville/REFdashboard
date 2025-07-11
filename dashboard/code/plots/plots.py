import plotly.graph_objs as go


def bar_plot(plot, class_name, years, yearly_predictions, class_colors):
    plot.add_trace(go.Bar(
        name=f'Class_{class_name}',
        x=years[:-1],
        y=yearly_predictions[f'class_{class_name}'][:-1],
        marker=dict(color=class_colors[f'class_{class_name}']), # Assign color from the mapping
        hovertemplate='Year: %{x}<br>Count: %{y}<br>Class: ' + str(class_name) + '<extra></extra>' # Add tooltip
    ))
    plot.add_trace(go.Bar(
        name=f'Class_{class_name}',
        x=years[-1:],
        y=yearly_predictions[f'class_{class_name}'][-1:],
        marker=dict(color=class_colors[f'class_{class_name}']), # Assign color from the mapping
        opacity=0.5,
        hovertemplate='Year: %{x}<br>Count: %{y}<br>Class: ' + str(class_name) + '<extra></extra>', # Add tooltip
        showlegend=False # Hide this trace from the legend
    ))

    return plot


def plot_research_methods(plot, class_column, methods, scores, class_colors):
    plot.add_trace(go.Bar(
        name=f'Class_{class_column}',
        x=methods,
        y=scores,
        marker=dict(color=class_colors[f'class_{class_column}']), # Assign color from the mapping
        hovertemplate='Method: %{x}<br>Count: %{y}<br>Class: ' + str(class_column) + '<extra></extra>' # Use i instead of class_name
    ))

    plot.update_layout(
        title=f'Top research methods for class {class_column}',
        xaxis_title='Research Method',
        yaxis_title='Count',
        xaxis=dict(type='category'),
        hoverlabel=dict( # Add hoverlabel styling
            bgcolor="white", # Set background color to white
            font=dict(color="black") # Set font color to black for contrast
            )
    )

    return plot


def plot_distance_vs_prediction(plot, class_name, embedding_values, prediction_values,  class_colors, marker_opacity, case):
    plot.add_trace(go.Scatter(
        name=f'Class_{class_name}_{case}', # Use case to differentiate traces
        x=embedding_values,
        y=prediction_values,
        mode='markers', # Use markers for a scatter plot
        marker=dict(color=class_colors[f'class_{class_name}'], opacity=marker_opacity), # Assign color from the mapping
        hovertemplate='Distance: %{x}<br>Prediction Class: %{y}<br>Class: ' + str(class_name) + '<extra></extra>' # Add tooltip
    ))
    return plot


def plot_sjr_scores(plot, year, all_sjr):
    sjr_scores = all_sjr.get(f'year_{year}', []) # Get SJR scores for the year, default to empty list
    if sjr_scores: # Only add if there are scores for the year
        plot.add_trace(go.Box(
            y=sjr_scores,
            name=str(year),
            boxpoints='outliers', # Show outlier points
            # jitter=0.3, # Add jitter to outlier points
            # Removed pointpos parameter to plot outliers with their boxes
        ))
    return plot


def plot_altmetric_scores(plot, year, all_alt):
    altmetric_scores = all_alt.get(f'year_{year}', []) # Get Altmetric scores for the year, default to empty list
    if altmetric_scores: # Only add if there are scores for the year
        plot.add_trace(go.Box(
            y=altmetric_scores,
            name=str(year),
            boxpoints='outliers', # Show outlier points
            # jitter=0.3, # Add jitter to outlier points
            # Removed pointpos parameter to plot outliers with their boxes
        ))
    return plot