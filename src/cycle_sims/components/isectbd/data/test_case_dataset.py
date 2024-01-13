from ..harness import flexible_intersect_compressed_fibers as hr_
import torch
from torch.utils.data import Dataset, DataLoader

class TestCaseDataset(Dataset):
    def __init__(self, sparsity0_range, sparsity1_range, fiber_length_values, vector_length_values, batch_size, num_tests, isect_fxn):
        self.sparsity0_range = sparsity0_range
        self.sparsity1_range = sparsity1_range
        self.fiber_length_values = fiber_length_values
        self.vector_length_values = vector_length_values
        self.batch_size = batch_size
        self.num_tests = num_tests
        self.isect_fxn = isect_fxn

    def __len__(self):
        # Return a very large number as the dataset is virtually infinite
        return int(1e12)

    def __getitem__(self, idx):
        # Generate batch_size number of test cases
        test_cases = hr_.generate_random_test_cases(
            self.sparsity0_range, self.sparsity1_range,
            self.fiber_length_values, self.vector_length_values,
            self.batch_size
        )
        converted_test_cases = hr_.convert_sparsity_to_compressed_length(test_cases)

        # Run the test cases and get results
        test_results = hr_.run_multiple_test_cases(converted_test_cases, self.num_tests, self.isect_fxn)

        # Convert test cases and results to tensors
        test_cases_tensor = torch.tensor([[case['compressedFiberLength0'], case['compressedFiberLength1'],
                                           case['fiberLength'], case['vectorLength']] for case in converted_test_cases])
        results_tensor = torch.tensor([[result['average_total_cycles'], result['average_num_intersections'],
                                        result['average_cycles_per_intersection'], result['average_result_length'],
                                        result['average_num_full_length_intersections']] for result in test_results])

        return test_cases_tensor, results_tensor

# Dataloader metadata
input_features = ['compressedFiberLength0', 'compressedFiberLength1', 'fiberLength', 'vectorLength']
target_features = ['average_total_cycles', 'average_num_intersections','average_cycles_per_intersection', 'average_result_length','average_num_full_length_intersections']

def test_case_dataloader_from_params(sparsity0_range, \
                                     sparsity1_range, \
                                     fiber_length_values, \
                                     vector_length_values, \
                                     batch_size, \
                                     num_tests, \
                                     direct_mapped_intersection_unit):
    
    dataset = TestCaseDataset(sparsity0_range, sparsity1_range, fiber_length_values, vector_length_values, batch_size, num_tests, direct_mapped_intersection_unit)
    return DataLoader(dataset, batch_size=1, shuffle=False)

