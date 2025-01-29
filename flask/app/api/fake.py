import imp
from faker import Faker
from faker_enum import EnumProvider
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError

from app import db
from app.utils.app.units import Unit

def n_time_ago(**kwargs):
    return datetime.now() - timedelta(**kwargs)


def random_between(low, high):
    return random.uniform(low, high)


def rand_n_digits(n):
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return random.randint(range_start, range_end)


fake = Faker()
fake.add_provider(EnumProvider)


def role(name, description=None, is_admin=False):
    if description is None:
        description = _("Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")

    print(f"Creating role {name}")
    role = db.session.query(Role).filter_by(name=name).first()
    if role:
        print(f"Role {name} already exists")
        return role
    role = Role(name=name, description=description, is_admin=is_admin)
    db.session.add(role)
    return role


def user(name=None, email=None, username=None, roles=[]):
    if name is None:
        name = fake.name()

    if email is None:
        email = fake.email()

    user_exists = (
        db.session.query(User).filter_by(email=email).first()
        or db.session.query(User).filter(User.username == username).first()
    )
    if user_exists:
        print(f"Email {email} already exists")
        return

    print(f"Creating user {name} with email {email}")
    user = User(
        first_name=name,
        last_name=name,
        username=username,
        email=email,
        password="123123",
        email_verified_at=datetime.now(timezone.utc),
    )


    db.session.add(user)
    return user

def strain(
    name=None,
    type=None,
    environment=None,
    thc=None,
    cbd=None,
    cbg=None,
    status=Status.ACTIVE,
    expected_time_immature=None,
    expected_time_harvest=None,
    expected_time_vegetative=None,
    expected_time_flowering=None,
    period_expected_time_immature=Period.WEEKS,
    period_expected_time_harvest=Period.WEEKS,
    period_expected_time_vegetative=Period.WEEKS,
    period_expected_time_flowering=Period.WEEKS,
    **kwargs,
):
    if name is None:
        name = fake.name()
    if type is None:
        type = fake.enum(StrainType)
    if environment is None:
        environment = fake.enum(Environment)
    if thc is None:
        thc = random_between(0, 0.22)
    if cbd is None:
        cbd = random_between(0, 0.003)
    if cbg is None:
        cbg = random_between(0, 0.02)

    if expected_time_immature is None:
        expected_time_immature = fake.random_number(digits=3)
    if expected_time_harvest is None:
        expected_time_harvest = fake.random_number(digits=3)
    if expected_time_vegetative is None:
        expected_time_vegetative = fake.random_number(digits=3)
    if expected_time_flowering is None:
        expected_time_flowering = fake.random_number(digits=3)

    strain = Strain(
        name=name,
        type=fake.enum(StrainType),
        environment=fake.enum(Environment),
        thc=thc,
        cbd=cbd,
        cbg=cbg,
        status=status,
        expected_time_immature=expected_time_immature,
        period_expected_time_immature=period_expected_time_immature,
        expected_time_harvest=expected_time_harvest,
        period_expected_time_harvest=period_expected_time_harvest,
        expected_time_vegetative=expected_time_vegetative,
        period_expected_time_vegetative=period_expected_time_vegetative,
        expected_time_flowering=expected_time_flowering,
        period_expected_time_flowering=period_expected_time_flowering,
        **kwargs,
    )
    db.session.add(strain)
    return strain


def insert_locations_with_assets(locations=locations):
    """
    Inserts locations with multiple assets within their admitted radius.

    Args:
        locations: A list of dictionaries containing location data:
            address_street, address_city, country, latitude, longitude, zipcode
    """

    for location in locations:
        # Create a new Location object
        location = Location(**location)
        db.session.add(location)

        # Generate random assets within the location's radius
        for _ in range(randint(1, 5)):
            # Create an asset with details and associate it with the location
            asset = Asset(
                # Example naming scheme
                name=f"Asset_{location.address_street}.",
                asset_type=fake.enum(AssetType),
                rating=fake.enum(Stars),
                admitted_radius=randint(1, 500),
                location=location
            )

            db.session.add(asset)

        try:
            db.session.commit()
            print(f"Inserted {len(locations)
                              } locations with a number of assets")

        except Exception as e:
            db.session.rollback()
            print(f"Error happens {str(e)}")


def _seed():
    admin_role = role(name="admin", is_admin=True)
    user_tio = user(
        name="tio", email="tio@equiptrace.ai", username="tio", roles=[admin_role]
    )






def seed(tenant_name=None):
    if tenant_name is not None:
        _seed()
    else:
        _seed_root()




