from code.authentication import reset_password
import pandas as pd
import yaml
from yaml.loader import SafeLoader
from code.plots.plots import bar_plot

import plotly
import plotly.graph_objects as px
import plotly.graph_objs as go
import numpy as np
with open('../config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

REFlabels = {
     "UoA1": "REF UoA1 - Clinical Medicine",
     "UoA2": "REF UoA2 - Public Health, Health Services and Primary Care",
     "UoA4": "REF UoA4 - Psychology, Psychiatry and Neuroscience",
     "UoA5": "REF UoA5 - Biological Sciences",
     "UoA6": "REF UoA6 - Agriculture, Food and Veterinary Sciences",
}


df = pd.read_csv('../data/Research_Output_Collection_features_predictions_and_embeddings.csv')
df = df[df['article_type'] == "ContributionToJournal"]

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

REFdata = {}

for i,j in enumerate(distances):
  df_uoa = df[df[j] < 0.7][["research_uuid", "year", "main_research_method", distances[i], prediction[i]]]
  uoa = j.split("_")[-1]
  REFdata[f'UoA{uoa}'] = df_uoa

# REFdata = {
#      "UoA1": pd.DataFrame({'Date':[1,2,3,4,5,6,7,8,9,10],'Publications':[2,4,2,1,3,3,4,6,7,8]}),
#      "UoA2": pd.DataFrame({'Date':[1,2,3,4,5,6,7,8,9,10],'Publications':[4,4,2,1,1,1,5,9,7,12]}),
#      "UoA4": pd.DataFrame({'Date':[1,2,3,4,5,6,7,8,9,10],'Publications':[1,1,1,1,3,5,2,6,9,8]}),
#      "UoA5": pd.DataFrame({'Date':[1,2,3,4,5,6,7,8,9,10],'Publications':[2,5,2,0,1,1,4,6,4,2]}),
#      "UoA6": pd.DataFrame({'Date':[1,2,3,4,5,6,7,8,9,10],'Publications':[5,5,2,4,3,5,7,9,7,5]}),
# }


def publications_over_time(data, predictions_selector, st):
    st.subheader("Publications over time")
    col1, col2, col3 = st.columns(3)    

    classes = np.sort(data[predictions_selector].unique()).tolist()
    years = np.sort(data["year"].unique())
    years = [str(i) for i in years]

    yearly_predictions = {}
    for i in classes:
        prediction_class = []
        for j in years:
            dat_1_1 = len(data[(data['year'] <= int(j)) & (data[predictions_selector] == i)])
            prediction_class.append(dat_1_1)
        yearly_predictions[f'class_{i}'] = prediction_class


    with col1:
        plot = go.Figure()

        colors = plotly.colors.qualitative.Plotly # Using a qualitative color scale
        class_colors = {f'class_{cls}': colors[i % len(colors)] for i, cls in enumerate(classes)} # Create color mapping

        # Bar Plots for the yearly predictions
        for class_name in classes:
            plot = bar_plot(plot, class_name, years, yearly_predictions, class_colors)

        plot.update_layout(
            title='Yearly Predictions for ',
            xaxis_title='Year',
            yaxis_title='Number of articles',
            xaxis=dict(type='category') # Set x-axis type to category
        )

        plot.update_layout(barmode='stack')
        plot.show()
        # plot = go.Figure(data=[
        #     go.Bar(
        #         name=f'Class_{k}',
        #         x=years,
        #         y=yearly_predictions[f'class_{k}']
        #     ) for k in classes
        # ])
        # plot.update_layout(barmode='stack')
        # plot.show()
        st.plotly_chart(plot, use_container_width=True)

        # Plotting top research methods for each class
        if predictions_selector == "predictions_for_uoa_2":
            class_column = [7, 4]
            for i in class_column:
                data_class = data[data[predictions_selector] == i]
                class_methods = data_class['main_research_method'].value_counts().head(6).to_dict()

                methods = []
                scores = []
                for k, v in class_methods.items():
                    methods.append(k)
                    scores.append(v)

                plot = go.Figure()

                colors = plotly.colors.qualitative.Plotly # Using a qualitative color scale
                class_colors = {f'class_{cls}': colors[idx % len(colors)] for idx, cls in enumerate(classes)} # Create color mapping

                plot.add_trace(go.Bar(
                    name=f'Class_{i}',
                    x=methods,
                    y=scores,
                    marker=dict(color=class_colors[f'class_{i}']), # Assign color from the mapping
                    hovertemplate='Method: %{x}<br>Count: %{y}<br>Class: ' + str(i) + '<extra></extra>' # Use i instead of class_name
                ))

                plot.update_layout(
                    title=f'Top Research Methods for Class {i}',
                    xaxis_title='Research Method',
                    yaxis_title='Count',
                    xaxis=dict(type='category')
                )

                st.plotly_chart(plot, use_container_width=True)

    with col2:
        plot = go.Figure()

        colors = plotly.colors.qualitative.Plotly # Using a qualitative color scale
        class_colors = {f'class_{cls}': colors[i % len(colors)] for i, cls in enumerate(classes)} # Create color mapping

        for class_name in reversed(classes):
            plot.add_trace(go.Scatter(
                name=f'Class_{class_name}',
                x=years,
                y=yearly_predictions[f'class_{class_name}'],
                mode='lines',
                line=dict(color=class_colors[f'class_{class_name}']), # Assign color from the mapping
                hovertemplate='Year: %{x}<br>Count: %{y}<br>Class: ' + str(class_name) + '<extra></extra>' # Add tooltip
            ))

        plot.update_layout(
            title='Yearly Predictions by Class',
            xaxis_title='Year',
            yaxis_title='Number of articles',
            xaxis=dict(type='category') # Set x-axis type to category
        )

        plot.show()
        st.plotly_chart(plot, use_container_width=True)

        # Plotting top research methods for each class
        if predictions_selector == "predictions_for_uoa_2":
            class_column = [6]
            for i in class_column:
                data_class = data[data[predictions_selector] == i]
                class_methods = data_class['main_research_method'].value_counts().head(6).to_dict()

                methods = []
                scores = []
                for k, v in class_methods.items():
                    methods.append(k)
                    scores.append(v)

                plot = go.Figure()

                colors = plotly.colors.qualitative.Plotly # Using a qualitative color scale
                class_colors = {f'class_{cls}': colors[idx % len(colors)] for idx, cls in enumerate(classes)} # Create color mapping

                plot.add_trace(go.Bar(
                    name=f'Class_{i}',
                    x=methods,
                    y=scores,
                    marker=dict(color=class_colors[f'class_{i}']), # Assign color from the mapping
                    hovertemplate='Method: %{x}<br>Count: %{y}<br>Class: ' + str(i) + '<extra></extra>' # Use i instead of class_name
                ))

                plot.update_layout(
                    title=f'Top Research Methods for Class {i}',
                    xaxis_title='Research Method',
                    yaxis_title='Count',
                    xaxis=dict(type='category')
                )

                st.plotly_chart(plot, use_container_width=True)

    with col3:
        plot = go.Figure()

        colors = plotly.colors.qualitative.Plotly # Using a qualitative color scale
        class_colors = {f'class_{cls}': colors[i % len(colors)] for i, cls in enumerate(classes)} # Create color mapping

        for class_name in classes:
            plot.add_trace(go.Scatter(
                name=f'Class_{class_name}',
                x=years,
                y=yearly_predictions[f'class_{class_name}'],
                mode='lines',
                stackgroup='one', # Stack lines
                line=dict(color=class_colors[f'class_{class_name}']), # Assign color from the mapping
                hovertemplate='Year: %{x}<br>Count: %{y}<br>Class: ' + str(class_name) + '<extra></extra>' # Add tooltip
            ))

        plot.update_layout(
            title='Yearly Predictions by Class',
            xaxis_title='Year',
            yaxis_title='Number of articles',
            xaxis=dict(type='category') # Set x-axis type to category
        )

        plot.show()
        st.plotly_chart(plot, use_container_width=True)


        # Plotting top research methods for each class
        if predictions_selector == "predictions_for_uoa_2":
            class_column = [5]
            for i in class_column:
                data_class = data[data[predictions_selector] == i]
                class_methods = data_class['main_research_method'].value_counts().head(6).to_dict()

                methods = []
                scores = []
                for k, v in class_methods.items():
                    methods.append(k)
                    scores.append(v)

                plot = go.Figure()

                colors = plotly.colors.qualitative.Plotly # Using a qualitative color scale
                class_colors = {f'class_{cls}': colors[idx % len(colors)] for idx, cls in enumerate(classes)} # Create color mapping

                plot.add_trace(go.Bar(
                    name=f'Class_{i}',
                    x=methods,
                    y=scores,
                    marker=dict(color=class_colors[f'class_{i}']), # Assign color from the mapping
                    hovertemplate='Method: %{x}<br>Count: %{y}<br>Class: ' + str(i) + '<extra></extra>' # Use i instead of class_name
                ))

                plot.update_layout(
                    title=f'Top Research Methods for Class {i}',
                    xaxis_title='Research Method',
                    yaxis_title='Count',
                    xaxis=dict(type='category')
                )

                st.plotly_chart(plot, use_container_width=True)

# def publications_over_time(data, st):
#         st.subheader("Publications over time")
#         col1, col2 = st.columns(2)
#         with col1:
#             st.line_chart(data=data, x='Date', y='Publications', color=None, width=0, height=0, use_container_width=True)
#         with col2:
#             st.dataframe(data, hide_index=True, use_container_width=True, height=300)        


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
                # try:
                #     email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False)
                #     if email_of_registered_user:
                #         config["credentials"]["usernames"][username_of_registered_user]["uoas"] = []
                #         config["credentials"]["usernames"][username_of_registered_user]["admin"] = False
                #         with open('../config.yaml', 'w') as file:
                #             yaml.dump(config, file, default_flow_style=False)   
                #         st.success('User registered successfully')
                # except Exception as e:
                #     st.error(e)
                with open('../config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
            else: 
                # Tab content for each UoA
                st.header(REFlabels[uoas[uoa_controller]], divider="red")
                st.markdown("**Note:** Articles with embedding distance of less than 0.7 are selected for each UoA")
                publications_over_time(REFdata[uoas[uoa_controller]], prediction[uoa_controller], st)
                uoa_controller += 1            