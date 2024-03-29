def linear_regression(x1, y1, x2, y2, t=None):
    slope = (y2 - y1) / (x2 - x1)
    intercept = y2 - (slope * x2)
    if t:
        return (slope * t) + intercept
    else:
        return slope, intercept


def extend_list_to(nums, target_len):
    if target_len < len(nums):
        print(
            f"INVALID USAGE: target_len {target_len} must not be less than len(nums) {len(nums)}"
        )
        assert False
    if target_len == len(nums):
        return nums
    elif len(nums) == 1:
        return nums * target_len
    range_formulas = []
    for i in range(len(nums) - 1):
        range_formulas.append(linear_regression(i, nums[i], i + 1, nums[i + 1]))
    extended_list = []
    step_range = len(nums) - 1
    step_size = step_range / (target_len - 1)
    relative_loc = 0
    range_idx = 0
    for i in range(target_len):
        if relative_loc > (range_idx + 1.0001):
            range_idx += 1
        extended_list.append(
            (relative_loc * range_formulas[range_idx][0]) + range_formulas[range_idx][1]
        )
        relative_loc += step_size
    return extended_list


def shrink_list_to(nums, target_len):
    if target_len > len(nums):
        print(
            f"INVALID USAGE: target_len {target_len} must not be greater than len(nums) {len(nums)}"
        )
        assert False
    shrunk_list = []
    try:
        window_size = max(round(target_len / len(nums)), 1)
    except ZeroDivisionError:
        return [0] * target_len
    for i in range(target_len):
        start = i * window_size
        end = start + window_size
        if start >= len(nums):
            return shrunk_list
        elif end >= len(nums):
            window = nums[start:]
            window_avg = sum(window) / len(window)
            shrunk_list.append(window_avg)
            break
        else:
            window = nums[start:end]
            window_avg = sum(window) / len(window)
            shrunk_list.append(window_avg)
    return shrunk_list


def adjust_list_len(nums, target_len):
    if len(nums) < target_len:
        return extend_list_to(nums, target_len)
    elif len(nums) > target_len:
        return shrink_list_to(nums, target_len)
    else:
        return nums


if __name__ == "__main__":
    l = [1, 5, 3]
    print(extend_list_to(l, 6))
