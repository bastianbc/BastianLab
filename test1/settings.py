from .environment import *
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

try:
    if ENVIRONMENT == "PRODUCTION":
        from .environments.production import *
    elif ENVIRONMENT == "DEVELOPMENT":
        from .environments.development import *
    elif ENVIRONMENT == "TEST":
        from .environments.test import *
    elif ENVIRONMENT == "AWS":
        from .environments.aws import *

    print("{} settings loaded..".format(ENVIRONMENT))
except ImportError as e:
    print("{} settings could not loaded..".format(ENVIRONMENT))
    print(e)
    pass
