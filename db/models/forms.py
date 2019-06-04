import enum

from peewee import BooleanField
from peewee import CharField
from peewee import DateTimeField
from peewee import ForeignKeyField
from peewee import TextField

from db.models.auth import User
from db.models.base import _BaseModel
from utils.fields import EnumField, JSONField


class PatientInformation(_BaseModel):
    class Meta:
        table_name = "forms_patient_information"

    class GenderTypes(enum.Enum):
        Masculine = "Masculino"
        Feminine = "Feminino"

    user = ForeignKeyField(User, unique=True)

    gender = EnumField(GenderTypes)
    birthday = DateTimeField()

    phone = CharField()
    acquaintance_phone = CharField()

    address = CharField()
    neighborhood = CharField()
    city = CharField()
    country = CharField()


class Form(_BaseModel):
    patient_information = ForeignKeyField(PatientInformation)


class SociodemographicEvaluation(Form):
    class Meta:
        table_name = "forms_sociodemographic_evaluation"

    class LivesWithStatusTypes(enum.Enum):
        Alone = "Sozinho(a)"
        Relatives = "Familiares"
        Friends = "Amigos"
        Spouse = "Cônjuge"

    class CivilStatusTypes(enum.Enum):
        Single = "Solteiro(a)"
        Married = "Casado(a)"
        Divorced = "Divorciado(a)"
        Widowed = "Viúvo(a)"

    class EducationTypes(enum.Enum):
        Illiterate = "Analfabeto(a)"
        Primary = "Primeiro Grau"
        Secondary = "Segundo Grau"
        Tertiary = "Superior/Pós-graduado(a)"

    class OccupationalStatusTypes(enum.Enum):
        Student = "Estudante"
        Unemployed = "Desempregado(a)"
        Employed = "Empregado(a)"
        AwayForHealth = "Afastado(a) por problemas de saúde"
        Retired = "Aposentado(a)"

    civil_status = EnumField(CivilStatusTypes)
    lives_with_status = EnumField(LivesWithStatusTypes)

    education = EnumField(EducationTypes)
    occupational_status = EnumField(OccupationalStatusTypes)
    current_job = CharField(default=None, null=True)
    last_job = CharField(default=None, null=True)

    is_sick = BooleanField()
    diseases = JSONField(default=None, null=True)
    is_medicated = BooleanField()
    medicines = JSONField(default=None, null=True)


class KineticFunctionalEvaluation(Form):
    class Meta:
        table_name = "forms_kinetic_functional_evaluation"

    class StructureAndFunctionTypes(enum.Flag):
        Goniometry = 1
        ArshworthScale = 2
        SensoryEvaluation = 4
        RespiratoryMuscleStrength = 8
        Spirometry = 16
        PeakFlow = 32
        Ventilometry = 64
        PainEvaluation = 128
        MuscleStrength = 256
        Baropodometry = 512
        Electromyography = 1024
        Biophotogrammetry = 2048
        Dynamometry = 4096

    class ActivityAndParticipationTypes(enum.Flag):
        MarchEvaluation = 1
        SixMWalkTest = 2
        BergsBalanceScale = 4
        FunctionalScopeTest = 8
        TimeUpGo = 16
        ComfortableAndFastRunningSpeed = 32
        StepTest = 64
        QVCysticFibrosis = 128
        SF36 = 256
        WHODAS2 = 512
        MIF = 1024
        WOMAC = 2048
        DASH = 4096
        LondonScale = 8192
        EORCTQLQC30 = 16384
        SaintGeorge = 32768
        BarthelScale = 65536

    #: Main and Functional Complaints.
    clinic_diagnostic = TextField()
    main_complaint = TextField()
    functional_complaint = TextField()

    #: Patient Clinical and Functional History.
    clinical_history = TextField()
    functional_history = TextField()

    #: Physical-Functional Tests Planning.
    structure_and_function = EnumField(
        StructureAndFunctionTypes, default=StructureAndFunctionTypes(0)
    )
    activity_and_participation = EnumField(
        ActivityAndParticipationTypes, default=ActivityAndParticipationTypes(0)
    )

    #: Physical-Functional Tests Results.
    physical_functional_tests_results = TextField(default=None, null=True)
    #: Complementary Exams Result.
    complementary_exams_results = TextField(default=None, null=True)

    #: Functional Kinetic Diagnosis.
    deficiency_diagnosis = TextField(default=None, null=True)
    activity_limitation_diagnosis = TextField(default=None, null=True)
    participation_restriction_diagnosis = TextField(default=None, null=True)
    environment_factors_diagnosis = TextField(default=None, null=True)
    functional_objectives_diagnosis = JSONField(default=None, null=True)
    therapeutic_plan_diagnosis = JSONField(default=None, null=True)

    reevaluation_dates = JSONField(default=None, null=True)

    #: Assessors.
    academic_assessor = CharField(default=None, null=True)
    preceptor_assessor = CharField(default=None, null=True)


_FORMS_TABLES = (
    PatientInformation,
    SociodemographicEvaluation,
    KineticFunctionalEvaluation,
)
