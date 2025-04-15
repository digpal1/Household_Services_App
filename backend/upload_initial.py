import os
from app import create_app
from household.model import db, User, Role, ProfessionalDetails, Services, Packages, Bookings
from household.sec import user_datastore
from werkzeug.security import generate_password_hash


# Create a folder to store PDF files if it doesn't already exist
ATTACH_FOLDER = os.path.join(os.path.dirname(__file__), 'pdf_files')
if not os.path.exists(ATTACH_FOLDER):
    os.makedirs(ATTACH_FOLDER)

# Path to the manually stored sample PDF file : copy a sample PDF file in the pdf_files folder
attach_pdf_name = 'sample.pdf'
attach_pdf_absolute_path = os.path.join(ATTACH_FOLDER, attach_pdf_name)
attach_pdf_path = f"/pdf_files/{attach_pdf_name}"

with create_app().app_context():
    db.create_all()
    
    # Find or create roles
    user_datastore.find_or_create_role(name='admin', description='Administrator')
    user_datastore.find_or_create_role(name='professional', description='Service Provider')
    user_datastore.find_or_create_role(name='user', description='Normal User')
    
    db.session.commit()
    # print('Roles created')

    # Query roles
    admin_role = Role.query.filter_by(name='admin').first()
    professional_role = Role.query.filter_by(name='professional').first()
    user_role = Role.query.filter_by(name='user').first()

    # Create users and assign roles
    if not user_datastore.find_user(username='admin'):
        admin_user = user_datastore.create_user(
            username='admin', 
            full_name='Admin',
            email='admin@household.com', 
            password=generate_password_hash('admin'),
            address="123 Main St, Anytown USA",
            pin_code="12345",
            roles=[admin_role]
        )

    professionals_data = [
        {
            "username": "plumber_john",
            "full_name": "John Smith",
            "email": "john@household.com",
            "service_name": "Plumbing",
            "experience": 5,
            "address": "123 Main St, Anytown USA",
            "pin_code": "12345",
            "attachment": attach_pdf_path
        },
        {
            "username": "electrician_mary",
            "full_name": "Mary Johnson",
            "email": "mary@household.com",
            "service_name": "Electrical",
            "experience": 7,
            "address": "123 Main St, Anytown USA",
            "pin_code": "12345",
            "attachment": attach_pdf_path
        },
        {
            "username": "carpenter_bob",
            "full_name": "Bob Brown",
            "email": "bob@household.com",
            "service_name": "Carpentry",
            "experience": 10,
            "address": "123 Main St, Anytown USA",
            "pin_code": "12345",
            "attachment": attach_pdf_path
        },
        {
            "username": "cleaner_susan",
            "full_name": "Susan Green",
            "email": "susan@household.com",
            "service_name": "Cleaning",
            "experience": 4,
            "address": "123 Main St, Anytown USA",
            "pin_code": "12345",
            "attachment": attach_pdf_path
        },
        {
            "username": "painter_tom",
            "full_name": "Tom White",
            "email": "tom@household.com",
            "service_name": "Painting",
            "experience": 6,
            "address": "123 Main St, Anytown USA",
            "pin_code": "12345",
            "attachment": attach_pdf_path
        },
        {
            "username": "landscaper_emma",
            "full_name": "Emma Wilson",
            "email": "emma@household.com",
            "service_name": "Landscaping",
            "experience": 8,
            "address": "123 Main St, Anytown USA",
            "pin_code": "12345",
            "attachment": attach_pdf_path
        },
        {
            "username": "hvac_james",
            "full_name": "James Taylor",
            "email": "james@household.com",
            "service_name": "HVAC",
            "experience": 12,
            "address": "123 Main St, Anytown USA",
            "pin_code": "12345",
            "attachment": attach_pdf_path
        },
        {
            "username": "pestcontrol_sara",
            "full_name": "Sara Davis",
            "email": "sara@household.com",
            "service_name": "Pest Control",
            "experience": 3,
            "address": "123 Main St, Anytown USA",
            "pin_code": "12345",
            "attachment": attach_pdf_path
        }
    ]

    # Create professional users and details in the database
    for pro in professionals_data:
        if not user_datastore.find_user(username=pro['username']):
            professional_user = user_datastore.create_user(
                username=pro['username'],
                full_name=pro['full_name'],
                email=pro['email'],
                password=generate_password_hash('password'), 
                address=pro['address'],
                pin_code=pro['pin_code'],
                roles=[professional_role]
            )
            db.session.commit()

            professional_user_id = professional_user.id

            professional_details = ProfessionalDetails(
                user_id=professional_user_id,
                service_name=pro['service_name'],
                experience=pro['experience'],
                attachment=pro['attachment']
            )
            db.session.add(professional_details)

    if not user_datastore.find_user(username='user'):
        normal_user = user_datastore.create_user(
            username='user', 
            full_name='User',
            email='user@household.com', 
            password=generate_password_hash('user'),
            address='456 User St', 
            pin_code='67890',
            roles=[user_role]
        )

        db.session.commit()
        
    db.session.commit()
    print('Users created and roles assigned')

    if Services.query.count() >0:
        print('Initial services already exist')
    else:
        # Add initial services
        services = [
            {
                "service_name": "Plumbing",
                "description": "All types of plumbing services including repairs and installations.",
                "base_price": 100
            },
            {
                "service_name": "Electrical",
                "description": "Electrical repairs, installations, and inspections.",
                "base_price": 150
            },
            {
                "service_name": "Carpentry",
                "description": "Custom woodwork, repairs, and installations.",
                "base_price": 200
            },
            {
                "service_name": "Cleaning",
                "description": "General cleaning services for homes and offices.",
                "base_price": 80
            },
            {
                "service_name": "Painting",
                "description": "Interior and exterior painting services.",
                "base_price": 250
            },
            {
                "service_name": "Landscaping",
                "description": "Design and maintenance of outdoor spaces.",
                "base_price": 300
            },
            {
                "service_name": "HVAC",
                "description": "Heating, ventilation, and air conditioning services.",
                "base_price": 400
            },
            {
                "service_name": "Pest Control",
                "description": "Control and elimination of pests and insects.",
                "base_price": 120
            }
        ]
        print('Adding initial services')
        for service in services:
            new_service = Services(
                service_name=service["service_name"],
                description=service["description"],
                base_price=service["base_price"]
            )
            db.session.add(new_service)

        db.session.commit()
        print('Initial services added')

    if Packages.query.count() >0:
        print('Initial packages already exist')
    else:
        # Add initial packages
        packages_data = [
                # Plumbing (service_id: 1)
                {
                "package_name": "Basic Plumbing",
                "description": "Includes minor repair and installations.",
                "price": 150,
                "service_id": 1,
                "user_id": 2
                },
                {
                "package_name": "Emergency Leak Repair",
                "description": "Immediate leak repair for pipes and taps.",
                "price": 250,
                "service_id": 1,
                "user_id": 2
                },
                {
                "package_name": "Pipe Fitting",
                "description": "Installation of new pipes in bathrooms or kitchens.",
                "price": 350,
                "service_id": 1,
                "user_id": 2
                },
                {
                "package_name": "Drain Cleaning",
                "description": "Professional cleaning of clogged drains.",
                "price": 200,
                "service_id": 1,
                "user_id": 2
                },
                {
                "package_name": "Water Heater Installation",
                "description": "Installation of water heaters.",
                "price": 500,
                "service_id": 1,
                "user_id": 2
                },
                {
                "package_name": "Electrical Repair",
                "description": "Fix electrical issues and minor installations.",
                "price": 200,
                "service_id": 2,
                "user_id": 3
                },
                {
                "package_name": "Light Fixture Installation",
                "description": "Install new light fixtures or repair old ones.",
                "price": 150,
                "service_id": 2,
                "user_id": 3
                },
                {
                "package_name": "Fan Installation",
                "description": "Install ceiling fans or repair old fans.",
                "price": 180,
                "service_id": 2,
                "user_id": 3
                },
                {
                "package_name": "Switchboard Repair",
                "description": "Repair faulty switchboards or replace old ones.",
                "price": 220,
                "service_id": 2,
                "user_id": 3
                },
                {
                "package_name": "Wiring Setup",
                "description": "Complete house wiring for new or renovated homes.",
                "price": 800,
                "service_id": 2,
                "user_id": 3
                },
                {
                "package_name": "Carpentry Essentials",
                "description": "Basic woodwork services.",
                "price": 250,
                "service_id": 3,
                "user_id": 4
                },
                {
                "package_name": "Furniture Assembly",
                "description": "Assembly of flat-pack furniture.",
                "price": 180,
                "service_id": 3,
                "user_id": 4
                },
                {
                "package_name": "Custom Shelving",
                "description": "Design and build custom shelves.",
                "price": 350,
                "service_id": 3,
                "user_id": 4
                },
                {
                "package_name": "Door and Window Frame Repair",
                "description": "Repair of door and window frames.",
                "price": 220,
                "service_id": 3,
                "user_id": 4
                },
                {
                "package_name": "Wooden Flooring Installation",
                "description": "Installation of wooden flooring.",
                "price": 550,
                "service_id": 3,
                "user_id": 4
                },
                {
                "package_name": "Home Cleaning",
                "description": "Complete home cleaning service.",
                "price": 100,
                "service_id": 4,
                "user_id": 5
                },
                {
                "package_name": "Deep Kitchen Cleaning",
                "description": "Thorough cleaning of kitchen surfaces and appliances.",
                "price": 150,
                "service_id": 4,
                "user_id": 5
                },
                {
                "package_name": "Bathroom Cleaning",
                "description": "Deep cleaning of bathrooms and toilets.",
                "price": 120,
                "service_id": 4,
                "user_id": 5
                },
                {
                "package_name": "Window Cleaning",
                "description": "Cleaning of all windows inside and outside.",
                "price": 80,
                "service_id": 4,
                "user_id": 5
                },
                {
                "package_name": "Carpet Cleaning",
                "description": "Professional carpet cleaning and stain removal.",
                "price": 200,
                "service_id": 4,
                "user_id": 5
                },
                {
                "package_name": "Interior Painting",
                "description": "Painting of interior spaces.",
                "price": 300,
                "service_id": 5,
                "user_id": 6
                },
                {
                "package_name": "Exterior Painting",
                "description": "Painting of exterior walls and surfaces.",
                "price": 450,
                "service_id": 5,
                "user_id": 6
                },
                {
                "package_name": "Room Painting",
                "description": "Complete painting for a single room.",
                "price": 250,
                "service_id": 5,
                "user_id": 6
                },
                {
                "package_name": "Wall Texturing",
                "description": "Add texture to interior walls for a stylish look.",
                "price": 400,
                "service_id": 5,
                "user_id": 6
                },
                {
                "package_name": "Ceiling Painting",
                "description": "Painting of ceilings.",
                "price": 200,
                "service_id": 5,
                "user_id": 6
                }
        ]

        # Create packages in the database
        for package in packages_data:
            new_package = Packages(
                package_name=package['package_name'],
                description=package['description'],
                price=package['price'],
                service_id=package['service_id'],
                user_id=package['user_id']
            )
            db.session.add(new_package)
        db.session.commit()


