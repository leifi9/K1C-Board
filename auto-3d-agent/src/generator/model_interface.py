class ModelInterface:
    """
    Interface for 3D model generation implementations.
    """
    
    def generate_model(self, description, images=None, videos=None, links=None):
        """
        Generate a 3D model from input description and resources.
        
        Args:
            description: Text description of the model
            images: Optional list of reference images
            videos: Optional list of reference videos
            links: Optional list of reference links
            
        Returns:
            Generated model data or path
        """
        raise NotImplementedError("Subclasses must implement generate_model")

    def fetch_additional_data(self, description):
        """
        Fetch additional data to enhance model generation.
        
        Args:
            description: Description to use for fetching data
            
        Returns:
            Additional data for model generation
        """
        return {}

    def validate_input(self, description, images=None, videos=None, links=None):
        """
        Validate input parameters for model generation.
        
        Args:
            description: Text description of the model
            images: Optional list of reference images
            videos: Optional list of reference videos
            links: Optional list of reference links
            
        Returns:
            bool: True if input is valid
        """
        return description is not None and len(description) > 0

    def export_model(self, format_type):
        """
        Export the generated model to a specific format.
        
        Args:
            format_type: Target export format (e.g., 'STL', 'OBJ', 'STEP')
            
        Returns:
            Path to exported model file
        """
        raise NotImplementedError("Subclasses must implement export_model")