from pathlib import Path

import pandas as pd
import yaml
from yaml.loader import SafeLoader

from code.authentication import reset_password
from code.components.download_predictions import download_predictions_section
from code.components.plots_publications import plot_distance_vs_prediction_for_uoa
from code.components.plots_publications import plot_embeddings_for_uoas
from code.components.plots_publications import plot_publications_over_time_bar
from code.components.plots_sjr_alt import plot_altmetric_scores_over_time
from code.components.plots_sjr_alt import plot_sjr_scores_over_time
from code.components.plots_top_reserach_methods import plot_top_research_methods
from code.db.predictions import get_predictions_sync
from code.tools.tools import select_data_for_uoa

CONFIG_PATH = Path(__file__).resolve().parents[2] / "dashboard" / "config.yaml"
with CONFIG_PATH.open() as file:
    config = yaml.load(file, Loader=SafeLoader)


# The data
data_prediction, data_all_ref_embeddings_2d = get_predictions_sync()
df = pd.DataFrame(data_prediction)
df = df[df['article_type'] == "ContributionToJournal"]
df_all_ref_2d = pd.DataFrame(data_all_ref_embeddings_2d)


UOA_CONFIG = {
    "UoA1": {
        "number": "1",
        "label": "REF UoA1 - Clinical Medicine",
        "distance_column": "distance_to_median_of_uoa_1",
        "prediction_column": "predictions_for_uoa_1",
    },
    "UoA2": {
        "number": "2",
        "label": "REF UoA2 - Public Health, Health Services and Primary Care",
        "distance_column": "distance_to_median_of_uoa_2",
        "prediction_column": "predictions_for_uoa_2",
    },
    "UoA4": {
        "number": "4",
        "label": "REF UoA4 - Psychology, Psychiatry and Neuroscience",
        "distance_column": "distance_to_median_of_uoa_4",
        "prediction_column": "predictions_for_uoa_4",
    },
    "UoA5": {
        "number": "5",
        "label": "REF UoA5 - Biological Sciences",
        "distance_column": "distance_to_median_of_uoa_5",
        "prediction_column": "predictions_for_uoa_5",
    },
    "UoA6": {
        "number": "6",
        "label": "REF UoA6 - Agriculture, Food and Veterinary Sciences",
        "distance_column": "distance_to_median_of_uoa_6",
        "prediction_column": "predictions_for_uoa_6",
    },
}

REFlabels = {uoa: cfg["label"] for uoa, cfg in UOA_CONFIG.items()}
distances = [cfg["distance_column"] for cfg in UOA_CONFIG.values()]
prediction = [cfg["prediction_column"] for cfg in UOA_CONFIG.values()]
all_uoas = [cfg["number"] for cfg in UOA_CONFIG.values()]


def publications_over_time(data, current_uoa, st, UoA_selection_type):
    # Filter data based on the selected UoA and its explicit mapping.
    uoa_config = UOA_CONFIG[current_uoa]
    predictions_selector = uoa_config["prediction_column"]
    distance_column = uoa_config["distance_column"]
    current_uoa_number = uoa_config["number"]

    
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


    col = st.columns(1)
    with col[0]:
        # row
        st.subheader("Predictions and Embeddings")
        st.markdown("**Key** <br> 7 = 4+/4,   6 = 4-/3+,   5 = 3,   4 = 3-/2+,   3 = 2,   2 = 2-/1+,   1 = 1/1-", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)    
    with col1:
        # row
        # Plotting publication predicted scores over time
        plot = plot_publications_over_time_bar(classes, years, yearly_predictions)
        plot.show()
        st.plotly_chart(plot, key=f"predictions_{current_uoa}", use_container_width=True)

    with col2:
        # row
        # Filter data for the current UoA
        plot = plot_distance_vs_prediction_for_uoa(
            df,
            data,
            classes,
            predictions_selector,
            distance_column,
            current_uoa_number,
        )
        plot.show()
        st.plotly_chart(plot, key=f"distances_{current_uoa}", use_container_width=True)

    with col3:
        # row
        # Embeddings for all UoAs form other universities
        plot = plot_embeddings_for_uoas(
            all_uoas,
            df_all_ref_2d,
            data,
            current_uoa_number
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
        # row
        # Plotting SJR scores
        plot = plot_sjr_scores_over_time(years, all_sjr)
        plot.show()
        st.plotly_chart(plot, key=f"sjr_scores_{current_uoa}", use_container_width=True)
    
    with col2:
        # row
        # Plotting Altmetric scores
        plot = plot_altmetric_scores_over_time(years, all_alt)
        plot.show()
        st.plotly_chart(plot, key=f"altmetric_scores_{current_uoa}", use_container_width=True)

    #  For research methods
    if predictions_selector == "predictions_for_uoa_2":
        col = st.columns(1)
        with col[0]:
            # row
            st.subheader("Top research methods for each class")

        # Plotting top research methods
        col1, col2, col3 = st.columns(3)
        with col1:
            # For class 7 and 4
            plot_top_research_methods(data, predictions_selector, [7, 4], current_uoa, st)
        with col2:
            # For class 6
            plot_top_research_methods(data, predictions_selector, [6], current_uoa, st)
        with col3:
            # For class 5
            plot_top_research_methods(data, predictions_selector, [5], current_uoa, st)        


    # Download predictions
    col = st.columns(1)
    with col[0]:
        st.subheader("Download predictions")
    col1, col2, col3 = st.columns(3)
    with col1:
        download_predictions_section(data, predictions_selector, classes, current_uoa, UoA_selection_type, st)


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
            selected_uoa = uoas[uoa_controller]
            if admin == True and selected_uoa == "admin":
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

                with CONFIG_PATH.open('w') as file:
                    yaml.dump(config, file, default_flow_style=False)
            else: 
                # Tab content for each UoA
                st.header(REFlabels[selected_uoa], divider="red")
                col_1, col_2 = st.columns(2)

                with col_2:
                    UoA_selection_type = st.selectbox("Choose how UoA data is selected",
                                                          ("Embedding distance less than 0.7", "Minimum embedding distance"),
                                                        key =f"select_{selected_uoa}"
                                                        )
                    
                REFdata = select_data_for_uoa(df, UoA_selection_type, distances)

                with col_1:
                    # row
                    st.markdown("You can select the UoA data based on either embedding distance of less than 0.7 or minimum embedding distance. " \
                    "The data is filtered based on the selected method and then visualized.")
                    st.markdown(f'**The current selection is "{UoA_selection_type}" with {len(REFdata[selected_uoa])} articles.**')

                # Plotting publications over time
                publications_over_time(REFdata[selected_uoa], selected_uoa, st, UoA_selection_type)
                uoa_controller += 1            