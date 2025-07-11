class Colors:
    """
    A class to hold color constants for the dashboard.
    """
    # colors = plotly.colors.qualitative.Plotly # Using a qualitative color scale
    # class_colors = {f'class_{cls}': colors[i % len(colors)] for i, cls in enumerate(classes)} # Create color mapping


    class_colors = {'class_1': "#F81F1F",
                    'class_2': "#F84A15",
                    'class_3': "#E07536",
                    'class_4': "#E89453",
                    'class_5': '#00CC96',
                    'class_6': "#4353F9",
                    'class_7': "#B402FB"
                    }
    
    embeddings_class_colors = {'class_1': "#FD7373",
                    'class_2': "#F98E89",
                    'class_3': "#FBAC8A",
                    'class_4': "#FCCC94",
                    'class_5': "#93FBDF",
                    'class_6': "#9099FB",
                    'class_7': "#DC90FA"
                    }
    
    bristol_uoa_colors = {'uoa_1': '#FF6692',
                'uoa_2': '#D96DB3',
                'uoa_4': '#19D3F3',
                'uoa_5': '#00CC96',
                'uoa_6': '#AB63FA',
                }

    ref_uoa_colors = {'uoa_1': "#B64666",
                'uoa_2': "#873C6C",
                'uoa_4': "#408F9D",
                'uoa_5': "#40947D",
                'uoa_6': "#70439F",
                }
    # Additional colors can be added as needed

    @classmethod
    def get_class_colors(cls):
        """
        Get the color for a given class name.
        
        :param class_name: The name of the class (e.g., 'class_1', 'uoa_1').
        :return: The corresponding color as a string.
        """
        return cls.class_colors
    
    @classmethod
    def get_embeddings_class_colors(cls):
        """
        Get the color for a given class name for embeddings.
        
        :param class_name: The name of the class (e.g., 'class_1', 'uoa_1').
        :return: The corresponding color as a string.
        """
        return cls.embeddings_class_colors
    
    @classmethod
    def get_bristol_uoa_colors(cls):
        """
        Get the color for a given Bristol UoA name.
        
        :param uoa_name: The name of the UoA (e.g., 'uoa_1').
        :return: The corresponding color as a string.
        """
        return cls.bristol_uoa_colors
    
    @classmethod
    def get_ref_uoa_colors(cls):
        """
        Get the color for a given REF UoA name.
        
        :param uoa_name: The name of the UoA (e.g., 'uoa_1').
        :return: The corresponding color as a string.
        """
        return cls.ref_uoa_colors