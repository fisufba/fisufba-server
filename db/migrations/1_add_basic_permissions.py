from db.models.auth import Permission


def do_migration():
    #: Creations.
    Permission.create(
        name="Create admin",
        codename="create_admin",
        description="Allows the creation of an admin user",
    )
    Permission.create(
        name="Create attendant",
        codename="create_attendant",
        description="Allows the creation of an attendant user",
    )
    Permission.create(
        name="Create physiotherapist",
        codename="create_physiotherapist",
        description="Allows the creation of a physiotherapist user",
    )
    Permission.create(
        name="Create patient",
        codename="create_patient",
        description="Allows the creation of a patient user",
    )
    Permission.create(
        name="Create form",
        codename="create_form",
        description="Allows the creation of a form",
    )

    #: Changes.
    Permission.create(
        name="Change admin data",
        codename="change_admin_data",
        description="Allows changes to admin user data",
    )
    Permission.create(
        name="Change attendant data",
        codename="change_attendant_data",
        description="Allows changes to attendant user data",
    )
    Permission.create(
        name="Change physiotherapist data",
        codename="change_physiotherapist_data",
        description="Allows changes to physiotherapist user data",
    )
    Permission.create(
        name="Change patient data",
        codename="change_patient_data",
        description="Allows changes to patient user data",
    )
    Permission.create(
        name="Change form data",
        codename="change_form_data",
        description="Allows changes to form data",
    )

    #: Readings
    Permission.create(
        name="Read admin data",
        codename="read_admin_data",
        description="Allows read in admin user data",
    )
    Permission.create(
        name="Read attendant data",
        codename="read_attendant_data",
        description="Allows read in attendant user data",
    )
    Permission.create(
        name="Read physiotherapist data",
        codename="read_physiotherapist_data",
        description="Allows read in physiotherapist user data",
    )
    Permission.create(
        name="Read patient data",
        codename="read_patient_data",
        description="Allows read in patient user data",
    )
    Permission.create(
        name="Read form data",
        codename="read_form_data",
        description="Allows read in form data",
    )


if __name__ == "__main__":
    do_migration()
