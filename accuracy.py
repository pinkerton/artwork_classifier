from keras.models import load_model

model_name = 'keras_artwork_classifier_trained_model.h5'

model = load_model("saved_models/{}".format(model_name))
model.summary()
config = model.get_config()
print(config)
