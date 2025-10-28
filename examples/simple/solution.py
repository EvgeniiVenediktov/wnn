import os
import sys
import numpy as np


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# Add project root folder to path for importing utils
sys.path.append(f"{CURRENT_DIR}/../..")

from utils import DataPoint, ScorerStepByStep


class PredictionModel:
    """
    Simple model that predicts the next value as a moving average
    of all previous values in the current sequence.
    """

    def __init__(self, max_len=100):
        self.current_seq_ix = None
        self.sequence_history = []
        self.max_len = max_len

    def predict(self, data_point: DataPoint) -> np.ndarray:
        if self.current_seq_ix != data_point.seq_ix:
            self.current_seq_ix = data_point.seq_ix
            self.sequence_history = []
        
        if len(self.sequence_history) == self.max_len:
            self.sequence_history.pop(0)

        self.sequence_history.append(data_point.state.copy())

        if not data_point.need_prediction:
            return None

        return np.mean(self.sequence_history, axis=0)


if __name__ == "__main__":
    # Check existence of test file
    test_file = f"{CURRENT_DIR}/../../datasets/train.parquet"

    r = []

    for i in range(10, 96, 5):
        print(i)
        # Create and test our model
        model = PredictionModel(max_len=i)

        # Load data into scorer
        scorer = ScorerStepByStep(test_file)

        print("Testing simple model with moving average...")
        print(f"Feature dimensionality: {scorer.dim}")
        print(f"Number of rows in dataset: {len(scorer.dataset)}")

        # Evaluate our solution
        results = scorer.score(model)
        
        r.append((results['mean_r2'], i))

        #print("\nResults:")
        #print(f"Mean R² across all features: {results['mean_r2']:.6f}")
        #print("\nR² for first 5 features:")
        #for i in range(min(5, len(scorer.features))):
        #    feature = scorer.features[i]
        #    print(f"  {feature}: {results[feature]:.6f}")

        #print(f"\nTotal features: {len(scorer.features)}")
    r.sort(key=lambda x: x[0], reverse=True)
    print(r[:5])
    bs, bp = r[0]

    with open('results.txt', 'w') as f:
        for s, p in r:
            f.write(f'{p}, {s}\n')



    print('Best param: ', bp)
    print('Best score: ', bs)
