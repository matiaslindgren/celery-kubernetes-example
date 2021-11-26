def longest_common_substr(str_a, str_b):
    longest_str = ''
    for i in range(len(str_a)):
        for j in range(len(str_b)):
            current_str = ''
            k = 0
            while i + k < len(str_a) and j + k < len(str_b) and str_a[i + k] == str_b[j + k]:
                current_str += str_a[i + k]
                k += 1
            if k > len(longest_str):
                longest_str = current_str
    return longest_str
