import unittest
from Transcrip_generator import DataLoad
import os


class TestStudentCsvLoad(unittest.TestCase):
    def setUp(self):
        current_dir=os.path.dirname(__file__)
        project_root=os.path.abspath(os.path.join(current_dir, "../../"))
        self.csv_path=os.path.join(project_root,"METU_Student_Simulated_Transcripts_With_Names.csv")
        self.data_load=DataLoad()

    def test_student_csv_exist(self):
        self.assertTrue(
            os.path.exists(self.csv_path),
            f"File does not exist. Please check the path and try again. Current path {self.csv_path}"
        )

    def test_student_csv_load(self):
        try:
            self.data_load.load_students(self.csv_path)
        except Exception as e:
            self.fail(f"An error occurred while loading the CSV file: {e}")

if __name__ == '__main__':
    unittest.main()
