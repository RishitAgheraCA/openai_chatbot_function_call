from django.contrib.admin import AdminSite
from django.conf import settings
from django.db.models import Model  # To check for Django model classes
from django.contrib.auth.models import User

# Local imports
import src.models

# Set up the custom admin panel
admin_site = AdminSite(name=settings.APP_NAME)

# Get a reference to the module containing all models
all_model_classes = src.models

# Loop through attributes to find models dynamically
for attribute_name in dir(all_model_classes):
    # Skip any built-in attributes or the BaseModel class
    if attribute_name.startswith("__") or attribute_name == "BaseModel":
        continue

    # Get the class reference for each attribute
    model_class = getattr(all_model_classes, attribute_name)

    # Check if the attribute is a Django model class
    if isinstance(model_class, type) and issubclass(model_class, Model):
        # If the model has the `show_in_admin` method and returns True, register it
        if hasattr(model_class, "show_in_admin") and callable(getattr(model_class, "show_in_admin")):
            if model_class.show_in_admin():
                try:
                    admin_site.register(model_class)
                except Exception as e:
                    print(f"Error registering {model_class.__name__}: {e}")

# Register the User model
try:
    admin_site.register(User)
except Exception as e:
    print(f"Error registering User model: {e}")