import unittest
from Transcrip_generator import DataLoad,Department
import os

class TestCurriculumCsvLoad(unittest.TestCase):
    def setUp(self):
        current_dir=os.path.dirname(__file__)
        project_root=os.path.abspath(os.path.join(current_dir,"../../"))
        self.csv_path=os.path.join(project_root,"METU_Curriculum_All_Departments.csv")
        self.data_load=DataLoad()
        self.data_load.departments["CNG"] = Department(1, "CNG", "Computer Engineering")
        self.data_load.departments["SNG"] = Department(2, "SNG", "Software Engineering")
        self.data_load.departments["INE"] = Department(3, "INE", "Industrial Engineering")



    def test_curriculum_csv_exist(self):
        self.assertTrue(
            os.path.exists(self.csv_path),
            f"File does not exist. Please check the path and try again. Current path {self.csv_path}")

    def test_curriculum_csv_load(self):
        try:
            self.data_load.load_curriculum(self.csv_path,None)
        except Exception as e:
            self.fail(f"An error occurred while loading the CSV file: {e}")

if __name__ == '__main__':
    unittest.main()