import enum

from peewee import BooleanField
from peewee import CharField
from peewee import DateField
from peewee import ForeignKeyField
from peewee import TextField

from db.models.auth import User
from db.models.base import _BaseModel
from utils.fields import EnumField, JSONField


class Form(_BaseModel):
    user = ForeignKeyField(User)


class PatientInformation(Form):
    class Meta:
        table_name = "forms_patient_information"

    class GenderTypes(enum.Enum):
        Masculine = "Masculino"
        Feminine = "Feminino"

    user = ForeignKeyField(User, unique=True)

    gender = EnumField(GenderTypes)
    birthday = DateField()

    acquaintance_phone = CharField()

    address = CharField()
    neighborhood = CharField()
    city = CharField()
    country = CharField()


class SociodemographicEvaluation(Form):
    class Meta:
        table_name = "forms_sociodemographic_evaluation"

    class CivilStatusTypes(enum.Enum):
        Single = "Solteiro(a)"
        Married = "Casado(a)"
        Divorced = "Divorciado(a)"
        Widowed = "Viúvo(a)"

    class LivesWithStatusTypes(enum.Enum):
        Alone = "Sozinho(a)"
        Relatives = "Familiares"
        Friends = "Amigos"
        Spouse = "Cônjuge"

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
        AshworthScale = 2
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

        @classmethod
        def valid_string_values(cls):
            return {
                "Goniometria",
                "Escala de Ashworth",
                "Avaliação Sensorial",
                "Força Muscular Respiratória",
                "Espirometria",
                "Peak-Flow",
                "Ventilometria",
                "Avaliação da Dor",
                "Força Muscular",
                "Baropodometria",
                "Eletromiografia",
                "Biofotogrametria",
                "Dinamometria",
            }

        @classmethod
        def from_string(cls, string):
            convert_table = {
                "Goniometria": cls.Goniometry,
                "Escala de Ashworth": cls.AshworthScale,
                "Avaliação Sensorial": cls.SensoryEvaluation,
                "Força Muscular Respiratória": cls.RespiratoryMuscleStrength,
                "Espirometria": cls.Spirometry,
                "Peak-Flow": cls.PeakFlow,
                "Ventilometria": cls.Ventilometry,
                "Avaliação da Dor": cls.PainEvaluation,
                "Força Muscular": cls.MuscleStrength,
                "Baropodometria": cls.Baropodometry,
                "Eletromiografia": cls.Electromyography,
                "Biofotogrametria": cls.Biophotogrammetry,
                "Dinamometria": cls.Dynamometry,
            }
            return convert_table[string]

        @classmethod
        def to_string(cls, enum_item):
            convert_table = {
                cls.Goniometry: "Goniometria",
                cls.AshworthScale: "Escala de Ashworth",
                cls.SensoryEvaluation: "Avaliação Sensorial",
                cls.RespiratoryMuscleStrength: "Força Muscular Respiratória",
                cls.Spirometry: "Espirometria",
                cls.PeakFlow: "Peak-Flow",
                cls.Ventilometry: "Ventilometria",
                cls.PainEvaluation: "Avaliação da Dor",
                cls.MuscleStrength: "Força Muscular",
                cls.Baropodometry: "Baropodometria",
                cls.Electromyography: "Eletromiografia",
                cls.Biophotogrammetry: "Biofotogrametria",
                cls.Dynamometry: "Dinamometria",
            }
            return convert_table[enum_item]

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
        BarthelsScale = 65536

        @classmethod
        def valid_string_values(cls):
            return {
                "Avaliação de Marcha",
                "Teste de Caminhada 6M",
                "Escala de Equilíbrio de Berg",
                "Teste do Alcane Funcional",
                "Time Up Go (TUG)",
                "Velocidade de marcha confortável e rápida (10m)",
                "Teste do Degrau",
                "QV Fibrose Cística",
                "SF-36",
                "WHODAS 2.0",
                "MIF",
                "WOMAC",
                "DASH",
                "Escala London",
                "EORCT QLQ C-30",
                "Saint George",
                "Escala de Barthel",
            }

        @classmethod
        def from_string(cls, string):
            convert_table = {
                "Avaliação de Marcha": cls.MarchEvaluation,
                "Teste de Caminhada 6M": cls.SixMWalkTest,
                "Escala de Equilíbrio de Berg": cls.BergsBalanceScale,
                "Teste do Alcane Funcional": cls.FunctionalScopeTest,
                "Time Up Go (TUG)": cls.TimeUpGo,
                "Velocidade de marcha confortável e rápida (10m)": cls.ComfortableAndFastRunningSpeed,
                "Teste do Degrau": cls.StepTest,
                "QV Fibrose Cística": cls.QVCysticFibrosis,
                "SF-36": cls.SF36,
                "WHODAS 2.0": cls.WHODAS2,
                "MIF": cls.MIF,
                "WOMAC": cls.WOMAC,
                "DASH": cls.DASH,
                "Escala London": cls.LondonScale,
                "EORCT QLQ C-30": cls.EORCTQLQC30,
                "Saint George": cls.SaintGeorge,
                "Escala de Barthel": cls.BarthelsScale,
            }
            return convert_table[string]

        @classmethod
        def to_string(cls, enum_item):
            convert_table = {
                cls.MarchEvaluation: "Avaliação de Marcha",
                cls.SixMWalkTest: "Teste de Caminhada 6M",
                cls.BergsBalanceScale: "Escala de Equilíbrio de Berg",
                cls.FunctionalScopeTest: "Teste do Alcane Funcional",
                cls.TimeUpGo: "Time Up Go (TUG)",
                cls.ComfortableAndFastRunningSpeed: "Velocidade de marcha confortável e rápida (10m)",
                cls.StepTest: "Teste do Degrau",
                cls.QVCysticFibrosis: "QV Fibrose Cística",
                cls.SF36: "SF-36",
                cls.WHODAS2: "WHODAS 2.0",
                cls.MIF: "MIF",
                cls.WOMAC: "WOMAC",
                cls.DASH: "DASH",
                cls.LondonScale: "Escala London",
                cls.EORCTQLQC30: "EORCT QLQ C-30",
                cls.SaintGeorge: "Saint George",
                cls.BarthelsScale: "Escala de Barthel",
            }
            return convert_table[enum_item]

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


