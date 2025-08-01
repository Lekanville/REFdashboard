import io

def download_predictions_section(data, predictions_selector, classes, current_uoa, UoA_selection_type, st):
    selected_class = st.selectbox(
        f"Select a Prediction Class from UoA {current_uoa} to Download",
        ["All Classes"] + classes
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