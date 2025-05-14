import os
import random
import requests
import tempfile
from django.core.management.base import BaseCommand
from django.core.files import File
from django.core.files.images import ImageFile
from django.conf import settings
from django.contrib.auth import get_user_model
from marketplace.models import Item

User = get_user_model()

class Command(BaseCommand):
    help = 'Populates the database with sample livestock and poultry items'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of items to create for each category'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing items before creating new ones'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']

        # Get or create a seller user
        seller, created = User.objects.get_or_create(
            username='seller',
            defaults={
                'email': 'seller@example.com',
                'is_seller': True,
            }
        )

        if created:
            seller.set_password('password123')
            seller.save()
            self.stdout.write(self.style.SUCCESS(f'Created seller user: {seller.username}'))
        else:
            self.stdout.write(f'Using existing seller user: {seller.username}')

        # Clear existing items if requested
        if clear:
            deleted_count = Item.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'Deleted {deleted_count} existing items'))

        # Sample data for livestock
        livestock_data = [
            {
                'name': 'Angus Cattle',
                'description': 'Healthy Angus cattle, known for their high-quality beef. Well-fed and raised in open pastures.',
                'price': random.uniform(25000, 35000),
                'image_url': 'https://images.unsplash.com/photo-1570042225831-d98fa7577f1e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8Y293fGVufDB8fDB8fHww&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Holstein Dairy Cow',
                'description': 'Productive Holstein dairy cow. Excellent milk production and healthy condition.',
                'price': random.uniform(30000, 40000),
                'image_url': 'https://images.unsplash.com/photo-1546445317-29f4545e9d53?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTB8fGNvd3xlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Berkshire Pig',
                'description': 'Premium Berkshire pig, known for its marbled meat and excellent flavor.',
                'price': random.uniform(8000, 12000),
                'image_url': 'https://images.unsplash.com/photo-1593179357196-705d7578c5a3?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8cGlnfGVufDB8fDB8fHww&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Merino Sheep',
                'description': 'Merino sheep with high-quality wool. Well-maintained and healthy.',
                'price': random.uniform(5000, 8000),
                'image_url': 'https://images.unsplash.com/photo-1484557985045-edf25e08da73?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8c2hlZXB8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Boer Goat',
                'description': 'Healthy Boer goat, excellent for meat production. Well-fed and disease-free.',
                'price': random.uniform(4000, 7000),
                'image_url': 'https://images.unsplash.com/photo-1560942485-b2a11cc13456?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Z29hdHxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Brahman Bull',
                'description': 'Strong and healthy Brahman bull, perfect for breeding purposes.',
                'price': random.uniform(40000, 60000),
                'image_url': 'https://images.unsplash.com/photo-1584240252425-c4f77a7e91b5?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTB8fGJ1bGx8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Suffolk Sheep',
                'description': 'Suffolk sheep known for fast growth and excellent meat quality.',
                'price': random.uniform(6000, 9000),
                'image_url': 'https://images.unsplash.com/photo-1588943211346-0908a1fb0b01?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8c2hlZXB8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Duroc Pig',
                'description': 'Duroc pig with excellent growth rate and meat quality.',
                'price': random.uniform(7000, 11000),
                'image_url': 'https://images.unsplash.com/photo-1604848698030-c434ba08ece1?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTF8fHBpZ3xlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Jersey Cow',
                'description': 'Jersey cow known for high butterfat content in milk. Gentle temperament.',
                'price': random.uniform(28000, 38000),
                'image_url': 'https://images.unsplash.com/photo-1500595046743-cd271d694d30?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Y293fGVufDB8fDB8fHww&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Alpine Goat',
                'description': 'Alpine dairy goat with good milk production. Healthy and well-maintained.',
                'price': random.uniform(3500, 6500),
                'image_url': 'https://images.unsplash.com/photo-1533318087102-b3ad366ed041?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Z29hdHxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=800&q=60'
            },
        ]

        # Sample data for poultry
        poultry_data = [
            {
                'name': 'Rhode Island Red Chickens',
                'description': 'Healthy Rhode Island Red chickens, excellent egg layers and good for meat.',
                'price': random.uniform(250, 350),
                'image_url': 'https://images.unsplash.com/photo-1548550023-2bdb3c5beed7?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2hpY2tlbnxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'White Leghorn Chickens',
                'description': 'Productive White Leghorn chickens, known for their excellent egg production.',
                'price': random.uniform(200, 300),
                'image_url': 'https://images.unsplash.com/photo-1612170153139-6f881ff067e0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Y2hpY2tlbnN8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Pekin Ducks',
                'description': 'Healthy Pekin ducks, fast-growing and excellent for meat production.',
                'price': random.uniform(300, 450),
                'image_url': 'https://images.unsplash.com/photo-1556155092-490a1ba16284?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8ZHVja3xlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Bronze Turkeys',
                'description': 'Large Bronze turkeys, perfect for special occasions. Healthy and well-fed.',
                'price': random.uniform(800, 1200),
                'image_url': 'https://images.unsplash.com/photo-1606728035253-49e8a23146de?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8dHVya2V5JTIwYmlyZHxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Embden Geese',
                'description': 'Embden geese with excellent meat quality. Large and healthy birds.',
                'price': random.uniform(600, 900),
                'image_url': 'https://images.unsplash.com/photo-1563281577-a7be47e20db9?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Z2Vuc2V8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Plymouth Rock Chickens',
                'description': 'Dual-purpose Plymouth Rock chickens, good for both eggs and meat.',
                'price': random.uniform(280, 380),
                'image_url': 'https://images.unsplash.com/photo-1569428034239-f9565e32e224?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8Y2hpY2tlbiUyMGZhcm18ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Muscovy Ducks',
                'description': 'Hardy Muscovy ducks with lean meat. Low maintenance and disease-resistant.',
                'price': random.uniform(350, 500),
                'image_url': 'https://images.unsplash.com/photo-1565098772267-60af42b81ef2?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8ZHVja3xlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Bourbon Red Turkeys',
                'description': 'Heritage Bourbon Red turkeys with excellent flavor. Free-range raised.',
                'price': random.uniform(900, 1300),
                'image_url': 'https://images.unsplash.com/photo-1574672280600-4accfa5b6f98?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8dHVya2V5JTIwYmlyZHxlbnwwfHwwfHx8MA%3D%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Toulouse Geese',
                'description': 'Large Toulouse geese, good for meat and egg production.',
                'price': random.uniform(650, 950),
                'image_url': 'https://images.unsplash.com/photo-1595613216787-a0bbcc1ae606?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8OXx8Z29vc2V8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=800&q=60'
            },
            {
                'name': 'Silkie Chickens',
                'description': 'Unique Silkie chickens with soft, fluffy feathers. Good brooders and pets.',
                'price': random.uniform(400, 600),
                'image_url': 'https://images.unsplash.com/photo-1612170153139-6f881ff067e0?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8Y2hpY2tlbnN8ZW58MHx8MHx8fDA%3D&auto=format&fit=crop&w=800&q=60'
            },
        ]

        # Helper function to download and save image
        def download_and_save_image(url, item, category, name):
            try:
                # Download the image
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    # Create a temporary file
                    img_temp = tempfile.NamedTemporaryFile(delete=True)
                    # Write the image content to the temporary file
                    for chunk in response.iter_content(1024):
                        img_temp.write(chunk)

                    # Create a clean filename from the item name
                    clean_name = name.lower().replace(' ', '_')
                    filename = f"{category}_{clean_name}.jpg"

                    # Save the image to the item
                    img_temp.flush()
                    item.image.save(filename, File(img_temp), save=True)

                    self.stdout.write(f"Downloaded image for {name}")
                    return True
                else:
                    self.stdout.write(self.style.WARNING(f"Failed to download image for {name}: HTTP {response.status_code}"))
                    return False
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error downloading image for {name}: {str(e)}"))
                return False

        # Create livestock items
        created_livestock = 0
        for i in range(min(count, len(livestock_data))):
            item_data = livestock_data[i]
            item = Item.objects.create(
                seller=seller,
                name=item_data['name'],
                description=item_data['description'],
                category='livestock',
                price=round(item_data['price'], 2),
                available=True
            )

            # Download and attach image
            if 'image_url' in item_data:
                download_and_save_image(
                    item_data['image_url'],
                    item,
                    'livestock',
                    item_data['name']
                )

            created_livestock += 1

        # Create poultry items
        created_poultry = 0
        for i in range(min(count, len(poultry_data))):
            item_data = poultry_data[i]
            item = Item.objects.create(
                seller=seller,
                name=item_data['name'],
                description=item_data['description'],
                category='poultry',
                price=round(item_data['price'], 2),
                available=True
            )

            # Download and attach image
            if 'image_url' in item_data:
                download_and_save_image(
                    item_data['image_url'],
                    item,
                    'poultry',
                    item_data['name']
                )

            created_poultry += 1

        self.stdout.write(self.style.SUCCESS(
            f'Successfully created {created_livestock} livestock items and {created_poultry} poultry items'
        ))

        # Create a buyer user for testing
        buyer, created = User.objects.get_or_create(
            username='buyer',
            defaults={
                'email': 'buyer@example.com',
                'is_buyer': True,
            }
        )

        if created:
            buyer.set_password('password123')
            buyer.save()
            self.stdout.write(self.style.SUCCESS(f'Created buyer user: {buyer.username}'))
        else:
            self.stdout.write(f'Using existing buyer user: {buyer.username}')
