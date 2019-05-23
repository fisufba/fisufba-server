from db.models.auth import Permission


def do_migration():
    #: Creations.
    Permission.create(
        name="Create attendant",
        codename="create_attendant",
        description="Allows the creation of an attendant",
    )
    Permission.create(
        name="Create physiotherapist",
        codename="create_physiotherapist",
        description="Allows the creation of a physiotherapist",
    )
    Permission.create(
        name="Create patient",
        codename="create_patient",
        description="Allows the creation of a patient",
    )

    #: Changes.
    Permission.create(
        name="Change attendant data",
        codename="change_attendant_data",
        description="Allows changes to attendant data",
    )
    Permission.create(
        name="Change physiotherapist data",
        codename="change_physiotherapist_data",
        description="Allows changes to physiotherapist data",
    )
    Permission.create(
        name="Change patient data",
        codename="change_patient_data",
        description="Allows changes to patient data",
    )

    #: Readings
    Permission.create(
        name="Read attendant data",
        codename="read_attendant_data",
        description="Allows read in attendant data",
    )
    Permission.create(
        name="Read physiotherapist data",
        codename="read_physiotherapist_data",
        description="Allows read in physiotherapist data",
    )
    Permission.create(
        name="Read patient data",
        codename="read_patient_data",
        description="Allows read in patient data",
    )


if __name__ == "__main__":
    do_migration()
