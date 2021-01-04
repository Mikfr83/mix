from mix.ui import *

# the init will check what application we're in
# we then will use that below to see which model we should be using
if MAYA:
    import psd_model_maya as psd_model_maya
    import weights_model_maya as weights_model_maya
    PSD_MODEL = psd_model_maya
    WEIGHTS_MODEL = weights_model_maya
else:
    import psd_model as psd_model
    import weights_model as weights_model
    PSD_MODEL = psd_model
    WEIGHTS_MODEL = weights_model