import argparse
import os
from experiments import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp_dir', type=str, default="experiments")

    # Experiment parameters
    # parser.add_argument("--repetitions", default=10, type=int)
    parser.add_argument("--max_steps", default=10000, type=int)
    parser.add_argument("--eval_every", default=100, type=int)

    # Dataset Parameters
    parser.add_argument('--dataset_dir', type=str, default="Dataset")

    # parser.add_argument('--data_directory', type=str, default="reasoned_ontologies")
    # parser.add_argument('--reference_alignments_dir', type=str, default="reference_alignments_owl")
    # parser.add_argument('--instance_alignments_dir', type=str, default="produced_instance_alignments")
    # parser.add_argument('--common_instances', type=str, default="simple", help='{"simple", "extended"}')

    # Agent policies
    # parser.add_argument('--teacher_policy', type=str, default="property-based", help='{"random", "property-based"}')
    # parser.add_argument('--student_policy', type=str, default="logic-based", help='{"logic-based", "frequency-based"}')

    args = parser.parse_args()

    # check dataset path exists
    if not os.path.exists(args.dataset_dir):
        raise ValueError(f"Dataset path '{args.dataset_dir}' could not be found!")
