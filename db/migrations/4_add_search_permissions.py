from db.models.auth import Group
from db.models.auth import Permission
from db.models.auth import GroupPermissions


def do_migration():
    #: Searching.
    search_patient = Permission.create(
        name="Search patient",
        codename="search_patient",
        description="Allows the search for patients",
    )

    #: Allowed groups.
    attendant_group = Group.get(name="attendant")
    physiotherapist_group = Group.get(name="physiotherapist")

    #: attendant.
    GroupPermissions.create(group=attendant_group, permission=search_patient)

    #: physiotherapist.
    GroupPermissions.create(group=physiotherapist_group, permission=search_patient)


if __name__ == "__main__":
    do_migration()
