import plotly.graph_objs as go
from code.plots.colors import Colors
from code.plots.plots import bar_plot, plot_distance_vs_prediction


class_colors = Colors.get_class_colors()
embedding_class_colors = Colors.get_embeddings_class_colors()
bristol_uoa_colors = Colors.get_bristol_uoa_colors()
ref_uoa_colors = Colors.get_ref_uoa_colors()

def plot_publications_over_time_bar(classes, years, yearly_predictions):
    plot = go.Figure()
    for class_name in classes:
        plot = bar_plot(plot, class_name, years, yearly_predictions, class_colors)

    plot.update_layout(
        barmode='stack',
        title=f"Publications over time (Yearly)",
        xaxis_title='Year',
        yaxis_title='Number of articles',
        xaxis=dict(type='category'),  # Set x-axis type to category
        hoverlabel=dict(
            bgcolor="white",  # Set background color to white
            font=dict(color="black")  # Set font color to black for contrast
        )
    )
    return plot


def plot_distance_vs_prediction_for_uoa(
    df,
    data,
    classes,
    predictions_selector,
    distance_column,
    current_uoa
):
    plot = go.Figure()
    for class_name in reversed(classes):
        # For data not selected for the current UoA
        data_class_others = df[df[predictions_selector] == class_name]
        uoa_selected = data["research_uuid"].to_list()
        data_class_others_final = data_class_others[~data_class_others["research_uuid"].isin(uoa_selected)]

        embedding_values = data_class_others_final[distance_column].tolist()
        prediction_values = data_class_others_final[predictions_selector].tolist()
        marker_opacity = 0.1
        plot = plot_distance_vs_prediction(
            plot, class_name, embedding_values, prediction_values,
            embedding_class_colors, marker_opacity, case="unselected"
        )

        # For data selected for the current UoA
        data_class_uoa = data[data[predictions_selector] == class_name]
        embedding_values_uoa = data_class_uoa[distance_column].tolist()
        prediction_values_uoa = data_class_uoa[predictions_selector].tolist()
        marker_opacity = 1.0
        plot = plot_distance_vs_prediction(
            plot, class_name, embedding_values_uoa, prediction_values_uoa,
            class_colors, marker_opacity, case="selected"
        )

    plot.update_layout(
        title='UoA distance vs. Predictions (All FHLS articles)',
        xaxis_title=f'Distance to median of UoA {current_uoa}',
        yaxis_title='Prediction class',
        yaxis=dict(tickmode='array', tickvals=classes),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white",
            font=dict(color="black")
        )
    )
    return plot


def plot_embeddings_for_uoas(
    all_uoas,
    df_all_ref_2d,
    data,
    current_uoa
):
    plot = go.Figure()
    # Plot REF UoAs
    for uoa in all_uoas:
        data_ref = df_all_ref_2d[df_all_ref_2d.Unit_of_assessment_number == int(uoa)]
        marker_opacity = 1.0 if uoa == current_uoa else 0.1
        plot.add_trace(go.Scatter(
            name=f'REF UoA {uoa}',
            x=data_ref["corpus_embeddings_x"],
            y=data_ref["corpus_embeddings_y"],
            mode='markers',
            marker=dict(
                color=ref_uoa_colors[f'uoa_{uoa}'],
                line=dict(color='white', width=1),
                opacity=marker_opacity
            ),
            customdata=data_ref[['DOI', 'Institution_name', 'Title']],
            hovertemplate=(
                '<b>Institution: %{customdata[1]}</b><br><br>' +
                'UoA %{text}<br>' +
                'Title: %{customdata[2]}<br>' +
                'DOI: %{customdata[0]}<br>' +
                'x-pca: %{x}<br>' +
                'y-pca: %{y}<extra></extra>'
            ),
            text=[str(uoa)] * len(data_ref)
        ))

    # Plot Bristol UoA
    # plot.add_trace(go.Scatter(
    #     name=f'Bristol UoA {current_uoa}',
    #     x=data["corpus_embeddings_x"],
    #     y=data["corpus_embeddings_y"],
    #     mode='markers',
    #     marker=dict(
    #         color=bristol_uoa_colors[f'uoa_{current_uoa}'],
    #         line=dict(color='white', width=1),
    #     ),
    #     customdata=data[['doi', 'research_uuid', 'title', 'year']],
    #     hovertemplate=(
    #         '<b>Institution: University of Bristol</b><br><br>' +
    #         'UoA %{text}<br>' +
    #         'Title: %{customdata[2]}<br>' +
    #         'DOI: %{customdata[0]}<br>' +
    #         'Year: %{customdata[3]}<br>' +
    #         'x-pca: %{x}<br>' +
    #         'y-pca: %{y}<extra></extra>'
    #     ),
    #     text=[str(current_uoa)] * len(data)
    # ))

    plot.add_trace(go.Scatter(
        name=f'Bristol UoA {current_uoa}',
        x=data["corpus_embeddings_x"],
        y=data["corpus_embeddings_y"],
        mode='markers',
        marker=dict(
            color='white',  # White fill
            line=dict(color=bristol_uoa_colors[f'uoa_{current_uoa}'], width=2),  # Colored edge
            symbol='cross',  # "+" marker
            size=7  # Adjust size as needed
        ),
        customdata=data[['doi', 'research_uuid', 'title', 'year']],
        hovertemplate=(
            '<b>Institution: University of Bristol</b><br><br>' +
            'UoA %{text}<br>' +
            'Title: %{customdata[2]}<br>' +
            'DOI: %{customdata[0]}<br>' +
            'Year: %{customdata[3]}<br>' +
            'x-pca: %{x}<br>' +
            'y-pca: %{y}<extra></extra>'
        ),
        text=[str(current_uoa)] * len(data)
    ))

    plot.update_layout(
        title='Article embeddings of UoB and other universities',
        xaxis_title='x-pca',
        yaxis_title='y-pca',
        yaxis=dict(tickmode='array'),
        hovermode='closest',
        hoverlabel=dict(
            bgcolor="white",
            font=dict(color="black")
        )
    )
    return plot