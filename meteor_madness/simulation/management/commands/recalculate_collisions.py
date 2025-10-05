from django.core.management.base import BaseCommand
from simulation.models import Asteroid
from simulation.collision_calculator import calculate_collision_location


class Command(BaseCommand):
    help = 'Recalculate collision data for all asteroids'

    def handle(self, *args, **options):
        asteroids = Asteroid.objects.all()
        updated_count = 0
        
        for asteroid in asteroids:
            try:
                # Calculate new collision data
                collision_data = calculate_collision_location(asteroid)
                
                # Update asteroid with new collision data
                asteroid.predicted_impact_latitude = collision_data['predicted_impact_latitude']
                asteroid.predicted_impact_longitude = collision_data['predicted_impact_longitude']
                asteroid.predicted_impact_location = collision_data['predicted_impact_location']
                asteroid.impact_probability = collision_data['impact_probability']
                asteroid.impact_energy_megatons = collision_data['impact_energy_megatons']
                asteroid.crater_diameter_km = collision_data['crater_diameter_km']
                asteroid.save()
                
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Updated {asteroid.name} - Impact Probability: {asteroid.impact_probability:.1%}')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error updating {asteroid.name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} asteroids with collision data')
        )
