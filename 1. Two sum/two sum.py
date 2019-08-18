"""
Given an array of integers, return indices of the two numbers such that they add up to a specific target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.



Example:

Given nums = [2, 7, 11, 15], target = 9,

Because nums[0] + nums[1] = 2 + 7 = 9,
return [0, 1].
"""
from typing import Callable, Any, Iterable, List


class solution:
    def two_sum(self, nums: List[int], target: int) -> List[int]:
        # a container for storing the value of nums that used in the subtraction and it's index
        dict = {}

        for i in range(len(nums)):
            if target-nums[i] not in dict:
                dict[nums[i]] = i

            else:
                return [dict[target-nums[i]], i]