class StructureAndFunction(Form):
    class Meta:
        table_name = "forms_structure_and_function"

    class StructureAndFunctionTypes(enum.Enum):
        Goniometry = "goniometry"
        AshworthScale = "ashworth_scale"
        SensoryEvaluation = "sensory_evaluation"
        RespiratoryMuscleStrength = "respiratory_muscle_strength"
        Spirometry = "spirometry"
        PeakFlow = "peak_flow"
        Ventilometry = "ventilometry"
        PainEvaluation = "pain_evaluation"
        MuscleStrength = "muscle_strength"
        Baropodometry = "baropodometry"
        Electromyography = "electromyography"
        Biophotogrammetry = "biophotogrammetry"
        Dynamometry = "dynamometry"

    type = EnumField(StructureAndFunctionTypes)


class StructureAndFunctionMeasure(_BaseModel):
    class Meta:
        table_name = "forms_structure_and_function_measure"

    class TypeTypes(enum.Enum):
        LeftSide = "E"
        RightSide = "D"

        MaximumInspirationPressure = "PiMax"
        MaximumExpirationPressure = "PeMax"

        PainIntensity = "Intensidade da Dor"

    class SensoryTypeTypes(enum.Enum):
        LightTouch = "Toque Leve"
        Pressure = "Pressão"
        Stings = "Picadas"
        Temperature = "Temperatura"
        TactileLocation = "Localização Tática"
        SimultaneousBilateralTouch = "Toque Bilateral Simultâneo"
        Proprioception = "Propriocepção"

    structure_and_function = ForeignKeyField(StructureAndFunction)

    type = EnumField(TypeTypes, default=None, null=True)

    sensory_type = EnumField(SensoryTypeTypes, default=None, null=True)

    target = CharField(default=None, null=True)
    value = CharField()

    date = DateField()


_FORMS_TABLES = (
    PatientInformation,
    SociodemographicEvaluation,
    KineticFunctionalEvaluation,
    StructureAndFunction,
    StructureAndFunctionMeasure,
)
