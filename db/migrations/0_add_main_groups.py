from db.models.auth import Group


def do_migration():
    Group.create(name="admin")
    Group.create(name="attendant")
    Group.create(name="physiotherapist")
    Group.create(name="patient")


if __name__ == "__main__":
    do_migration()
