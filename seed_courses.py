from app import app, db
from models import Course

with app.app_context():
    # Sample Courses
    courses = [
        Course(
            title="Python for Beginners",
            description="Learn Python from scratch with hands-on projects.",
            category="Programming",
            price=499,
            rating=4.7
        ),
        Course(
            title="Data Science Masterclass",
            description="Data analysis, visualization, and machine learning using Python.",
            category="Data Science",
            price=999,
            rating=4.9
        ),
        Course(
            title="Business Analytics with Excel",
            description="Master Excel and analytics techniques for business decision-making.",
            category="Business",
            price=799,
            rating=4.6
        ),
        Course(
            title="UI/UX Design Bootcamp",
            description="Learn design principles, wireframing, and Figma prototyping.",
            category="Design",
            price=599,
            rating=4.8
        ),
    ]

    # Insert into DB
    db.session.bulk_save_objects(courses)
    db.session.commit()
    print("✅ Sample courses added successfully!")
