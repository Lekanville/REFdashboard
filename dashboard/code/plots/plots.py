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
        title=f'Top Research Methods for Class {class_column}',
        xaxis_title='Research Method',
        yaxis_title='Count',
        xaxis=dict(type='category')
    )

    return plot


def plot_distance_vs_prediction(plot, class_name, embedding_values, prediction_values,  class_colors):
    plot.add_trace(go.Scatter(
        name=f'Class_{class_name}',
        x=embedding_values,
        y=prediction_values,
        mode='markers', # Use markers for a scatter plot
        marker=dict(color=class_colors[f'class_{class_name}']), # Assign color from the mapping
        hovertemplate='Distance: %{x}<br>Prediction Class: %{y}<br>Class: ' + str(class_name) + '<extra></extra>' # Add tooltip
    ))