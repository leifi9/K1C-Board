class StepExporter:
    def __init__(self):
        pass

    def export(self, model_data, file_path):
        # Logic to convert model_data to STEP format
        step_data = self._convert_to_step(model_data)
        self.save_file(step_data, file_path)

    def save_file(self, step_data, file_path):
        with open(file_path, 'wb') as file:
            file.write(step_data)

    def _convert_to_step(self, model_data):
        # Placeholder for conversion logic
        return b'STEP data representation of the model'