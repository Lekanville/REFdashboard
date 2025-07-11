def select_data_for_uoa(read_data, selected_name, distances):
    """
    Selects data for each UoA based on the either embedding distance less than 0.7 
    or minimum embedding distance.
    """
    REFdata = {}

    if selected_name == "Embedding distance less than 0.7":
        for distance in distances:
            df_uoa = read_data[read_data[distance] < 0.7]
            uoa = distance.split("_")[-1]
            REFdata[f'UoA{uoa}'] = df_uoa
    elif selected_name == "Minimum embedding distance":
        read_data["minimum_distances"] = read_data[distances].idxmin(axis = 1).apply(lambda x: x.split("_")[-1])
        for distance in distances:
            uoa = distance.split("_")[-1]
            df_uoa = read_data[read_data["minimum_distances"] == uoa]
            REFdata[f'UoA{uoa}'] = df_uoa
    # REFdata = {}
    # for distance in distances:
    #     #   df_uoa = df[df[j] < 0.7][["research_uuid", "year", "main_research_method", distances[i], prediction[i]]]
    #     df_uoa = df[df[distance] < 0.7]
    #     uoa = distance.split("_")[-1]
    #     REFdata[f'UoA{uoa}'] = df_uoa


    return REFdata

def get_research_methods_for_uoa(uoa_data, class_column, predictions_selector):
    """
    Returns a dictionary with research methods for each UoA based on the selected name.
    """
    data_class = uoa_data[uoa_data[predictions_selector] == class_column]
    class_methods = data_class['main_research_method'].value_counts().head(6).to_dict()

    methods = []
    scores = []
    for k, v in class_methods.items():
        methods.append(k)
        scores.append(v)
    return(methods, scores)
