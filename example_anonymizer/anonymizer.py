import logging
import os
from pathlib import Path

import anomed_anonymizer as anon
import numpy as np
from diffprivlib.models import GaussianNB

logging.basicConfig(
    format="{asctime} - {levelname} - {name}.{funcName}: {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)

lower_bounds = 4 * [0.0]
upper_bounds = [10.0, 5.0, 10.0, 5.0]
estimator = GaussianNB(
    bounds=(lower_bounds, upper_bounds),
    priors=3 * [1.0 / 3.0],
)


def input_array_validator(feature_array: np.ndarray) -> None:
    if feature_array.shape[1] != 4 or len(feature_array.shape) != 2:
        raise ValueError("Feature array needs to have shape (n_samples, 4).")
    if feature_array.dtype != np.float_:
        raise ValueError("Feature array must be an array of floats.")


example_anon = anon.WrappedAnonymizer(
    anonymizer=estimator,
    serializer=anon.pickle_anonymizer,
    feature_array_validator=input_array_validator,
)

hostname = os.getenv("CHALLENGE_HOST")
logger.info(f"Obtained challenge hostname '{hostname}' from environment.")

# This is what GUnicorn expects
application = anon.supervised_learning_anonymizer_server_factory(
    anonymizer_identifier="example_anonymizer",
    anonymizer_obj=example_anon,
    model_filepath=Path("/persistent_data") / "anonymizer.pkl",
    default_batch_size=64,
    training_data_url=f"http://{hostname}/data/anonymizer/training",
    tuning_data_url=f"http://{hostname}/data/anonymizer/tuning",
    validation_data_url=f"http://{hostname}/data/anonymizer/training",
    utility_evaluation_url=f"http://{hostname}/utility/anonymizer",
    model_loader=anon.unpickle_anonymizer,
)
