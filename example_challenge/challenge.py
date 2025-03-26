import logging
from pathlib import Path

import anomed_challenge as anochal
import numpy as np
from sklearn import model_selection

logging.basicConfig(
    format="{asctime} - {levelname} - {name}.{funcName}: {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.DEBUG,
)


with np.load(Path("/docker_volume") / "iris.npz") as arrays:
    X = arrays["X"]
    y = arrays["y"]

X_train, X_other, y_train, y_other = model_selection.train_test_split(
    X, y, test_size=0.3, random_state=42
)
X_tune, X_val, y_tune, y_val = model_selection.train_test_split(
    X_other, y_other, test_size=0.5, random_state=21
)

example_challenge = anochal.SupervisedLearningMIAChallenge(
    training_data=anochal.InMemoryNumpyArrays(X=X_train, y=y_train),
    tuning_data=anochal.InMemoryNumpyArrays(X=X_tune, y=y_tune),
    validation_data=anochal.InMemoryNumpyArrays(X=X_val, y=y_val),
    anonymizer_evaluator=anochal.strict_binary_accuracy,
    MIA_evaluator=anochal.evaluate_MIA,
    MIA_evaluation_dataset_length=5,
)

# This is what GUnicorn expects
application = anochal.supervised_learning_MIA_challenge_server_factory(
    example_challenge
)
