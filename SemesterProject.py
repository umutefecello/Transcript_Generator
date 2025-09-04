from typing import List,Optional
import csv
import pandas as pd
import os
from fpdf import FPDF


GRADES={"AA":4.0,"BA":3.5,"BB":3.0,"CB":2.5,"CC":2.0,"DC":1.5,"DD":1.0,"FD":0.5,"FF":0.0}
#dictionary for letter grades
EX_GRADE={"EX"}
#dictionary for ex that will not count in cpga

class Department: #class for department objects on university
    def __init__(self, id:int,code:str,name:str):#initialization function and variables for department objects
        self.id=id
        self.code=code
        self.name=name
        self.cur_version:List["CurriculumVersion"]=[]# used curriculum versions for departments
        self.students:List["Student"]=[]#students in this department

    def add_curr_ver(self,version:"CurriculumVersion"):
        """
        going to add curriculum version to department
        """
        self.cur_version.append(version)# adding curriculum version to this department

    def add_student(self,student:"Student"):
        """
        going to add student to department
        """
        self.students.append(student)# adding students to this department

    def createTranscript(self, folderPath:str):# generate transcripts for all students in this department
        """
        going to create transcript for all students in this department and save transcripts to file
        """
        if not os.path.exists(folderPath):#crate folder if its not exists
            os.makedirs(folderPath)

        for student in self.students:
            transCreate=TranscriptCreate(student)
            file_name=f"{student.id}_{student.name.replace(' ', '_')}_transcript.pdf"
            full_path=os.path.join(folderPath, file_name)
            transCreate.save_to_file(full_path)
            print(f"transcript pdf saved at==>{full_path}")


class Course:# course class for representing course objects
    def __init__(self, id:int,code:str,name:str):
        self.id=id
        self.code=code
        self.name=name


class CurriculumVersion:# this class holds informations about version of curriculum used by which department
    def __init__(self, id:int,version_code:str,year:int,department:'Department'):
        self.id=id
        self.version_code=version_code
        self.year=year
        self.department=department
        self.cur_course:List["CurriculumCourse"]=[]

    def add_curr_course(self,course:"CurriculumCourse"):
        """
        going to add curriculum course to version
        """
        self.cur_course.append(course)

class CurriculumCourse:# this class links course to specific curriculum version
    def __init__(self, id:int,cur_version:'CurriculumVersion',course:'Course',metu_credi:str,ects_credi:float,prerequisites:Optional[List[int]]=None):
        self.id=id
        self.cur_version=cur_version
        self.course=course
        self.metu_credi=metu_credi
        self.ects_credi=ects_credi
        if prerequisites is not None:
            self.prerequisites=prerequisites
        else:
            self.prerequisites=[]

class Student:# student class used for student informations and their transcriptions
    def __init__(self, id:int,name:str,department:'Department'):
        self.id=id
        self.name=name
        self.department=department
        self.cur_version:Optional["CurriculumVersion"]=None
        self.transcript:List["TranscriptSemester"]=[]

    def add_transcript(self,semester:"TranscriptSemester"):
        """
        we gonna add semester transcript to student
        """
        self.transcript.append(semester)



class TranscriptCourseRec:# one course in a semester transcript
    def __init__(self,course_code:str,course_name:str,grade:str,credi:float):
        self.course_code=course_code
        self.course_name=course_name
        self.grade=grade
        self.credi=credi

class TranscriptSemester:# holds all courses taken in one semester and calculates gpas for this semester
    def __init__(self,semester_code:str):
        self.semester_code=semester_code
        self.courses:list["TranscriptCourseRec"]=[]
        self.gpa=None
        self.total_credit=0.0
        self.total_point=0.0

    def add_course(self,course_rec:"TranscriptCourseRec"):#adding course to semester and do not add dumplicates
        """
        we gonna add course record to the semester transcript
        """
        for existCourse in self.courses:
            if existCourse.course_code==course_rec.course_code:
                return

        self.courses.append(course_rec)
        self.total_credit+=course_rec.credi
        point=GRADES.get(course_rec.grade,None)
        if point is not None:
            self.total_point+= point*course_rec.credi

    def calculateGpa(self):# calculating gpa for current semester
        """
        we gonna calculate gpa for this semester
        """
        if self.total_credit>0:
            temp_gpa=self.total_point/self.total_credit
            self.gpa=int(temp_gpa*100+0.5)/100
        else:
            self.gpa=None

