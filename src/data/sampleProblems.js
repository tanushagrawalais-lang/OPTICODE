export const sampleProblems = [
  {
    id: 'two-sum-bruteforce',
    title: 'Two Sum (Nested Quadratic)',
    complexity: 'O(N²)',
    targetComplexity: 'O(N)',
    category: 'Array / Hashing',
    astGateStatus: 'TRIGGER_REFACTOR',
    astReasoning: 'Exclusionary AST Gate detected depth-2 loop nesting (ast_node: ForStatement). Algorithmic refactoring required.',
    code: `def two_sum(nums: list[int], target: int) -> list[int]:
    """Find two numbers that add up to target.
    Current complexity: O(N^2) time, O(1) space.
    """
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []`,
    optimizedCode: `def two_sum(nums: list[int], target: int) -> list[int]:
    """Find two numbers that add up to target.
    Optimized via Hash Map: O(N) time, O(N) space.
    """
    seen: dict[int, int] = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []`,
    benchmarks: {
      speedup: '3.4x',
      originalTime: '124.8 ms',
      optimizedTime: '36.7 ms',
      memoryDelta: '-18.4 MB',
      astNodesReduced: 14,
      syntaxVerified: true,
      dockerPassed: true,
    },
  },
  {
    id: 'find-duplicates',
    title: 'Find Duplicates in Large Stream',
    complexity: 'O(N²)',
    targetComplexity: 'O(N)',
    category: 'Collection Lookup',
    astGateStatus: 'TRIGGER_REFACTOR',
    astReasoning: 'Exclusionary AST Gate detected linear scan containment inside loop (ast_node: InExpression inside WhileStatement).',
    code: `def find_duplicates(elements: list[str]) -> list[str]:
    """Identifies duplicate items in stream.
    Naive nested search: O(N^2)
    """
    duplicates = []
    for item in elements:
        # 'item in duplicates' causes hidden secondary O(N) scan
        if elements.count(item) > 1 and item not in duplicates:
            duplicates.append(item)
    return duplicates`,
    optimizedCode: `def find_duplicates(elements: list[str]) -> list[str]:
    """Identifies duplicate items in stream.
    Refactored using Set tracking: O(N) single pass
    """
    seen = set()
    duplicates = set()
    for item in elements:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)`,
    benchmarks: {
      speedup: '5.8x',
      originalTime: '210.5 ms',
      optimizedTime: '36.2 ms',
      memoryDelta: '-24.0 MB',
      astNodesReduced: 22,
      syntaxVerified: true,
      dockerPassed: true,
    },
  },
  {
    id: 'linear-already-optimal',
    title: 'Max Subarray Sum (Kadane)',
    complexity: 'O(N)',
    targetComplexity: 'O(N) [Optimal]',
    category: 'Dynamic Programming',
    astGateStatus: 'SHORT_CIRCUITED',
    astReasoning: 'Exclusionary AST Gate Short-Circuit: Algorithm is already optimal O(N). SLM inference bypassed to prevent hallucination & save 100% compute/tokens.',
    code: `def max_sub_array(nums: list[int]) -> int:
    """Calculates max subarray sum using Kadane's algorithm.
    Already optimal O(N) single pass.
    """
    max_current = max_global = nums[0]
    for num in nums[1:]:
        max_current = max(num, max_current + num)
        if max_current > max_global:
            max_global = max_current
    return max_global`,
    optimizedCode: `# AST Gate Report: Short-circuit triggered!
# No code modification required.
# Your function is already optimal with respect to time complexity: O(N).
# Preserving existing code structure prevents regression and token waste.`,
    benchmarks: {
      speedup: '1.0x (Optimal)',
      originalTime: '18.2 ms',
      optimizedTime: '18.2 ms',
      memoryDelta: '0 MB',
      astNodesReduced: 0,
      syntaxVerified: true,
      dockerPassed: true,
    },
  },
];
