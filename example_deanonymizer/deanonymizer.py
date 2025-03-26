import logging
import os
from wsgiref.simple_server import make_server

import anomed_deanonymizer
import numpy as np
from art.attacks.inference.membership_inference import MembershipInferenceBlackBox

logging.basicConfig(
    format="{asctime} - {levelname} - {name}.{funcName}: {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)


def validate_input_array(feature_array: np.ndarray) -> None:
    if feature_array.shape[1] != 4 or len(feature_array.shape) != 2:
        raise ValueError("Feature array needs to have shape (n_samples, 4).")
    if feature_array.dtype != np.float_:
        raise ValueError("Feature array must be an array of floats.")


attack_target_hostname = os.getenv("ATTACK_TARGET_HOST")
logger.debug(
    f"Obtained attack target hostname '{attack_target_hostname}' from environment."
)
attack_target = anomed_deanonymizer.WebClassifier(
    url=f"http://{attack_target_hostname}/predict", input_shape=(4,), nb_classes=3
)
example_attack_art = MembershipInferenceBlackBox(
    estimator=attack_target,  # type: ignore
    attack_model_type="rf",
)
example_attack = anomed_deanonymizer.ARTWrapper(
    art_mia=example_attack_art, input_validator=validate_input_array
)

challenge_hostname = os.getenv("CHALLENGE_HOST")
logger.debug(f"Obtained challenge hostname '{challenge_hostname}' from environment.")
application = anomed_deanonymizer.supervised_learning_MIA_server_factory(
    anonymizer_identifier="example_anonymizer",
    deanonymizer_identifier="example_deanonymizer",
    deanonymizer_obj=example_attack,
    model_filepath="deanonymizer.pkl",
    default_batch_size=64,
    member_url=f"http://{challenge_hostname}/data/deanonymizer/members",
    nonmember_url=f"http://{challenge_hostname}/data/deanonymizer/non-members",
    evaluation_data_url=f"http://{challenge_hostname}/data/attack-success-evaluation",
    model_loader=anomed_deanonymizer.unpickle_deanonymizer,
    utility_evaluation_url=f"http://{challenge_hostname}/utility/deanonymizer",
)

with make_server("", 80, application) as httpd:  # type: ignore
    httpd.serve_forever()