class TranscriptCreate:# creating transcripts by using student information and calculates gpa
    def __init__(self,student:"Student"):
        self.student=student

    def generate(self,sem_data:dict[str,list["TranscriptCourseRec"]]):
        """
        generate semester transcript records
        organize courses and calculate gpa
        """
        self.group_courses_by_semester(sem_data)


    def calculate_cgpa(self) ->Optional[float]:# calculates cgpa by using last grades of courses
        """
        calculate students cgpa
        """
        recentGrades={}
        for semester in self.student.transcript:
            for course in semester.courses:
                if course.grade in EX_GRADE:
                    continue
                recentGrades[course.course_code]=(course.grade,course.credi)

        total_point=0.0
        total_credi=0.0

        for grade,credi in recentGrades.values():
            point=GRADES.get(grade)
            if point!=None:
                total_point+=point*credi
                total_credi+=credi

        if total_credi==0:
            return None

        return int((total_point/total_credi)*100+0.5)/100

    def get_last_grade(self,course_code:str)->Optional[str]:# helper function to get last grade of specific course
        """
        Return the most recent grade for a given course.
        """
        recentGrade=None
        for semester in self.student.transcript:
            for course in semester.courses:
                if course.course_code==course_code and course.grade!="EX":
                    recentGrade=course.grade
        return recentGrade

    def save_to_file(self, filePath:str):# saves transcript to pdf file
        """
        save transcript to file
        """
        writervar=TranscriptCreator(self)
        writervar.writeToFile(filePath)

    def group_courses_by_semester(self,sem_data:dict[str,list["TranscriptCourseRec"]]):# groups all course records by semester
        """
        Group the student's course records by semester for structure transcript data
        """
        for semesterCode,courseList in sem_data.items():
            sem_transcript=TranscriptSemester(semesterCode)
            for course in courseList:
                sem_transcript.add_course(course)
            sem_transcript.calculateGpa()
            self.student.add_transcript(sem_transcript)

class DataLoad:#main class for loading all data from csv files
    def __init__(self):
        self.courses:dict[int,Course]={}
        self.departments:dict[str,Department]={}
        self.students:dict[int,Student]={}
        self.curriculum_versions:list[CurriculumVersion]=[]
        self.version_map:dict[tuple[str, int, int],CurriculumVersion]={}

    def get_student_by_id(self, student_id: int) -> Optional["Student"]:
        return self.students.get(student_id, None)

    def load_curriculum(self,csv_path:str,version:CurriculumVersion):#loading curriculum data from csv and organizes them
        """
        loads curriculum data from database and adds curriculum courses to the given version.
        """
        with open(csv_path,newline='',encoding='utf-8') as myfile:
            reader=csv.DictReader(myfile)
            version_id=1
            course_id=1

            for row in reader:
                dept_code=row["department_code"].strip()
                if not row["course_code"]:
                    continue

                course_code=int(row["course_code"])
                metu_credit=row["metu_credit"].strip()
                ects_credit=float(row["ects_credit"])

                prerequisites_raw=row["prerequisites"].strip()
                prerequisites=[]
                if prerequisites_raw:
                    for p in prerequisites_raw.split(","):
                        prerequisites.append(int(p))

                course_name=row["course_name"].strip()
                year=int(row["year"])
                semester=int(row["semester"])
                versCode=f"Y{year}S{semester}"
                department=self.departments[dept_code]
                version_key=(dept_code,year,semester)

                if version_key not in self.version_map:
                    version=CurriculumVersion(id=version_id,version_code=versCode,year=year,department=department)
                    version_id+=1
                    department.add_curr_ver(version)
                    self.curriculum_versions.append(version)
                    self.version_map[version_key]=version
                else:
                    version=self.version_map[version_key]
                if course_code not in self.courses:
                    course=Course(course_code,str(course_code),course_name)
                    self.courses[course_code]=course
                else:
                    course=self.courses[course_code]

                curriculum_course=CurriculumCourse(id=course_id,cur_version=version,course=course,metu_credi=metu_credit,ects_credi=ects_credit,prerequisites=prerequisites)
                version.add_curr_course(curriculum_course)
                course_id+=1

    def load_students(self,csv_path:str):# this function loads data and add themto departments
        """
        loads students and links them to departments and curriculum versions.
        """
        df=pd.read_csv(csv_path)
        for _,row in df.iterrows():
            student_id=int(row["student_id"])
            student_name=row["full_name"].strip()
            dept_code="CNG"
            if dept_code not in self.departments:
                continue
            department=self.departments[dept_code]
            if student_id not in self.students:
                student=Student(student_id,student_name,department)
                self.students[student_id]=student
                department.add_student(student)
                year=int(row["year"])
                semester=int(row["semester"])
                version_key=(dept_code,year,semester)
                if version_key in self.version_map:
                    student.cur_version=self.version_map[version_key]
            else:
                student=self.students[student_id]

            course_code=int(row["course_code"])
            course_name=row["course_name"]
            year=int(row["year"])
            semester=int(row["semester"])
            semsCode=f"Y{year}S{semester}"
            metu_credit=float(row["metu_credit"].split("(")[0])
            letter_grade=row["letter_grade"]

            if course_code not in self.courses:
                course=Course(course_code,str(course_code),course_name)
                self.courses[course_code]=course
            else:
                course=self.courses[course_code]
            course_record=TranscriptCourseRec(str(course_code),course_name,letter_grade,metu_credit)
            semester_found=None

            for sem in student.transcript:
                if sem.semester_code==semsCode:
                    semester_found=sem
                    break
            if not semester_found:
                semester_found=TranscriptSemester(semsCode)
                student.add_transcript(semester_found)

            semester_found.add_course(course_record)
            semester_found.calculateGpa()

