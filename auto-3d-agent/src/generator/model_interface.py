class ModelInterface:
    def generate_model(self, description, images=None, videos=None, links=None):
        pass

    def fetch_additional_data(self, description):
        pass

    def validate_input(self, description, images=None, videos=None, links=None):
        pass

    def export_model(self, format_type):
        pass