import random
import string
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import WebFramework, Experience
import django.db.utils

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with users and frameworks'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Clearing existing data...'))

        Experience.objects.all().delete()
        WebFramework.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Existing data cleared!'))

        self.stdout.write(self.style.SUCCESS('Seeding users...'))

        try:
            random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
            admin = User.objects.create_user(
                username='admin',
                email='admin@akasec.com',
                password=random_password
            )
            admin.is_admin = True
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin.username} with password: {random_password}'))
        except django.db.utils.IntegrityError:
            print("User admin already exists.")
        
        try:
            player = User.objects.create_user(
                username='guest',
                email='guest@example.com',
                password='guest'
            )
            self.stdout.write(self.style.SUCCESS(f'Created player user: {player.username}'))
        except django.db.utils.IntegrityError:
            print("User player already exists.")

        self.stdout.write(self.style.SUCCESS('Seeding WebFrameworks...'))

        frameworks = [
            {"name": "Ruby on Rails", "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Ruby_On_Rails_Logo.svg/1024px-Ruby_On_Rails_Logo.svg.png"},
            {"name": "React", "icon": "https://reactjs.org/logo-og.png"},
            {"name": "Vue.js", "icon": "https://vuejs.org/images/logo.png"},
            {"name": "Angular", "icon": "https://angular.io/assets/images/logos/angular/angular.svg"},
            {"name": "Django", "icon": "https://www.djangoproject.com/m/img/logos/django-logo-positive.png"},
            {"name": "Flask", "icon": "https://seeklogo.com/images/F/flask-logo-44C507ABB7-seeklogo.com.png"},
            {"name": "Express.js", "icon": "https://avatars.githubusercontent.com/u/5658226?s=200&v=4"},
            {"name": "Laravel", "icon": "https://laravel.com/img/logomark.min.svg"},
            {"name": "Next.js", "icon": "https://www.svgrepo.com/show/354113/nextjs-icon.svg"},
            {"name": "Svelte", "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Svelte_Logo.svg/340px-Svelte_Logo.svg.png"},
            {"name": "Spring Boot", "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Spring_Boot.svg/1024px-Spring_Boot.svg.png"},
            {"name": "ASP.NET Core", "icon": "https://dotnet.microsoft.com/favicon.ico"},
            {"name": "Symfony", "icon": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Symfony2.svg/2880px-Symfony2.svg.png"},
            {"name": "htmx", "icon": "https://www.drupal.org/files/project-images/htmx_logo.1.png"}
        ]

        for framework in frameworks:
            WebFramework.objects.create(
                name=framework["name"],
                icon=framework["icon"]
            )
            self.stdout.write(self.style.SUCCESS(f'Created framework: {framework["name"]}'))

        self.stdout.write(self.style.SUCCESS('Seeding Experiences...'))

        rails_framework = WebFramework.objects.get(name='Ruby on Rails')
        Experience.objects.create(
            owner=admin,
            web_framework=rails_framework,
            text=f"Ruby/{rails_framework.name}/🎩",
            hot=True
        )

        self.stdout.write(self.style.SUCCESS('Database seeding completed!'))