class TranscriptCreator:#main class used for writing to pdf with using FPDF
    def __init__(self,trans_creator:TranscriptCreate):
        self.trans_creator=trans_creator

    def writeToFile(self, filePath: str):
        def convert_semester_label(index):
            baseYear=2024
            startYear=baseYear+(index//2)
            term="Fall" if index%2==0 else "Spring"
            return f"{startYear}-{startYear+1} {term}"

        myPdf = FPDF()
        myPdf.add_font("DejaVu","","DejaVuSans.ttf",uni=True)
        myPdf.add_font("DejaVu","B","DejaVuSans-Bold.ttf",uni=True)
        myPdf.set_font("DejaVu",size=12)
        myPdf.add_page()

        student = self.trans_creator.student
        myPdf.cell(200,10,txt=f"Name: {student.name}",ln=True)
        myPdf.cell(200,10, txt=f"Student ID: {student.id}",ln=True)
        myPdf.ln(10)

        cumCredits=0.0
        cumPoints=0.0

        for index, semester in enumerate(student.transcript):
            myPdf.set_font("DejaVu",style='B',size=12)
            myPdf.cell(200,10,txt=convert_semester_label(index),ln=True)
            myPdf.set_font("DejaVu",size=11)

            myPdf.cell(50,10,txt="Code",border=1)
            myPdf.cell(70,10,txt="Name",border=1)
            myPdf.cell(30,10,txt="Grade",border=1)
            myPdf.cell(30,10,txt="Credit",border=1)
            myPdf.ln()

            for course in semester.courses:
                myPdf.set_font("DejaVu",size=9)
                course_name=course.course_name
                myPdf.cell(50,10,txt=course.course_code,border=1)

                yBefore = myPdf.get_y()
                xAfter = myPdf.get_x()

                myPdf.multi_cell(70,5,txt=course_name,border=1)
                yAfter=myPdf.get_y()
                maxHeight=yAfter-yBefore

                myPdf.set_xy(xAfter+70,yBefore)
                myPdf.cell(30,maxHeight,txt=course.grade,border=1)
                myPdf.cell(30,maxHeight,txt=str(course.credi),border=1)
                myPdf.ln(maxHeight)

            if semester.gpa is not None:
                myPdf.set_font("DejaVu",style='B',size=11)
                myPdf.cell(40,10,txt="GPA",border=1)
                myPdf.cell(40,10,txt=str(semester.gpa),border=1)
                myPdf.ln()
                myPdf.cell(40,10,txt="Total Credit",border=1)
                myPdf.cell(40,10,txt=str(semester.total_credit),border=1)
                myPdf.ln()
                myPdf.cell(40,10,txt="Total Point",border=1)
                myPdf.cell(40,10,txt=str(semester.total_point),border=1)
                myPdf.ln()

            cumCredits+=semester.total_credit
            cumPoints+=semester.total_point
            if cumCredits>0:
                cgpaRecent= int((cumPoints/cumCredits) *100+0.5)/100
                myPdf.cell(40,10,txt="CGPA",border=1)
                myPdf.cell(40,10,txt=str(cgpaRecent),border=1)
                myPdf.ln(15)

        myPdf.output(filePath)

if __name__=="__main__":# main function to execute all process directly
    data = DataLoad()
    data.departments["CNG"]=Department(1,"CNG","Computer Engineering")
    data.departments["SNG"]=Department(2,"SNG","Software Engineering")
    data.departments["INE"]=Department(3,"INE","Industrial Engineering")
    data.load_students("METU_Student_Simulated_Transcripts_With_Names.csv")
    data.load_curriculum("METU_Curriculum_All_Departments.csv",None)
    try:
        student_id_input=int(input("Enter student ID: ").strip())
    except ValueError:
        print("Invalid student ID.")
        exit(1)

    takenStudent = data.get_student_by_id(student_id_input)
    if takenStudent:
        transcript_creator=TranscriptCreate(takenStudent)
        deskPath=os.path.join(os.path.expanduser("~"),"Desktop","transcript")
        os.makedirs(deskPath,exist_ok=True)
        myFile= f"{takenStudent.id}_{takenStudent.name.replace(' ', '_')}_transcript.pdf"
        full_path=os.path.join(deskPath,myFile)
        transcript_creator.save_to_file(full_path)
        print(f"Transcript PDF saved at ==> {full_path}")
    else:
        print(f"No student found with ID {student_id_input}.")