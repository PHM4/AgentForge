def binary_search(arr, target):
    """
    Performs binary search on a sorted array to find the target value.
    
    Args:
        arr: A sorted list of comparable elements
        target: The value to search for
        
    Returns:
        int: The index of the target if found, -1 otherwise
    """
    left = 0
    right = len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1


def binary_search_recursive(arr, target, left=0, right=None):
    """
    Recursive implementation of binary search.
    
    Args:
        arr: A sorted list of comparable elements
        target: The value to search for
        left: Left boundary (default: 0)
        right: Right boundary (default: len(arr) - 1)
        
    Returns:
        int: The index of the target if found, -1 otherwise
    """
    if right is None:
        right = len(arr) - 1
    
    if left > right:
        return -1
    
    mid = (left + right) // 2
    
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)


# Test cases
if __name__ == "__main__":
    test_array = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    
    # Test cases
    print(f"Array: {test_array}")
    print(f"Search for 7: {binary_search(test_array, 7)}")
    print(f"Search for 1: {binary_search(test_array, 1)}")
    print(f"Search for 19: {binary_search(test_array, 19)}")
    print(f"Search for 8: {binary_search(test_array, 8)}")
    print(f"Search for 0: {binary_search(test_array, 0)}")
    print(f"Search for 20: {binary_search(test_array, 20)}")
    
    # Test empty array
    print(f"Empty array search: {binary_search([], 5)}")
    
    # Test single element
    print(f"Single element found: {binary_search([5], 5)}")
    print(f"Single element not found: {binary_search([5], 3)}")