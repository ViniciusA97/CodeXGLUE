// Bug: Modifying collection while iterating
public void removeNegatives(List<Integer> numbers) {
    for (Integer num : numbers) {
        if (num < 0) {
            numbers.remove(num);
        }
    }
}
