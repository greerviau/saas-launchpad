import argparse
import sys

from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(".")  # Add the current directory to the Python path

from app.database.schema.users import User

# Set up password hashing (same as in auth.py)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str):
    return pwd_context.hash(password)


def create_user(
    name: str,
    email: str,
    password: str,
    database_url: str,
    timezone: str = "America/New_York",
):
    # Create database engine and session
    engine = create_engine(database_url.replace("+asyncpg", ""))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Check if user with given email already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists.")
            return

        # Create new user
        new_user = User(
            name=name,
            email=email,
            password_hash=get_password_hash(password),
            timezone=timezone,
            has_access=True,
        )

        # Add user to database and commit
        db.add(new_user)
        db.commit()
        print(f"User {name} with email {email} created successfully.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new user in the database.")
    parser.add_argument("--name", required=True, help="User's name")
    parser.add_argument("--email", required=True, help="User's email")
    parser.add_argument("--password", required=True, help="User's password")
    parser.add_argument(
        "--database_url",
        required=True,
        help="Database URL",
    )
    parser.add_argument(
        "--timezone",
        default="America/New_York",
        help="User's timezone (default: America/New_York)",
    )

    args = parser.parse_args()

    create_user(args.name, args.email, args.password, args.database_url, args.timezone)
