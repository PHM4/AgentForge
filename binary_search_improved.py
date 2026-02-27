"""
Improved Binary Search Implementation with Input Validation and Type Hints
"""
from typing import List, Union, Optional

def binary_search(
    arr: List[Union[int, float, str]], 
    target: Union[int, float, str],
    validate_sorted: bool = False
) -> int:
    """
    Performs binary search on a sorted array.
    
    Args:
        arr: A sorted list of comparable elements
        target: The value to search for
        validate_sorted: Whether to validate array is sorted (default: False)
        
    Returns:
        int: The index of target if found, -1 otherwise
        
    Raises:
        ValueError: If arr is None or not sorted (when validate_sorted=True)
        TypeError: If arr is not a list/tuple or elements not comparable
        
    Time Complexity: O(log n)
    Space Complexity: O(1)
    
    Example:
        >>> binary_search([1, 3, 5, 7, 9], 5)
        2
        >>> binary_search([1, 3, 5, 7, 9], 4)
        -1
    """
    # Input validation
    if arr is None:
        raise ValueError("Array cannot be None")
    if not isinstance(arr, (list, tuple)):
        raise TypeError("Array must be a list or tuple")
    if not arr:
        return -1
    
    # Optional sorted validation (expensive for large arrays)
    if validate_sorted and len(arr) > 1:
        if not all(arr[i] <= arr[i+1] for i in range(len(arr)-1)):
            raise ValueError("Array must be sorted")
    
    left = 0
    right = len(arr) - 1
    
    while left <= right:
        # Prevent potential integer overflow (best practice)
        mid = left + (right - left) // 2
        
        try:
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                left = mid + 1
            else:
                right = mid - 1
        except TypeError as e:
            raise TypeError(f"Elements must be comparable: {e}")
    
    return -1


def binary_search_first(
    arr: List[Union[int, float, str]], 
    target: Union[int, float, str]
) -> int:
    """
    Find the first occurrence of target in a sorted array with duplicates.
    
    Args:
        arr: A sorted list that may contain duplicates
        target: The value to search for
        
    Returns:
        int: The index of the first occurrence, -1 if not found
    """
    if not arr:
        return -1
        
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            result = mid
            right = mid - 1  # Continue searching left
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return result


def binary_search_last(
    arr: List[Union[int, float, str]], 
    target: Union[int, float, str]
) -> int:
    """
    Find the last occurrence of target in a sorted array with duplicates.
    
    Args:
        arr: A sorted list that may contain duplicates
        target: The value to search for
        
    Returns:
        int: The index of the last occurrence, -1 if not found
    """
    if not arr:
        return -1
        
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = left + (right - left) // 2
        
        if arr[mid] == target:
            result = mid
            left = mid + 1  # Continue searching right
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return result


# Comprehensive test suite
def test_binary_search():
    """Comprehensive test suite for binary search implementations."""
    print("=== Testing Binary Search Implementations ===")
    
    # Test cases
    test_cases = [
        ([1, 3, 5, 7, 9, 11, 13], 7, 3),
        ([1, 3, 5, 7, 9, 11, 13], 1, 0),
        ([1, 3, 5, 7, 9, 11, 13], 13, 6),
        ([1, 3, 5, 7, 9, 11, 13], 4, -1),
        ([1, 3, 5, 7, 9, 11, 13], 0, -1),
        ([1, 3, 5, 7, 9, 11, 13], 15, -1),
        ([5], 5, 0),
        ([5], 3, -1),
        ([], 5, -1),
    ]
    
    print("Standard Binary Search:")
    for arr, target, expected in test_cases:
        result = binary_search(arr, target)
        status = "✅" if result == expected else "❌"
        print(f"{status} Search {target} in {arr}: got {result}, expected {expected}")
    
    # Test with duplicates
    print("\nTesting with Duplicates:")
    dup_arr = [1, 2, 2, 2, 3, 4, 5]
    print(f"Array: {dup_arr}")
    print(f"binary_search(2): {binary_search(dup_arr, 2)}")
    print(f"binary_search_first(2): {binary_search_first(dup_arr, 2)}")
    print(f"binary_search_last(2): {binary_search_last(dup_arr, 2)}")
    
    # Test error handling
    print("\nTesting Error Handling:")
    try:
        binary_search(None, 5)
    except ValueError as e:
        print(f"✅ Null array handled: {e}")
    
    try:
        binary_search("not a list", 5)
    except TypeError as e:
        print(f"✅ Invalid type handled: {e}")
    
    try:
        binary_search([3, 1, 2], 2, validate_sorted=True)
    except ValueError as e:
        print(f"✅ Unsorted array detected: {e}")
    
    # Performance test
    print("\nPerformance Test:")
    import time
    large_arr = list(range(0, 1000000, 2))
    start = time.time()
    result = binary_search(large_arr, 500000)
    end = time.time()
    print(f"Large array (500K elements) search: {result}, Time: {end - start:.6f}s")


if __name__ == "__main__":
    test_binary_search()