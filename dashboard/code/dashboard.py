import os
import io
import yaml
import pandas as pd
from yaml.loader import SafeLoader
from code.authentication import reset_password
from code.plots.plots import *
from code.plots.colors import Colors
from code.tools.tools import select_data_for_uoa
from code.tools.tools import get_research_methods_for_uoa
from code.db.predictions import get_predictions_sync

import plotly
import plotly.graph_objects as px
import plotly.graph_objs as go
import numpy as np
with open('../config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)


# The data
# df = pd.read_csv('../data/Research_Output_Collection_features_predictions_and_embeddings.csv')
# df = df[df['article_type'] == "ContributionToJournal"]
# df_all_ref_2d = pd.read_csv('../data/df_sampled_ref_embeddings_2D.csv')

data_prediction, data_all_ref_embeddings_2d = get_predictions_sync()
df = pd.DataFrame(data_prediction)
df = df[df['article_type'] == "ContributionToJournal"]
df_all_ref_2d = pd.DataFrame(data_all_ref_embeddings_2d)


REFlabels = {
     "UoA1": "REF UoA1 - Clinical Medicine",
     "UoA2": "REF UoA2 - Public Health, Health Services and Primary Care",
     "UoA4": "REF UoA4 - Psychology, Psychiatry and Neuroscience",
     "UoA5": "REF UoA5 - Biological Sciences",
     "UoA6": "REF UoA6 - Agriculture, Food and Veterinary Sciences",
}

distances = [
  "distance_to_median_of_uoa_1",
  "distance_to_median_of_uoa_2",
  "distance_to_median_of_uoa_4",
  "distance_to_median_of_uoa_5",
  "distance_to_median_of_uoa_6"
]

prediction = [
  "predictions_for_uoa_1",
  "predictions_for_uoa_2",
  "predictions_for_uoa_4",
  "predictions_for_uoa_5",
  "predictions_for_uoa_6"
]

all_uoas = ["1","2","4","5","6"]

def publications_over_time(data, controller, st, UoA_selection_type):

    predictions_selector = prediction[controller]
    distance_column = distances[controller]
    current_uoa = distance_column.split("_")[-1]


    classes = sorted(data[predictions_selector].unique())
    years = sorted(data["year"].unique())
    years = [str(i) for i in years]

    # Yearly predictions
    yearly_predictions = {}
    for i in classes:
        prediction_class = []
        for j in years:
            dat_1_1 = len(data[(data['year'] <= int(j)) & (data[predictions_selector] == i)])
            prediction_class.append(dat_1_1)
        yearly_predictions[f'class_{i}'] = prediction_class

    # SJR and Altmetric scores
    all_sjr = {}
    all_alt = {}
    for i in years:
        dat_sjr = data[(data['year'] <= int(i)) & (~pd.isnull(data["SJR"]))][f"scaled_SJR_{current_uoa}"].to_list()
        dat_alt = data[(data['year'] <= int(i)) & (~pd.isnull(data["Altmetric_score"]))][f"scaled_Altmetric_score_{current_uoa}"].to_list()

        all_sjr[f'year_{i}'] = dat_sjr
        all_alt[f'year_{i}'] = dat_alt

    # Colors for classes and UoAs
    class_colors = Colors.get_class_colors()
    embedding_class_colors = Colors.get_embeddings_class_colors()
    bristol_uoa_colors = Colors.get_bristol_uoa_colors()
    ref_uoa_colors = Colors.get_ref_uoa_colors()

    # Plots for Predictions and Embeddings
    # col = st.columns(1)
    # with col[0]:
    #     st.markdown("You can zoom, pan and view fullscreen mode of each plots by clicking on the icon in the top right corner of each plot.")

    col = st.columns(1)
    with col[0]:
        # row
        st.subheader("Predictions and Embeddings")
        # st.markdown("You can zoom, pan and view fullscreen mode of each plots by clicking on the icon in the top right corner of each plot.")
        st.markdown("**Key** <br> 7 = 4+/4,   6 = 4-/3+,   5 = 3,   4 = 3-/2+,   3 = 2,   2 = 2-/1+,   1 = 1/1-", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)    
    with col1:
        # row
        plot = go.Figure()

        # Bar Plots for the yearly predictions
        for class_name in classes:
            plot = bar_plot(plot, class_name, years, yearly_predictions, class_colors)

        plot.update_layout(
            barmode='stack',
            title=f"Publications over time (Yearly)",
            xaxis_title='Year',
            yaxis_title='Number of articles',
            xaxis=dict(type='category'), # Set x-axis type to category,
            hoverlabel=dict( # Add hoverlabel styling
                bgcolor="white", # Set background color to white
                font=dict(color="black") # Set font color to black for contrast
                )
            )

        # plot.update_layout(barmode='stack')
        plot.show()
        st.plotly_chart(plot, key=f"predictions_{current_uoa}", use_container_width=True)

    with col2:
        # row
        plot = go.Figure()

        # Filter data for the current class
        for class_name in reversed(classes):
            # For data not selected for the current UoA
            data_class_others = df[df[predictions_selector] == class_name]
            uoa_selected = data["research_uuid"].to_list()
            data_class_others_final = data_class_others[~data_class_others["research_uuid"].isin(uoa_selected)]

            embedding_values=data_class_others_final[distance_column].tolist()
            prediction_values=data_class_others_final[predictions_selector].tolist()
            marker_opacity = 0.1
            plot = plot_distance_vs_prediction(plot, class_name, embedding_values, prediction_values,  embedding_class_colors, marker_opacity, case="unselected")

            # For data selected for the current UoA
            data_class_uoa = data[data[predictions_selector] == class_name]
            embedding_values_uoa = data_class_uoa[distance_column].tolist()
            prediction_values_uoa = data_class_uoa[predictions_selector].tolist()
            marker_opacity = 1.0
            plot = plot_distance_vs_prediction(plot, class_name, embedding_values_uoa, prediction_values_uoa,  class_colors, marker_opacity, case="selected")

        # Add a vertical line at x=0.7
        # plot.add_shape(
        #     type="line",
        #     x0=0.7, x1=0.7,
        #     y0=0, y1=len(classes) - 1,
        #     line=dict(color="Red", width=2, dash="dash"),
        #     xref="x", yref="y"
        # )

        plot.update_layout(
            title='UoA distance vs. Predictions (All FHLS articles)',
            xaxis_title=f'Distance to median of UoA {current_uoa}',
            yaxis_title='Prediction class',
            yaxis=dict(tickmode='array', tickvals=classes), # Ensure y-axis shows class numbers clearly
            hovermode='closest', # Improve hover behavior
            hoverlabel=dict( # Add hoverlabel styling
                bgcolor="white", # Set background color to white
                font=dict(color="black") # Set font color to black for contrast
                )
        )

        plot.show()
        st.plotly_chart(plot, key=f"distances_{current_uoa}", use_container_width=True)

    with col3:
        # row
        plot = go.Figure()
        # Embeddings for all UoAs form other universities
        # st.subheader("Comparison of article embeddings of UoB with other universities")
        for uoa in all_uoas:
            data_ref = df_all_ref_2d[df_all_ref_2d.Unit_of_assessment_number == int(uoa)]
            # Set opacity based on whether the current UoA is UoA_1
            marker_opacity = 1.0 if uoa == current_uoa else 0.3 # Set opacity to 1 for current UoA, and 0.3 for others
   
            plot.add_trace(go.Scatter(
                name=f'REF UoA {uoa}',
                x=data_ref["corpus_embeddings_x"],
                y=data_ref["corpus_embeddings_y"],
                mode='markers', # Use markers for a scatter plot
                marker=dict(
                    color=ref_uoa_colors[f'uoa_{uoa}'], # Assign color from the mapping
                    line=dict( # Add marker outline
                        color='white',
                        width=1
                    ),
                    opacity=marker_opacity # Apply the calculated opacity
                    ),
                    customdata=data_ref[['DOI', 'Institution_name', 'Title']], # Add DOI, Institution_name, and Title to customdata
                    hovertemplate= # Use text for UoA number as it's passed in the trace name
                      '<b>Institution: %{customdata[1]}</b><br><br>' +
                      'UoA %{text}<br>'+
                      'Title: %{customdata[2]}<br>' +
                      'DOI: %{customdata[0]}<br>' +
                      'x-pca: %{x}<br>' +
                      'y-pca: %{y}<extra></extra>', # Add tooltip with DOI, Institution, and Title
                      text=[str(uoa)] * len(data_ref) # Pass UoA number as text for hover template
                    ))

        # For the current UoA of University of Bristol
        plot.add_trace(go.Scatter(
            name=f'Bristol UoA {current_uoa}',
            x=data["corpus_embeddings_x"],
            y=data["corpus_embeddings_y"],
            mode='markers', # Use markers for a scatter plot
            marker=dict(color=bristol_uoa_colors[f'uoa_{current_uoa}'],
                        line=dict( # Add marker outline
                        color='white',
                        width=1
                    ),
                ),
                customdata=data[['doi', 'research_uuid', 'title', 'year']], # Add DOI, Institution_name, and Title to customdata
                hovertemplate= # Use text for UoA number as it's passed in the trace name
                            '<b>Institution: University of Bristol</b><br><br>' +
                            'UoA %{text}<br>'+
                            'Title: %{customdata[2]}<br>' +
                            'DOI: %{customdata[0]}<br>' +
                            'Year: %{customdata[3]}<br>' +
                            'x-pca: %{x}<br>' +
                            'y-pca: %{y}<extra></extra>', # Add tooltip with DOI, Institution, and Title
                            text=[str(current_uoa)] * len(data) # Pass UoA number as text for hover template
            # '<b>UoA %{text}</b><br><br>'     
            # text=[str(current_uoa)] * len(data) # Pass UoA number as text for hover template
            ))

        plot.update_layout(
            title='Article embeddings of UoB and other universities',
            xaxis_title='x-pca',
            yaxis_title='y-pca',
            yaxis=dict(tickmode='array'), # Ensure y-axis shows class numbers clearly
            hovermode='closest', # Improve hover behavior
            hoverlabel=dict( # Add hoverlabel styling
                bgcolor="white", # Set background color to white
                font=dict(color="black") # Set font color to black for contrast
                )
        )

        plot.show()
        st.plotly_chart(plot, key=f"embeddings_{current_uoa}", use_container_width=True)

    # Plots for SJR and Altmetric scores
    col = st.columns(1)
    with col[0]:
        # row
        st.subheader("SJR and Altmetric scores")
    col1, col2, col3 = st.columns(3)

    with col1:
        plot = go.Figure()
        for year in years:
            plot = plot_sjr_scores(plot, year, all_sjr)

        # Update layout for white border and titles
        plot.update_layout(
            title='Distribution of SJR Scores (Scaled) Over Time',
            xaxis_title='Year',
            yaxis_title='SJR Score',
            # paper_bgcolor='white', # Set the background color of the paper (area outside the plot) to white
            # plot_bgcolor='white',  # Set the background color of the plot area to white
            # margin=dict(l=20, r=20, t=40, b=20), # Adjust margins to create space for the border effect
            xaxis=dict(type='category'), # Ensure x-axis is treated as categories
            hoverlabel=dict( # Add hoverlabel styling
                bgcolor="white", # Set background color to white
                font=dict(color="black") # Set font color to black for contrast
            )
        )

        plot.show()
        st.plotly_chart(plot, key=f"sjr_scores_{current_uoa}", use_container_width=True)
    
    with col2:
        plot = go.Figure()
        for year in years:
            plot = plot_altmetric_scores(plot, year, all_alt)
        
        # Update layout for white border and titles
        plot.update_layout(
            title='Distribution of Altmetric Scores (Scaled) Over Time',
            xaxis_title='Year',
            yaxis_title='Altmetric Score',
            # paper_bgcolor='white', # Set the background color of the paper (area outside the plot) to white
            # plot_bgcolor='white',  # Set the background color of the plot area to white
            # margin=dict(l=20, r=20, t=40, b=20), # Adjust margins to create space for the border effect
            xaxis=dict(type='category'), # Ensure x-axis is treated as categories
            hoverlabel=dict( # Add hoverlabel styling
                bgcolor="white", # Set background color to white
                font=dict(color="black") # Set font color to black for contrast
            )
        )
        plot.show()
        st.plotly_chart(plot, key=f"altmetric_scores_{current_uoa}", use_container_width=True)

    #  For research methods
    if predictions_selector == "predictions_for_uoa_2":
        col = st.columns(1)
        with col[0]:
            # row
            st.subheader("Top research methods for each class")
            
    col1, col2, col3 = st.columns(3)
    with col1:
        # row
        # Plotting top research methods for each class
        if predictions_selector == "predictions_for_uoa_2":
            class_columns = [7, 4]
            for class_column in class_columns:
                methods, scores = get_research_methods_for_uoa(data, class_column, predictions_selector)
                plot = go.Figure()
                plot = plot_research_methods(plot, class_column, methods, scores, class_colors)
                st.plotly_chart(plot, key=f"class_{class_column}_{current_uoa}", use_container_width=True)

    with col2:
        # row
        # Plotting top research methods for each class
        if predictions_selector == "predictions_for_uoa_2":
            class_columns = [6]
            for class_column in class_columns:
                methods, scores = get_research_methods_for_uoa(data, class_column, predictions_selector)
                plot = go.Figure()
                plot = plot_research_methods(plot, class_column, methods, scores, class_colors)
                st.plotly_chart(plot, key=f"class_{class_column}_{current_uoa}", use_container_width=True)

    with col3:
        # row
        # Plotting top research methods for each class
        if predictions_selector == "predictions_for_uoa_2":
            class_columns = [5]
            for class_column in class_columns:
                methods, scores = get_research_methods_for_uoa(data, class_column, predictions_selector)
                plot = go.Figure()
                plot = plot_research_methods(plot, class_column, methods, scores, class_colors)
                st.plotly_chart(plot, key=f"class_{class_columns}_{current_uoa}", use_container_width=True)


    # Download predictions
    col = st.columns(1)
    with col[0]:
        # row
        st.subheader("Download predictions")
    col1, col2, col3 = st.columns(3)

    with col1:
        # row
        # Add a selectbox to choose a class for download
        selected_class = st.selectbox(
            f"Select a Prediction Class from UoA {current_uoa} to Download",
            ["All Classes"] + classes # Add "All Classes" option
        )

        # Filter data based on selected class
        if selected_class == "All Classes":
            df_download = data[['research_uuid','title','article_type','year','doi', predictions_selector]].copy()
            class_label = "All_Classes"
        else:
            df_download = data[data[predictions_selector] == selected_class][['research_uuid','title','article_type','year','doi', predictions_selector]].copy()
            class_label = str(selected_class)

        # Add a download button
        if not df_download.empty:
            csv_buffer = io.StringIO()
            df_download.to_csv(csv_buffer, index=False)
            st.download_button(
                label=f"Download Predictions for UoA {current_uoa} ({UoA_selection_type}) - Class {selected_class}",
                data=csv_buffer.getvalue(),
                file_name=f"UoA_{current_uoa}_{UoA_selection_type}_class_{class_label}_data.csv",
                mime="text/csv"
            )
        else:
            st.info(f"No data to download for UoA {current_uoa} - Class {selected_class}.")



def render_dashboard(session_state, authenticator, st):
    st.sidebar.write(f'Logged in as *{session_state["name"]}*')
    st.sidebar.button('Change password', on_click=reset_password, args=(st,), type="primary")
    authenticator.logout('Logout', 'sidebar')
    uoas = list(config["credentials"]["usernames"][st.session_state["username"]]["uoas"]) 
    admin = config["credentials"]["usernames"][st.session_state["username"]]["admin"]
    if admin == True:
        uoas.append("admin")
    tabs = st.tabs(uoas)
    uoa_controller = 0
    for tab in tabs:
        with tab:
            if admin == True and uoas[uoa_controller] == "admin":
                st.header("Admin", divider="red")
                for user in list(config["credentials"]["usernames"]):
                    st.markdown(f"**User:** {user}")
                    userconfig = config["credentials"]["usernames"][user]
                    #useruoas = st.data_editor(config["credentials"]["usernames"][user]["uoas"], key=user+"uoas", num_rows="dynamic")
                    useradmin = st.toggle("Admin", value=config["credentials"]["usernames"][user]["admin"], key=user+"admin", label_visibility="visible")
                    # ===========
                    useruoas2 = {"UoA1": False, "UoA2": False, "UoA4": False, "UoA5": False, "UoA6": False, } 
                    for uoa in config["credentials"]["usernames"][user]["uoas"]:
                        useruoas2[uoa] = True
                    columns = st.columns(5)
                    colcounter = 0
                    for uoa in useruoas2.keys():
                        with columns[colcounter]:
                            useruoas2[uoa] = st.toggle(uoa, value=useruoas2[uoa], key=user+uoa, label_visibility="visible")
                        colcounter += 1
                    useruoas = [val for val in useruoas2.keys() if useruoas2[val] == True]
                    # ===========
                    config["credentials"]["usernames"][user] = {'admin': useradmin, 
                                                                'email': userconfig['email'], 
                                                                'failed_login_attempts': userconfig['failed_login_attempts'], 
                                                                'logged_in': userconfig['logged_in'], 
                                                                'name': userconfig['name'], 
                                                                'password': userconfig['password'], 
                                                                'uoas': useruoas} 
                    st.divider()

                with open('../config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
            else: 
                # Tab content for each UoA
                st.header(REFlabels[uoas[uoa_controller]], divider="red")
                col_1, col_2 = st.columns(2)

                with col_2:
                    UoA_selection_type = st.selectbox("Choose how UoA data is selected",
                                                          ("Embedding distance less than 0.7", "Minimum embedding distance"),
                                                        key =f"select_{uoas[uoa_controller]}"
                                                        )
                    
                REFdata = select_data_for_uoa(df, UoA_selection_type, distances)

                with col_1:
                    # row
                    st.markdown("You can select the UoA data based on either embedding distance of less than 0.7 or minimum embedding distance. " \
                    "The data is filtered based on the selected method and then visualized.")
                    st.markdown(f'**The current selection is "{UoA_selection_type}" with {len(REFdata[uoas[uoa_controller]])} articles.**')

                # with col_2:
                #     # row
                #     st.markdown(f'**The current selection is "{UoA_selection_type}" with {len(REFdata[uoas[uoa_controller]])} articles.**')

                publications_over_time(REFdata[uoas[uoa_controller]], uoa_controller, st, UoA_selection_type)
                uoa_controller += 1            