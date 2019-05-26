from db.models.auth import Group
from db.models.auth import Permission
from db.models.auth import GroupPermissions


def do_migration():
    #: Groups.
    admin_group = Group.get(name="admin")
    attendant_group = Group.get(name="attendant")
    physiotherapist_group = Group.get(name="physiotherapist")

    #: Creations.
    create_admin = Permission.get(codename="create_admin")
    create_attendant = Permission.get(codename="create_attendant")
    create_physiotherapist = Permission.get(codename="create_physiotherapist")
    create_patient = Permission.get(codename="create_patient")

    #: Changes.
    change_admin_data = Permission.get(codename="change_admin_data")
    change_attendant_data = Permission.get(codename="change_attendant_data")
    change_physiotherapist_data = Permission.get(codename="change_physiotherapist_data")
    change_patient_data = Permission.get(codename="change_patient_data")

    #: Readings
    read_admin_data = Permission.get(codename="read_admin_data")
    read_attendant_data = Permission.get(codename="read_attendant_data")
    read_physiotherapist_data = Permission.get(codename="read_physiotherapist_data")
    read_patient_data = Permission.get(codename="read_patient_data")

    #: admin.
    GroupPermissions.create(group=admin_group, permission=create_admin)
    GroupPermissions.create(group=admin_group, permission=create_attendant)
    GroupPermissions.create(group=admin_group, permission=create_physiotherapist)
    GroupPermissions.create(group=admin_group, permission=change_admin_data)
    GroupPermissions.create(group=admin_group, permission=change_attendant_data)
    GroupPermissions.create(group=admin_group, permission=change_physiotherapist_data)
    GroupPermissions.create(group=admin_group, permission=read_admin_data)
    GroupPermissions.create(group=admin_group, permission=read_attendant_data)
    GroupPermissions.create(group=admin_group, permission=read_physiotherapist_data)

    #: attendant.
    GroupPermissions.create(group=attendant_group, permission=create_patient)
    GroupPermissions.create(group=attendant_group, permission=change_patient_data)
    GroupPermissions.create(group=attendant_group, permission=read_patient_data)

    #: physiotherapist.
    GroupPermissions.create(group=physiotherapist_group, permission=read_patient_data)


if __name__ == "__main__":
    do_migration()
